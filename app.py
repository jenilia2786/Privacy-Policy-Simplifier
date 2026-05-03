import os
import fitz  # PyMuPDF
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from transformers import pipeline

app = Flask(__name__)
app.config['SECRET_KEY'] = 'policylens-secret-key-2026'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///policylens.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# --- Database Model ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ML Models ---
print("Loading NLP models. This might take a moment...")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")
print("Models loaded successfully.")

# --- Helper Functions ---
def extract_text_from_pdf(path):
    text = ""
    with fitz.open(path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def simplify_text(text):
    # Split text into chunks to avoid exceeding model token limits.
    # Grouping by roughly 400 words (safely under 1024 tokens).
    words = text.split()
    chunk_size = 400 
    chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    
    summaries = []
    for chunk in chunks:
        if len(chunk.split()) > 30:
            summary = summarizer(chunk, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
            summaries.append(summary)
        else:
            summaries.append(chunk)
    return "\n\n".join(summaries)

def answer_question(question, context):
    try:
        result = qa_pipeline({'question': question, 'context': context})
        return result['answer']
    except Exception as e:
        return f"Error extracting answer: {str(e)}"

# --- Routes ---

@app.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists. Please log in.', 'danger')
            return redirect(url_for('login'))
            
        new_user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your username and password.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    original_text = ""
    simplified = ""
    answer = ""
    question_asked = ""
    
    if request.method == "POST":
        action = request.form.get('action')
        
        if action == 'upload':
            if 'pdf' in request.files:
                file = request.files['pdf']
                if file and file.filename.endswith('.pdf'):
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    file.save(path)
                    original_text = extract_text_from_pdf(path)
                    os.remove(path)
                else:
                    flash('Invalid file. Please upload a PDF.', 'danger')
                    
        elif action == 'simplify':
            original_text = request.form.get('raw_text', '')
            if original_text.strip():
                simplified = simplify_text(original_text)
            else:
                flash('Please provide text to simplify.', 'warning')
                
        elif action == 'ask':
            original_text = request.form.get('raw_text', '')
            question_asked = request.form.get('question', '')
            if original_text.strip() and question_asked.strip():
                answer = answer_question(question_asked, original_text)
            else:
                flash('Please provide both text and a question.', 'warning')

    return render_template("dashboard.html", 
                           original_text=original_text, 
                           simplified=simplified, 
                           answer=answer,
                           question=question_asked)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
