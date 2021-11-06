import json
from typing import Optional

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.batch import sqs_batch_processor
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from aws_lambda_powertools.utilities.typing import LambdaContext

from loyalty.shared.models import Booking, LoyaltyPoint, Payment
from loyalty.shared.storage import BaseStorage, DynamoDBStorage

tracer = Tracer()
logger = Logger()


@tracer.capture_method
def ingest_loyalty_points(transaction: LoyaltyPoint, storage_client: Optional[BaseStorage] = None):
    tracer.put_annotation(key="customerId", value=transaction.customerId)
    logger.append_keys(customer_id=transaction.customerId, booking_id=transaction.booking.id)

    if storage_client is None:
        storage_client = DynamoDBStorage.from_env()

    storage_client.add(item=transaction)


@tracer.capture_method
def sqs_record_handler(record: dict):
    payload: SQSRecord = SQSRecord(record)
    data: dict = json.loads(payload.body)

    try:
        transaction = LoyaltyPoint(
            booking=Booking(**data.pop("booking")), payment=Payment(**data.pop("payment")), **data
        )
    except KeyError:
        logger.exception("Possibly missing booking or payment required data", data)
        raise ValueError("Invalid payload")

    ingest_loyalty_points(transaction=transaction)

    tracer.put_metadata(
        key="ProcessedMessage",
        value={
            "message_id": payload.message_id,
            "record_attributes": payload.attributes.raw_event,
            "source_arn": payload.event_source_arn,
        },
    )


@sqs_batch_processor(record_handler=sqs_record_handler)
@logger.inject_lambda_context
def lambda_handler(event: dict, context: LambdaContext):
    return "success"


# TODO: Revisit correlation ID choice [booking ID or X-Ray]
