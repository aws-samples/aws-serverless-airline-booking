import datetime
import json
import os

import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.batch import sqs_batch_processor
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from botocore.exceptions import ClientError
from cyksuid import ksuid

tracer = Tracer()
logger = Logger()

session = boto3.Session()
table_name = os.getenv("LOYALTY_TABLE_NAME", "undefined")
dynamodb = session.resource("dynamodb").Table(table_name)


@tracer.capture_method
def process_loyalty_points(record: dict, dynamodb_client=dynamodb) -> dict:
    record: SQSRecord = SQSRecord(record)
    logger.set_correlation_id(record.message_id)
    payload = json.loads(record.body)

    transaction = f"TRANSACTION#{ksuid.ksuid().encoded.decode()}"
    payment_details = payload.get("paymentDetails", {})
    loyalty_transaction = {
        "pk": payload.get("customerId"),
        "sk": transaction,
        "outboundFlightId": payload.get("outboundFlightId"),
        "tier": "BRONZE",
        "points": payment_details.get("ticketPrice"),
        "status": "ACTIVE",
        "bookingDetails": {**payload.get("bookingDetails")},
        "paymentDetails": {**payment_details},
        # Convert ksuid time to utc?
        "createdAt": str(datetime.datetime.utcnow()),
    }

    logger.debug(f"Inserting loyalty transaction into '{table_name}' table")
    try:
        dynamodb_client.put_item(Item=loyalty_transaction)
    except ClientError:
        logger.exception(
            f"Unable to insert loyalty transaction into '{table_name}' table"
        )
    except:
        logger.exception(
            "Unknown error when inserting loyalty transaction into '{table_name}' table"
        )

    return loyalty_transaction


@sqs_batch_processor(record_handler=process_loyalty_points)
def lambda_handler(event, context):
    return "success"
