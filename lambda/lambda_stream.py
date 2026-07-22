import json
import boto3
from decimal import Decimal
from datetime import datetime

s3 = boto3.client("s3")

BUCKET_NAME = "weather-data-66"

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def lambda_handler(event, context):

    for record in event["Records"]:

        if record["eventName"] == "INSERT":

            item = record["dynamodb"]["NewImage"]

            weather_data = {}

            for key, value in item.items():
                if "S" in value:
                    weather_data[key] = value["S"]
                elif "N" in value:
                    weather_data[key] = Decimal(value["N"])

            file_name = f"weather/{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=file_name,
                Body=json.dumps(weather_data, cls=DecimalEncoder),
                ContentType="application/json"
            )

    return {
        "statusCode": 200,
        "body": "Uploaded to S3 successfully"
    }