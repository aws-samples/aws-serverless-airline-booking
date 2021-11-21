import os
import uuid
from typing import Optional

from aws_lambda_powertools import Logger

from loyalty.shared.models import Booking, LoyaltyPoint, Payment, create_loyalty_expiration_epoch
from loyalty.shared.storage import BaseStorage, DynamoDBStorage


def make_loyalty_point(customer_id: Optional[str] = None, points: int = 100):
    """Create fake loyalty point for fake-<id> customer ID"""
    customer_id = customer_id or f"fake-{uuid.uuid4()}"
    return LoyaltyPoint(
        customerId=customer_id,
        booking=Booking(id="dummy", reference="dummy", outboundFlightId="dummy"),
        payment=Payment(receipt="fake", amount=points),
        points=points,
        expireAt=create_loyalty_expiration_epoch(days=7),
    )


def make_loyalty_points(customer_id: Optional[str] = None, count: int = 2):
    """Create fake loyalty points, by default 2 for fake-<id> customer ID"""
    customer_id = f"fake-{uuid.uuid4()}"
    return [make_loyalty_point(customer_id=customer_id) for _ in range(count)]


def make_dynamodb_storage():
    os.environ["LOYALTY_TABLE_NAME"] = "test"
    return DynamoDBStorage.from_env(logger=Logger(service="test"))
