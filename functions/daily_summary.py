import boto3
import os
import json
from datetime import datetime, timedelta, timezone

s3 = boto3.client('s3')
ses = boto3.client('ses')

BUCKET = "mobileye-parking-violation"
PREFIX = "violations/"
EMAIL = os.environ['MANAGER_EMAIL']

def lambda_handler(event, context):
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(hours=24)

    print(f"📅 Current UTC time: {now}")
    print(f"🕓 Looking for files modified after: {start_time}")

    response = s3.list_objects_v2(Bucket=BUCKET, Prefix=PREFIX)
    violations = []

    if 'Contents' in response:
        print(f"📂 Found {len(response['Contents'])} files under {PREFIX}")
        for obj in response['Contents']:
            key = obj['Key']
            last_modified = obj['LastModified']
            print(f"🔍 Checking file: {key} | LastModified: {last_modified}")

            if last_modified >= start_time:
                print(f"✅ File is within 24h range. Processing: {key}")
                try:
                    file = s3.get_object(Bucket=BUCKET, Key=key)
                    body = file['Body'].read().decode('utf-8').strip()
                    data = json.loads(body)
                    violations.append(data)
                except Exception as e:
                    print(f"❌ Error reading/parsing file {key}: {e}")
            else:
                print(f"⏩ Skipping file {key} – older than 24h")
    else:
        print("📭 No files found in S3 prefix.")

    print(f"📊 Total violations collected: {len(violations)}")

    if not violations:
        subject = "📭 Daily Violations Report – No Violations"
        body = (
            "Daily Parking Violation Summary (Last 24 hours):\n\n"
            "There were no parking violations reported in the last 24 hours.\n\n"
            "This is an automated summary sent by the enforcement system."
        )
    else:
        subject = "📈 Daily Violations Report – Summary for Last 24 Hours"
        body = "Daily Parking Violation Summary (Last 24 hours):\n\n"
        for v in violations:
            body += (
                f"- {v.get('driver_name', 'Unknown')} "
                f"({v.get('license_plate', 'No Plate')}), "
                f"Reason: {v.get('reason', 'No reason')}, "
                f"Fouls: {v.get('fouls', '-')}, "
                f"Time: {v.get('timestamp', 'No timestamp')}\n"
            )

    print("📧 Sending email...")
    try:
        ses.send_email(
            Source=EMAIL,
            Destination={'ToAddresses': [EMAIL]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )
        print("✅ Email sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return {
            "status": "error",
            "message": f"Failed to send email: {str(e)}"
        }

    return {
        "status": "Email sent",
        "violations_sent": len(violations)
    }
