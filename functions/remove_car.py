import json
import boto3
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb')
VEHICLES_TABLE = 'Vehicles'

def lambda_handler(event, context):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "POST,OPTIONS"
    }

    try:
        data = json.loads(event['body'])
        license_plate = data.get('license_plate')

        if not license_plate:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Missing license_plate'})
            }

        table = dynamodb.Table(VEHICLES_TABLE)
        timestamp = datetime.now(timezone.utc).isoformat()

        # עדכון שדות 'removed' ו־'removed_at'
        table.update_item(
            Key={'license_plate': license_plate},
            UpdateExpression="SET removed = :removed, removed_at = :removed_at",
            ExpressionAttributeValues={
                ':removed': True,
                ':removed_at': timestamp
            }
        )

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'Vehicle marked as removed'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }
