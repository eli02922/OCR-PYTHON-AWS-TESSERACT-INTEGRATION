Description

This project is a Django-based Optical Character Recognition (OCR) application that allows users to upload PDF documents and automatically extract text from them.

It uses:

pdfminer for extracting selectable text,

PyMuPDF (fitz) + pytesseract for image-based OCR (no Poppler required),

SQLite for storing OCR results, and

a prepared structure for AWS Textract integration for scalable cloud OCR.

System Architecture
                ┌────────────────────────────┐
                │        Web Browser          │
                │ (Upload PDF via HTML Form)  │
                └────────────┬───────────────┘
                               │ POST /upload
                               ▼
                 ┌─────────────────────────────┐
                 │         Django App           │
                 │   (views.py / ocr_app)      │
                 └────────────┬────────────────┘
                      │
                      │ Handles upload
                      ▼
      ┌────────────────────────────────────────┐
      │ File saved to /media/uploads            │
      │ OCR logic selects one of two paths:     │
      │   1️⃣ pdfminer (extract text directly)   │
      │   2️⃣ PyMuPDF + pytesseract (OCR)       │
      └────────────────────────────────────────┘
                      │
                      ▼
         ┌──────────────────────────┐
         │ SQLite Database (ORM)    │
         │ Table: OCRDocument       │
         │ - file_name              │
         │ - extracted_text         │
         │ - ocr_source             │
         │ - created_at             │
         └──────────────────────────┘
                      │
                      ▼
       ┌────────────────────────────┐
       │ Future Integration (AWS)   │
       │ - AWS Textract             │
       │ - S3 for file storage      │
       └────────────────────────────┘

Tech Stack
Layer	Technology
Backend	Django 5.x
OCR Engine	pytesseract, PyMuPDF (fitz), pdfminer
Database	SQLite (default)
Frontend	Django Template (HTML5, Bootstrap)
Future Integration	AWS Textract, AWS S3
Installation & Setup
1. Clone the Repository
git clone https://github.com/eli02922/OCR-PYTHON-AWS-TESSERACT-INTEGRATION.git
cd OCR-PYTHON-AWS-TESSERACT-INTEGRATION

2. Install Dependencies
pip install -r requirements.txt

3. Apply Migrations
python manage.py makemigrations
python manage.py migrate

4. Run Development Server
python manage.py runserver


Then open your browser:

http://127.0.0.1:8000/