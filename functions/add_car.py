import json
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
VEHICLES_TABLE = 'Vehicles'

def lambda_handler(event, context):
    try:
        data = json.loads(event['body'])

        required_fields = ['license_plate', 'driver_name', 'employee_id', 'phone_number', 'email', 'role']
        for field in required_fields:
            if field not in data:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'Missing field: {field}'})
                }

        # שדות ברירת מחדל
        data['fouls'] = 0
        data['flagged'] = False
        data['removed'] = False
        data['removed_at'] = None

        # 🆕 הרשאות חניה - אם לא נשלח, ברירת מחדל False
        data['disabled_permit'] = data.get('disabled_permit', False)
        data['pregnancy_permit'] = data.get('pregnancy_permit', False)
        data['electric_vehicle'] = data.get('electric_vehicle', False)

        table = dynamodb.Table(VEHICLES_TABLE)
        table.put_item(Item=data)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Car added successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
