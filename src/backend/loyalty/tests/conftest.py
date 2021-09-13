import json
from dataclasses import dataclass
from pathlib import Path

import pytest
from botocore.stub import Stubber
from loyalty.shared.models import LoyaltyPoint
from loyalty.shared.storage import DynamoDBStorage

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
    return LoyaltyPoint(**json.loads(record["body"]))


@pytest.fixture
def aggregate_records():
    return load_event(filepath=AGG_INSERT_TEST_EVENT)


@pytest.fixture(scope="function")
def dynamodb_stub(monkeypatch):
    monkeypatch.setenv("TABLE_NAME", "test")
    ddb_storage = DynamoDBStorage.from_env()
    stubber = Stubber(ddb_storage.client.meta.client)
    stubber.activate()
    yield ddb_storage, stubber
    stubber.deactivate()
    stubber.assert_no_pending_responses()


def load_event(filepath: Path) -> dict:
    with filepath.open() as event:
        return json.load(event)
