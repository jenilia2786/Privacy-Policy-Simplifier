import os
import fitz  # PyMuPDF
from flask import Flask, request, render_template
from transformers import pipeline

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

def extract_text_from_pdf(path):
    text = ""
    with fitz.open(path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def simplify_text(text):
    chunks = [text[i:i+1024] for i in range(0, len(text), 1024)]
    return "\n".join([summarizer(chunk, max_length=100, min_length=30, do_sample=False)[0]['summary_text'] for chunk in chunks])

def answer_question(question, context):
    return qa_pipeline({'question': question, 'context': context})['answer']

@app.route("/", methods=["GET", "POST"])
def index():
    original_text = simplified = answer = ""
    if request.method == "POST":
        if 'pdf' in request.files:
            file = request.files['pdf']
            if file and file.filename.endswith('.pdf'):
                path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(path)
                original_text = extract_text_from_pdf(path)
                os.remove(path)
        elif 'raw_text' in request.form:
            original_text = request.form['raw_text']

        if 'simplify' in request.form:
            simplified = simplify_text(original_text)

        if 'question' in request.form and original_text:
            question = request.form['question']
            answer = answer_question(question, original_text)

    return render_template("index.html", original_text=original_text, simplified=simplified, answer=answer)

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
