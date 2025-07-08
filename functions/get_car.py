import json
import boto3
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

dynamodb = boto3.resource('dynamodb')
VEHICLES_TABLE = 'Vehicles'

def lambda_handler(event, context):
    try:
        license_plate = event['queryStringParameters'].get('license_plate')
        print("🔍 Received license_plate:", license_plate)
        if not license_plate:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'license_plate required'})
            }

        table = dynamodb.Table(VEHICLES_TABLE)
        response = table.get_item(Key={'license_plate': license_plate})
        print("📦 DynamoDB get_item response:", response)

        item = response.get('Item')
        if not item:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Car not found'})
            }

        # אל תציג אם removed = true, אחרת תציג תמיד
        if item.get('removed') is True:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Car is marked as removed'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps(item, cls=DecimalEncoder)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
