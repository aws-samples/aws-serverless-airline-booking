import json
import os
import uuid
from dataclasses import dataclass
from pathlib import Path

import pytest
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes import DynamoDBStreamEvent
from aws_lambda_powertools.utilities.parameters import get_parameter

from loyalty.shared.models import Booking, LoyaltyPoint, Payment, create_loyalty_expiration_epoch
from loyalty.shared.storage import DynamoDBStorage

INGEST_TEST_EVENT = Path("tests/events/ingest_event.json")
AGG_INSERT_TEST_EVENT = Path("tests/events/aggregate_insert_event.json")


@pytest.fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "test"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:test"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


@pytest.fixture
def sqs_records():
    return load_event(filepath=INGEST_TEST_EVENT)


@pytest.fixture
def record(sqs_records):
    return sqs_records["Records"][0]


@pytest.fixture
def transaction(record):
    data: dict = json.loads(record["body"])
    transaction = LoyaltyPoint(booking=Booking(**data.pop("booking")), payment=Payment(**data.pop("payment")), **data)
    transaction.points = transaction.payment.amount
    return transaction


@pytest.fixture
def aggregate_insert_event():
    return load_event(filepath=AGG_INSERT_TEST_EVENT)


@pytest.fixture
def aggregate_records(aggregate_insert_event: dict):
    return DynamoDBStreamEvent(aggregate_insert_event)


@pytest.fixture
def aggregate_modify_records(aggregate_insert_event: dict):
    for record in aggregate_insert_event["Records"]:
        record["eventName"] = "MODIFY"

    return DynamoDBStreamEvent(aggregate_insert_event)


@pytest.fixture
def aggregate_agg_records(aggregate_insert_event: dict):
    for record in aggregate_insert_event["Records"]:
        record["dynamodb"]["Keys"]["pk"]["S"] = "CUSTOMER#AGGREGATE"

    return DynamoDBStreamEvent(aggregate_insert_event)


@pytest.fixture(scope="function")
def dynamodb_storage(monkeypatch):
    monkeypatch.setenv("LOYALTY_TABLE_NAME", "test")
    return DynamoDBStorage.from_env(logger=Logger(service="test"))


def load_event(filepath: Path) -> dict:
    with filepath.open() as event:
        return json.load(event)


@pytest.fixture
def fake_loyalty_point():
    return LoyaltyPoint(
        customerId=f"fake-{uuid.uuid4()}",
        booking=Booking(id="dummy", reference="dummy", outboundFlightId="dummy"),
        payment=Payment(receipt="fake", amount=100),
        points=100,
        expireAt=create_loyalty_expiration_epoch(days=7),
    )


@pytest.fixture
def stage():
    return os.getenv("AWS_BRANCH", "develop")


@pytest.fixture
def table_name(stage):
    table = os.getenv("LOYALTY_TABLE_NAME")
    if table is None:
        table = get_parameter(name=f"/{stage}/service/loyalty/storage/table")
    return table
