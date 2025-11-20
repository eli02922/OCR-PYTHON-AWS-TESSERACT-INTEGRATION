import os
import pytesseract
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings
from pdfminer.high_level import extract_text as pdf_extract_text
from PIL import Image
import fitz
# import boto3  #Uncomment this when enabling S3 upload

from .models import OCRDocument


def upload_page(request):
    """
    Handles PDF uploads and OCR extraction.

    Workflow:
      1. Validates that the file is a PDF.
      2. Extracts text using pdfminer (if selectable text exists).
      3. Falls back to image-based OCR using PyMuPDF + pytesseract if needed.
      4. Saves the result into the SQLite database.
      5. (Optional) Uploads the PDF to S3.
      6. Prepares the pipeline for AWS Textract integration.
    """
    extracted_text = None
    file_name = None
    error = None
    s3_file_url = None  #placeholder for S3 integration (future use)

    if request.method == "POST" and "file" in request.FILES:
        uploaded_file = request.FILES["file"]
        file_name = uploaded_file.name

        # --- Step 1: Validate file type ---
        if not file_name.lower().endswith(".pdf"):
            error = "Only PDF files are allowed. Please upload a valid PDF document."
        else:
            # Save uploaded PDF locally (MEDIA_ROOT/uploads/)
            saved_path = default_storage.save(f"uploads/{file_name}", uploaded_file)
            full_path = os.path.join(settings.MEDIA_ROOT, saved_path)

            try:
                #
                #
                # Uncomment this block to enable S3 upload
                #
                # s3 = boto3.client(
                #     "s3",
                #     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                #     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                #     region_name=settings.AWS_S3_REGION_NAME,
                # )
                #
                # bucket_name = settings.AWS_STORAGE_BUCKET_NAME
                # s3_key = f"uploads/{file_name}"
                #
                # # Upload the local file to your S3 bucket
                # s3.upload_file(full_path, bucket_name, s3_key)
                #
                # # Optionally get the S3 public URL (if bucket allows public access)
                # s3_file_url = f"https://{bucket_name}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"

                # --- Step 2: Try extracting selectable text first ---
                try:
                    selectable_text = pdf_extract_text(full_path).strip()
                except Exception:
                    selectable_text = ""

                if selectable_text:
                    extracted_text = f"{selectable_text}"
                    ocr_source = "pdfminer"
                else:
                    # --- Step 3: OCR fallback using PyMuPDF + pytesseract ---
                    doc = fitz.open(full_path)
                    ocr_results = []

                    for page_number in range(len(doc)):
                        page = doc.load_page(page_number)
                        zoom = 2  # increases resolution for better OCR accuracy
                        mat = fitz.Matrix(zoom, zoom)
                        pix = page.get_pixmap(matrix=mat, alpha=False)

                        # Convert PyMuPDF pixmap to a PIL Image
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                        # OCR using pytesseract
                        text = pytesseract.image_to_string(img)
                        ocr_results.append(f"\n--- Page {page_number+1} ---\n{text}\n")

                    extracted_text = "\n\n" + "".join(ocr_results)
                    ocr_source = "pytesseract"
                    doc.close()

                                # --- Step 4: Save OCR result into SQLite database ---
                OCRDocument.objects.create(
                    file_name=file_name,
                    extracted_text=extracted_text,
                    ocr_source=ocr_source
                )

                # ------------------------------------------------------------------
                # Step 6 (Future): LLM Prompt Initialization for Claude / OpenAI
                # ------------------------------------------------------------------
                #
                # Example using Claude (Anthropic):
                #
                # from anthropic import Anthropic
                #
                # client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                #
                # prompt = f"""
                # You are an assistant that analyzes PDF content.
                #
                # Extracted PDF content:
                # ----------------------
                # {extracted_text}
                #
                # Task:
                # Summarize the key points and identify any important details.
                # """
                #
                # response = client.messages.create(
                #     model="claude-3-sonnet-20240229",
                #     max_tokens=500,
                #     messages=[{"role": "user", "content": prompt}]
                # )
                #
                # llm_output = response.content[0].text
                #
                # You may store `llm_output` into database or display it on UI.
                #
                # ------------------------------------------------------------------


                # --- Step 5 (Optional): Prepare for AWS Textract integration ---
                # In future, you can replace or complement pytesseract with AWS Textract:
                #
                # from .aws_ocr import extract_text_from_aws_textract
                # aws_text = extract_text_from_aws_textract(full_path)
                # if aws_text:
                #     extracted_text = aws_text
                #     ocr_source = "aws_textract"

            except Exception as e:
                error = f"An error occurred while processing the PDF: {e}"

    # Render output on page
    return render(request, "ocr_app/upload.html", {
        "extracted_text": extracted_text,
        "file_name": file_name,
        "error": error,
        "s3_file_url": s3_file_url,  #still included for future use
    })
