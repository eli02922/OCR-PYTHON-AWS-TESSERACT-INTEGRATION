import boto3

def extract_text_from_aws_textract(file_path):
    """
    Uses AWS Textract to extract text from a PDF or image file.
    Returns the detected text as a string.
    """
    textract = boto3.client("textract", region_name="ap-southeast-1")

    with open(file_path, "rb") as document:
        response = textract.analyze_document(
            Document={"Bytes": document.read()},
            FeatureTypes=["TABLES", "FORMS"]
        )

    extracted_text = ""
    for block in response.get("Blocks", []):
        if block["BlockType"] == "LINE":
            extracted_text += block["Text"] + "\n"

    return extracted_text.strip()
