from typing import List, Dict

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import DynamoDBStreamEvent, event_source
from aws_lambda_powertools.utilities.typing import LambdaContext
from loyalty.shared.storage import BaseStorage, DynamoDBStorage
from loyalty.shared.models import LoyaltyPointAggregate
from loyalty.aggregate.tier import calculate_tier

tracer = Tracer()
logger = Logger()


@tracer.capture_method
def aggregate_loyalty_points(records: List[LoyaltyPointAggregate], storage_client: BaseStorage = None):
    if storage_client is None:
        storage_client = DynamoDBStorage.from_env()

    transactions = {}
    for record in records:
        if record.customerId in transactions:
            if record.increment:
                transactions[record.customerId].points += record.points
            else:
                transactions[record.customerId].points -= record.points
        else:
            transactions[record.customerId] = record

    for transaction in transactions.values():
        transaction.tier = calculate_tier(transaction.points).value

    storage_client.add_aggregate(items=transactions)

    return True


@event_source(data_class=DynamoDBStreamEvent)
def lambda_handler(event: DynamoDBStreamEvent, context: LambdaContext):
    aggregates = DynamoDBStorage.build_loyalty_point_aggregate(event)
    return aggregate_loyalty_points(records=aggregates)
