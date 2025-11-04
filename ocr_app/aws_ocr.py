import boto3

def extract_text_from_aws_textract(s3_file_url):
    textract = boto3.client("textract")
    bucket_name = s3_file_url.split("/")[3]
    key = "/".join(s3_file_url.split("/")[4:])

    response = textract.detect_document_text(
        Document={"S3Object": {"Bucket": bucket_name, "Name": key}}
    )

    text_blocks = [
        item["Text"] for item in response["Blocks"] if item["BlockType"] == "LINE"
    ]
    return "\n".join(text_blocks)
