import json
from dataclasses import dataclass
from pathlib import Path

import pytest
from loyalty.shared.models import LoyaltyPoint

INGEST_TEST_EVENT = Path("tests/events/ingest_event.json")


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


def load_event(filepath: Path) -> dict:
    with filepath.open() as event:
        return json.load(event)
