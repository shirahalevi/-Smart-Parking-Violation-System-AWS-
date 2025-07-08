import boto3
import os
import json
from datetime import datetime, timedelta, timezone
from collections import Counter

s3 = boto3.client('s3')
ses = boto3.client('ses')

BUCKET = "mobileye-parking-violation"
PREFIX = "violations/"
EMAIL = os.environ['MANAGER_EMAIL']

CATEGORIES = [
    "חניה בחניית נכים",
    "חניה בחניית היריון",
    "חניה בחניה שמורה",
    "חניה בעמדת טעינה",
    "חסימת מחסום",
    "חסימת מחסן",
    "חסימת רכב",
    "חסימת חניה כפולה",
    "עצירה בנתיב נסיעה",
    "אחר"
]

def lambda_handler(event, context):
    start_date = datetime.now(timezone.utc) - timedelta(days=7)
    response = s3.list_objects_v2(Bucket=BUCKET, Prefix=PREFIX)

    if 'Contents' not in response:
        return {"message": "No violations this week."}

    category_counter = Counter({category: 0 for category in CATEGORIES})
    total_violations = 0

    for obj in response['Contents']:
        last_modified = obj['LastModified']
        if last_modified >= start_date:
            try:
                file = s3.get_object(Bucket=BUCKET, Key=obj['Key'])
                body = file['Body'].read().decode('utf-8').strip()
                if not body:
                    continue

                data = json.loads(body)
                reason = data.get('reason', '').strip()

                if reason in CATEGORIES:
                    category_counter[reason] += 1
                    total_violations += 1
                else:
                    print(f"⚠️ Skipped unknown reason: {reason}")

            except Exception as e:
                print(f"❌ Error reading/parsing file {obj['Key']}: {e}")
                continue

    if total_violations == 0:
        return {"message": "No violations found for this week."}

    body = f"📊 דו\"ח עבירות שבועי – החל מתאריך {start_date.date()}:\n\n"
    for category in CATEGORIES:
        count = category_counter[category]
        body += f"- {category}: {count}\n"
    body += f"\nסה\"כ עבירות: {total_violations}"

    # הוספת סימן RTL לתחילת גוף ההודעה
    body = "\u200f" + body

    try:
        ses.send_email(
            Source=EMAIL,
            Destination={'ToAddresses': [EMAIL]},
            Message={
                'Subject': {'Data': f"📊 Weekly Parking Violations Report – Since {start_date.date()}"},
                'Body': {'Text': {'Data': body}}
            }
        )
        print("✅ Weekly summary email sent.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return {"error": f"Failed to send email: {str(e)}"}

    return {
        "status": "Weekly summary sent (categorized)",
        "total": total_violations,
        "categories": dict(category_counter)
    }
