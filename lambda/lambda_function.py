import json
import boto3
import urllib.request
import urllib.parse
import os
from datetime import datetime, timezone
from decimal import Decimal

# Connect to DynamoDB
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("weather-data")

def lambda_handler(event, context):

    # Read environment variables
    api_key = os.environ["API_KEY"]
    city = os.environ["CITY"]

    # Encode city name for URL
    city_encoded = urllib.parse.quote(city)

    # Build API URL
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city_encoded}&appid={api_key}&units=metric"
    )

    try:
        # Call OpenWeather API
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode("utf-8"))

        # Create item
        item = {
            "city": data["name"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature": Decimal(str(data["main"]["temp"])),
            "humidity": Decimal(str(data["main"]["humidity"])),
            "weather": data["weather"][0]["description"]
        }

        # Save to DynamoDB
        table.put_item(Item=item)

        return {
            "statusCode": 200,
            "body": json.dumps("Weather data stored successfully!")
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(str(e))
        }