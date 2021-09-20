from typing import Dict, List, Optional

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import DynamoDBStreamEvent, event_source
from aws_lambda_powertools.utilities.typing import LambdaContext

from loyalty.shared.functions import calculate_aggregate_points
from loyalty.shared.models import LoyaltyPoint, LoyaltyPointAggregate
from loyalty.shared.storage import BaseStorage, DynamoDBStorage

tracer = Tracer()
logger = Logger()


@tracer.capture_method
def aggregate_loyalty_points(
    records: List[LoyaltyPoint], storage_client: Optional[BaseStorage] = None
) -> Dict[str, LoyaltyPointAggregate]:
    if storage_client is None:
        storage_client = DynamoDBStorage.from_env()

    transactions = calculate_aggregate_points(records=records)
    logger.debug(f"Transactions before we store them: {records}")
    storage_client.add_aggregate(items=transactions)

    return transactions


@tracer.capture_lambda_handler
@logger.inject_lambda_context
@event_source(data_class=DynamoDBStreamEvent)
def lambda_handler(event: DynamoDBStreamEvent, _: LambdaContext):
    logger.debug(event.raw_event)
    aggregates = DynamoDBStorage.build_loyalty_point_list(event=event)
    ret = aggregate_loyalty_points(records=aggregates)
    return {"processed_aggregate": len(ret)}
