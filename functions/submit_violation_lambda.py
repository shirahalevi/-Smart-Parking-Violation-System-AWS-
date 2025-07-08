import boto3
import os
import json
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')
sns = boto3.client('sns')
s3 = boto3.client('s3')

VEHICLES_TABLE = os.environ['VEHICLES_TABLE']
VIOLATIONS_TABLE = os.environ['VIOLATIONS_TABLE']
S3_BUCKET = "mobileye-parking-violation"
MANAGER_EMAIL = os.environ['MANAGER_EMAIL']
SENDER_EMAIL = "shirahalevi3@gmail.com"

def lambda_handler(event, context):
    try:
        data = json.loads(event['body'])
        license_plate = data.get("license_plate")
        reason = data.get("reason", "")
        description = data.get("description", "")
        image_url = data.get("image_url", "")

        if not license_plate or not reason:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing license_plate or reason"})}

        # שליפת רכב
        vehicles_table = dynamodb.Table(VEHICLES_TABLE)
        res = vehicles_table.get_item(Key={"license_plate": license_plate})
        if "Item" not in res:
            return {"statusCode": 404, "body": json.dumps({"error": "Vehicle not found"})}

        vehicle = res["Item"]
        fouls = int(vehicle.get("fouls", 0)) + 1
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
        violation_id = str(uuid.uuid4())

        # שמירת דוח ב- Violations
        violations_table = dynamodb.Table(VIOLATIONS_TABLE)
        violations_table.put_item(Item={
            "violation_id": violation_id,
            "license_plate": license_plate,
            "timestamp": timestamp,
            "reason": reason,
            "description": description,
            "image_url": image_url
        })

        # עדכון רכב
        update_expr = "SET fouls = :fouls"
        expr_vals = {":fouls": fouls}
        if fouls >= 3:
            update_expr = "SET flagged = :flagged, removed = :removed, fouls = :fouls"
            expr_vals = {
                ":flagged": True,
                ":removed": True,
                ":fouls": 0
               }
        else:
            update_expr = "SET fouls = :fouls"
            expr_vals = {
                ":fouls": fouls
                }       


        vehicles_table.update_item(
            Key={"license_plate": license_plate},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_vals
        )

        # העלאה ל-S3
        full_data = {
            "violation_id": violation_id,
            "license_plate": license_plate,
            "driver_name": vehicle.get("driver_name"),
            "employee_id": vehicle.get("employee_id"),
            "email": vehicle.get("email"),
            "phone_number": vehicle.get("phone_number"),
            "reason": reason,
            "description": description,
            "timestamp": timestamp,
            "fouls": fouls
        }
        local_path = "/tmp/report.json"
        with open(local_path, "w") as f:
            json.dump(full_data, f, indent=2)
        s3.upload_file(local_path, S3_BUCKET, f"violations/{license_plate}_{timestamp}.json")

        # שליחת מייל לפי מספר עבירות
        email = vehicle["email"]
        subject = "Parking Violation Notification"

        # גוף ההודעה ב-HTML כולל תמונה ופרטים
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <p>Dear {vehicle['driver_name']},</p>
        """

        if fouls == 1:
            html_body += f"""
            <p>This is a notification for a parking violation on your vehicle <strong>{license_plate}</strong>.</p>
            """
        elif fouls == 2:
            html_body += f"""
            <p>This is your <strong>second</strong> parking violation.</p>
            <p>⚠️ <strong>Note:</strong> One more violation will result in being blocked from the parking lot.</p>
            """
        else:
            html_body += f"""
            <p>🚫 Your vehicle has been <strong>blocked</strong> from entering the parking lot due to repeated violations.</p>
            <p>Please contact the control center for more details.</p>
            """

        html_body += f"""
            <p><strong>Violation reason:</strong> {reason}</p>
            <p><strong>Comment:</strong> {description or "—"}</p>
            <p><strong>Date:</strong> {timestamp}</p>
        """

        if image_url:
            html_body += f"""
            <p><strong>Image evidence:</strong><br>
            <img src="{image_url}" alt="Violation Image" style="max-width: 400px; margin-top: 10px;">
            <a href="{image_url}" target="_blank">Click here to view the image</a>
            </p>
            """

        html_body += """
            <p>Thank you,<br>
            Mobileye Control Center</p>
          </body>
        </html>
        """

        # אם יש 3 עבירות – גם מייל למנהל
        if fouls >= 3:
            ses.send_email(
                Source=SENDER_EMAIL,
                Destination={"ToAddresses": [MANAGER_EMAIL]},
                Message={
                    "Subject": {"Data": f"🚨 Vehicle {license_plate} Blocked"},
                    "Body": {"Text": {"Data": f"Vehicle {license_plate} has reached {fouls} violations and has been blocked."}}
                }
            )

        # שליחת מייל לנהג – HTML
        ses.send_email(
            Source=SENDER_EMAIL,
            Destination={"ToAddresses": [email]},
            Message={
                "Subject": {"Data": subject},
                "Body": {
                    "Html": {"Data": html_body}
                }
            }
        )

        # שליחת SMS קבוע
        phone_number = format_phone_number(vehicle["phone_number"])
        sms_message = f"{vehicle['driver_name']}, please move your vehicle {license_plate} due to a parking violation."
        sns.publish(PhoneNumber=phone_number, Message=sms_message)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Violation recorded and driver notified", "fouls": fouls})
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

def format_phone_number(phone):
    digits = ''.join(filter(str.isdigit, phone))
    if digits.startswith("0"):
        digits = digits[1:]
    return "+972" + digits
