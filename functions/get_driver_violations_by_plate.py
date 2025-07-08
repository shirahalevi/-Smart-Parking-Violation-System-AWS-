import boto3
import json

s3 = boto3.client("s3")
BUCKET = "mobileye-parking-violation"
PREFIX = "violations/"

def lambda_handler(event, context):
    # ✅ שלב 1: לטפל בבקשת OPTIONS מראש (preflight)
    if event.get("httpMethod") == "OPTIONS":
        return _response(200, "OK")

    # שלב 2: קריאה רגילה לנתוני עבר
    license_plate = event["pathParameters"]["license_plate"]

    response = s3.list_objects_v2(Bucket=BUCKET, Prefix=PREFIX)
    if "Contents" not in response:
        return _response(200, [])

    violations = []

    for obj in response["Contents"]:
        key = obj["Key"]
        if not key.endswith(".json"):
            continue
        if not key.startswith(f"{PREFIX}{license_plate}_"):
            continue

        file = s3.get_object(Bucket=BUCKET, Key=key)
        content = file["Body"].read().decode("utf-8").strip()

        if not content:
            continue

        try:
            data = json.loads(content)
            violations.append({
                "timestamp": data.get("timestamp"),
                "reason": data.get("reason"),
                "description": data.get("description", "")
            })
        except Exception as e:
            print(f"Error parsing {key}: {str(e)}")

    return _response(200, violations)

def _response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "GET,OPTIONS",
            "Content-Type": "application/json"
        },
        "body": json.dumps(body if isinstance(body, (list, dict)) else {"message": body})
    }
