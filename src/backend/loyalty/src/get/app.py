import json


def lambda_handler(event, context):
    # Dummy response
    return {
        "statusCode": 200,
        "body": json.dumps({
            "points": 10000,
            "level": "bronze",
            "remainingPoints": 100
        })
    }
