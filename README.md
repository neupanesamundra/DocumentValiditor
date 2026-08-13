Document Validator Pro

An Intelligent System for Document Evaluation and Improvement

Document Validator Pro is a web-based application that automatically evaluates the quality of academic and professional documents and generates an improved version using a hybrid rule-based + machine learning pipeline combined with AI-powered rewriting.

Unlike tools such as Grammarly (grammar-only) or Turnitin (plagiarism-only), Document Validator Pro evaluates structure, readability, section completeness, and domain-specific quality criteria in a single workflow — then rewrites weak sections and hands back a downloadable, improved document with a full change log.

Features
📄 Accepts PDF, DOCX, and TXT uploads
🏷️ Automatically classifies document type — Resume, CV, Cover Letter, Report, Proposal
📊 Scores document quality across 7 dimensions:
Section coverage
Word count
Grammar
Readability
Keyword relevance
Requirement section compliance
ML-predicted score
🤖 Hybrid rule-based + ML classification and scoring, with automatic fallback if ML models are unavailable
✍️ AI-powered content rewriting via Google Gemini 2.5-flash
📝 Detailed Document Changes Summary with a tracked change log
⬇️ Exports improved documents in DOCX and PDF
⚙️ Custom requirement notes/files supported for tailored evaluation
Tech Stack
Layer	Technology
Backend	Python, Flask
Document Parsing	pdfplumber, python-docx
Machine Learning	scikit-learn (TF-IDF + Logistic Regression)
Grammar Checking	LanguageTool (local server, with heuristic fallback)
Readability	textstat (Flesch Reading Ease)
AI Rewriting	Google Gemini 2.5-flash API
Document Export	python-docx, ReportLab
Frontend	HTML, CSS, Jinja2, Bootstrap
How It Works
Upload → Validate → Extract Text → Classify Type → Score (7 dimensions)
       → Generate Suggestions → (optional) AI Improve → Export DOCX/PDF
       → Download + View Changes
Parser extracts text and detects sections from PDF/DOCX/TXT files.
Classifier determines document type using ML first, falling back to keyword-based rules if the model is unavailable.
Scoring Engine computes a composite 0–100 quality score across 7 dimensions.
Improver rewrites weak sections using the Gemini API (or rule-based fixes as a fallback) and rescoring the result.
Exporter generates the improved document in DOCX and PDF formats.
Change Tracker logs every modification for full transparency.
Project Architecture

The system follows a modular, layered architecture:

Presentation Layer — HTML/CSS/JS via Jinja2 templates
Application Layer — independent core modules (Parser, Classifier, Scoring Engine, Requirement Engine, Improver, Exporter, Change Tracker)
Data Layer — file-system based storage for uploads and generated outputs

Reliability is built around a Plan-Play architecture: rule-based processing is always available as a dependable baseline ("Plan"), while ML and AI components enhance results when available ("Play") — the system remains fully functional even if the ML models or Gemini API are unreachable.

Installation
bash
# Clone the repository
git clone https://github.com/<your-username>/document-validator-pro.git
cd document-validator-pro

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
Environment Variables

Create a .env file in the project root:

AI_ENABLED=true
AI_PROVIDER=gemini
AI_MODEL=gemini-2.5-flash
GEMINI_API_KEY=your_api_key_here
Run the App
bash
python app.py

Visit http://127.0.0.1:5000 in your browser.

Note: Grammar checking requires a local LanguageTool server. If unavailable, the system automatically falls back to heuristic grammar checking.

Usage
Upload a document (PDF, DOCX, or TXT).
Select the document type or leave it on Auto Detect.
(Optional) Add requirement notes or upload a requirements file.
Click Validate Document to see your quality score, breakdown, and suggestions.
Enable Generate Improved Document to get an AI-enhanced rewrite with a full change log.
Download the improved DOCX or PDF.
Testing

The project includes both unit and system-level test cases covering:

Text extraction accuracy across all supported formats
Document type classification
Multi-dimension scoring correctness
AI-assisted improvement and layout preservation
End-to-end upload → analyze → improve → download workflow
Limitations
Currently supports English-language documents only
Grammar-checking accuracy depends on the local LanguageTool configuration
ML models are trained on a limited dataset and may not generalize to every document domain
Single-user local web application (no cloud deployment or user accounts yet)
Complex PDF layouts may not be preserved exactly during export
Future Improvements
Support for additional document types (Essay, Thesis, General Document)
Retraining ML models on a larger, more diverse dataset
Multilingual support (including Nepali)
Cloud deployment with user accounts and persistent history
Authors
Ashlesha Thapa — Roll No. 79020112
Sakshi Sapkota — Roll No. 79020132
Samundra Prasad Neupane — Roll No. 79020133

Developed as a Bachelor in Information Technology (BIT) project at Amrit Campus, Tribhuvan University, under the supervision of Asst. Prof. Dabbal Singh Mahara.

License

This project was developed for academic purposes as part of the BIT curriculum at Tribhuvan University.
