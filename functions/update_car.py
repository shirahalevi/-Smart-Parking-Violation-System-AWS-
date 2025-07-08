import json
import boto3

dynamodb = boto3.resource('dynamodb')
VEHICLES_TABLE = 'Vehicles'

RESERVED_WORDS = {"role", "name", "status", "type"}  # תוסיפי לפה מילים שמורות נוספות לפי הצורך

def lambda_handler(event, context):
    try:
        data = json.loads(event['body'])
        license_plate = data.get('license_plate')

        if not license_plate:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing license_plate'})
            }

        update_expr = []
        expr_vals = {}
        expr_names = {}

        for key in data:
            if key != 'license_plate':
                placeholder = f":{key}"
                field_expr = f"{key}"

                # אם זו מילה שמורה – נשתמש בשם חלופי
                if key in RESERVED_WORDS:
                    expr_names[f"#{key}"] = key
                    field_expr = f"#{key}"

                update_expr.append(f"{field_expr} = {placeholder}")
                expr_vals[placeholder] = data[key]

        if not update_expr:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No fields to update'})
            }

        update_params = {
            'Key': {'license_plate': license_plate},
            'UpdateExpression': 'SET ' + ', '.join(update_expr),
            'ExpressionAttributeValues': expr_vals
        }

        if expr_names:
            update_params['ExpressionAttributeNames'] = expr_names

        table = dynamodb.Table(VEHICLES_TABLE)
        table.update_item(**update_params)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Car updated successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
