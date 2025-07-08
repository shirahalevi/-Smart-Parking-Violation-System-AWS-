import boto3
import json
from datetime import datetime, timezone

s3 = boto3.client("s3")

BUCKET = "mobileye-parking-violation"
PREFIX = "violations/"  # שונה מ־daily_violations

def lambda_handler(event, context):
    # מחשב את התאריך של היום לפי שעון ישראל
    now_israel = datetime.now(timezone.utc).astimezone()
    today_str = now_israel.strftime("%Y-%m-%d")
    print(f"📆 מחפש קבצים עם התאריך: {today_str} בשם")

    # מקבל את רשימת כל הקבצים בתיקייה
    response = s3.list_objects_v2(Bucket=BUCKET, Prefix=PREFIX)
    if "Contents" not in response:
        print("📭 אין קבצים בתיקייה")
        return _response(200, [])

    results = []

    for obj in response["Contents"]:
        key = obj["Key"]
        print(f"🔍 בודק קובץ: {key}")

        # מסנן רק קבצים עם התאריך הרצוי בשם
        if today_str not in key:
            continue

        try:
            file = s3.get_object(Bucket=BUCKET, Key=key)
            body = file["Body"].read().decode("utf-8").strip()
            if not body:
                continue

            data = json.loads(body)
            results.append({
                "license_plate": data.get("license_plate", "לא ידוע"),
                "reason": data.get("reason", "ללא סיבה"),
                "timestamp": data.get("timestamp", "לא צויין")
            })
            print(f"✅ נוסף מהרכב: {data.get('license_plate')}")

        except Exception as e:
            print(f"❌ שגיאה בקריאת הקובץ {key}: {e}")
            continue

    print(f"📦 נמצאו {len(results)} דוחות שנוצרו היום.")
    return _response(200, results)


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json"
        },
        "body": json.dumps(body, ensure_ascii=False)
    }
