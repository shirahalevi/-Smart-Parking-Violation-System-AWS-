import json
import boto3
import base64
import os
import uuid
from datetime import datetime

s3 = boto3.client('s3')
S3_BUCKET = "mobileye-parking-violation"

def lambda_handler(event, context):
    try:
        # שלב 1: קלט מה-API
        data = json.loads(event['body'])
        file_data = data.get("file_data")
        file_name = data.get("file_name", f"{uuid.uuid4()}.jpg")  # שם קובץ ייחודי אם לא נשלח

        if not file_data:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing file_data"})
            }

        # שלב 2: חילוץ נתוני base64
        if "," in file_data:
            file_data = file_data.split(",")[1]  # הסרת ה-header (data:image/jpeg;base64,...)
        decoded_file = base64.b64decode(file_data)

        # שלב 3: יצירת שם ייחודי לתמונה
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        s3_key = f"uploads/{timestamp}_{file_name}"

        # שלב 4: העלאה ל-S3
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=decoded_file,
            ContentType="image/jpeg",  # ניתן לשפר ע"י זיהוי דינמי
        )

        # שלב 5: יצירת כתובת URL ציבורית
        image_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{s3_key}"

        return {
            "statusCode": 200,
            "body": json.dumps({"image_url": image_url})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

