from django.db import models

class OCRDocument(models.Model):
    """Stores uploaded PDF details and extracted text."""
    file_name = models.CharField(max_length=255)
    extracted_text = models.TextField(blank=True, null=True)
    ocr_source = models.CharField(max_length=50, default="local")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_name} ({self.ocr_source})"
