import json
from dataclasses import dataclass
from pathlib import Path

import pytest
from loyalty.shared.models import LoyaltyPoint
from loyalty.shared.storage import DynamoDBStorage
from aws_lambda_powertools import Logger

INGEST_TEST_EVENT = Path("tests/events/ingest_event.json")
AGG_INSERT_TEST_EVENT = Path("tests/events/aggregate_insert_event.json")
AGG_REMOVE_TEST_EVENT = Path("tests/events/aggregate_remove_event.json")


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
def records():
    return load_event(filepath=INGEST_TEST_EVENT)


@pytest.fixture
def record():
    return load_event(filepath=INGEST_TEST_EVENT)["Records"][0]


@pytest.fixture
def transaction(record):
    transaction = LoyaltyPoint(**json.loads(record["body"]))
    transaction.points = transaction.payment["amount"]
    return transaction


@pytest.fixture
def aggregate_records():
    return load_event(filepath=AGG_INSERT_TEST_EVENT)


@pytest.fixture
def aggregate_modify_records():
    event = load_event(filepath=AGG_INSERT_TEST_EVENT)
    for record in event["Records"]:
        record["eventName"] = "MODIFY"

    return event


@pytest.fixture(scope="function")
def dynamodb_storage(monkeypatch):
    monkeypatch.setenv("TABLE_NAME", "test")
    return DynamoDBStorage.from_env(logger=Logger(service="test"))


def load_event(filepath: Path) -> dict:
    with filepath.open() as event:
        return json.load(event)
