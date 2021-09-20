import time
from typing import Tuple

import boto3
from boto3.dynamodb.conditions import Key

from loyalty.shared.models import LoyaltyPoint, LoyaltyTier
from loyalty.shared.storage import DynamoDBStorage

# TODO: tearDown:
### A) Delete all fake records including aggregates (batch_delete)
### B) Batch update items createdAt and updatedAt and let DDB delete it as part of TTL

session = boto3.Session()
MAX_RETRIES = 5
QUERY_TIMEOUT = 0.6


def fetch_aggregate(storage: DynamoDBStorage, customer_id: str) -> Tuple[LoyaltyTier, int]:
    for _ in range(1, MAX_RETRIES + 1):
        tier, points = storage.get_customer_tier_points(customer_id=customer_id)
        if points != 0:
            return tier, points
        time.sleep(QUERY_TIMEOUT)
    return LoyaltyTier.BRONZE, 0


def test_add_item_and_aggregation(fake_loyalty_point: LoyaltyPoint, table_name):
    ddb = session.resource("dynamodb").Table(table_name)
    storage = DynamoDBStorage(client=ddb)

    storage.add(item=fake_loyalty_point)
    transaction = ddb.query(
        KeyConditionExpression=Key("pk").eq(f"CUSTOMER#TRANSACTION#{fake_loyalty_point.customerId}")
        & Key("sk").begins_with("TRANSACTION")
    )
    assert transaction["Count"] == 1

    tier, points = fetch_aggregate(storage=storage, customer_id=fake_loyalty_point.customerId)
    assert points == fake_loyalty_point.points
    assert tier.value == fake_loyalty_point.tier


def test_aggregate_idempotency(fake_loyalty_point: LoyaltyPoint, table_name):
    # GIVEN
    ddb = session.resource("dynamodb").Table(table_name)
    storage = DynamoDBStorage(client=ddb)

    # WHEN we attempt circumvent dedup logic in aggregate code
    storage.add(item=fake_loyalty_point)
    storage.add(item=fake_loyalty_point)
    storage.add(item=fake_loyalty_point)

    tier, points = fetch_aggregate(storage=storage, customer_id=fake_loyalty_point.customerId)

    # THEN we should have calculated aggregate key only once
    assert points == fake_loyalty_point.points
    assert tier.value == fake_loyalty_point.tier
