# Privacy Policy Simplifier

Privacy Policy Simplifier is an AI-powered web application built with Flask that helps users easily understand complex privacy policies. It leverages Natural Language Processing (NLP) to summarize lengthy documents and provides an interactive question-answering system to address specific concerns.

## Features

- **Text Summarization**: Upload a PDF or paste the raw text of a privacy policy, and the application will generate a concise, simplified summary using the `facebook/bart-large-cnn` model.
- **Question Answering**: Ask specific questions about the privacy policy, and the application will find the relevant answers within the text using the `distilbert-base-uncased-distilled-squad` model.
- **File Support**: Supports direct PDF file uploads for easy processing of official documents.

## Technologies Used

- **Backend Framework**: Flask (Python)
- **Natural Language Processing**: Hugging Face `transformers` library
- **PDF Processing**: `PyMuPDF` (fitz)
- **Models**:
  - Summarization: `facebook/bart-large-cnn`
  - Question Answering: `distilbert-base-uncased-distilled-squad`

## Prerequisites

Before running the application, make sure you have Python installed on your system. 

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/jenilia2786/Privacy-Policy-Simplifier.git
   cd Privacy-Policy-Simplifier
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install flask transformers PyMuPDF torch
   ```
   *(Note: PyTorch (`torch`) is required by the `transformers` library.)*

## Usage

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to `http://127.0.0.1:5000`.

3. Use the interface to either upload a PDF or paste raw text. You can then click to simplify the text or ask specific questions related to the document.

## License

This project is open-source and available for educational and non-commercial use.
