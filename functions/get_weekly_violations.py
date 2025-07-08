import boto3
import os
import json
from datetime import datetime, timedelta, timezone
from collections import defaultdict

s3 = boto3.client('s3')

BUCKET = "mobileye-parking-violation"
PREFIX = "violations/daily_violations/"

def lambda_handler(event, context):
    start_date = datetime.now(timezone.utc) - timedelta(days=7)

    response = s3.list_objects_v2(Bucket=BUCKET, Prefix=PREFIX)
    if 'Contents' not in response:
        return _response(200, [])

    violation_counts = defaultdict(int)

    for obj in response['Contents']:
        if obj['LastModified'] >= start_date:
            key = obj['Key']
            file = s3.get_object(Bucket=BUCKET, Key=key)
            body = file['Body'].read().decode('utf-8').strip()

            if not body:
                continue

            try:
                data = json.loads(body)
                license_plate = data.get("license_plate")
                if license_plate:
                    violation_counts[license_plate] += 1
            except Exception as e:
                print(f"Error parsing file {key}: {str(e)}")

    results = [{"license_plate": lp, "totalViolations": count} for lp, count in violation_counts.items() if count >= 1]
    return _response(200, results)

def _response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }
