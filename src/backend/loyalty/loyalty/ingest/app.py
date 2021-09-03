import json
from typing import Optional

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.batch import sqs_batch_processor
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from aws_lambda_powertools.utilities.typing import LambdaContext
from loyalty.shared.models import LoyaltyPoint
from loyalty.shared.storage import BaseStorage, DynamoDBStorage

tracer = Tracer()
logger = Logger()


@tracer.capture_method
def process_loyalty_points(record: dict, storage_client: Optional[BaseStorage] = None):
    payload: SQSRecord = SQSRecord(record)
    logger.set_correlation_id(payload.message_id)
    tracer.put_annotation(key="MessageId", value=payload.message_id)

    if storage_client is None:
        storage_client = DynamoDBStorage.from_env()

    transaction = LoyaltyPoint(**json.loads(payload.body))
    storage_client.add(item=transaction)


@sqs_batch_processor(record_handler=process_loyalty_points)
def lambda_handler(event: dict, context: LambdaContext):
    return "success"
