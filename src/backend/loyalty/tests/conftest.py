import json
import os
import uuid
from dataclasses import dataclass
from pathlib import Path

import pytest
from aws_lambda_powertools.utilities.data_classes import DynamoDBStreamEvent
from aws_lambda_powertools.utilities.parameters import get_parameter

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
def dynamodb_stream_records():
    return load_event(filepath=AGG_INSERT_TEST_EVENT)


@pytest.fixture
def dynamodb_stream_modify_records(dynamodb_stream_records: dict):
    for record in dynamodb_stream_records["Records"]:
        record["eventName"] = "MODIFY"

    return DynamoDBStreamEvent(dynamodb_stream_records)


@pytest.fixture
def dynamodb_stream_aggregate_records(dynamodb_stream_records: dict):
    for record in dynamodb_stream_records["Records"]:
        record["dynamodb"]["Keys"]["pk"]["S"] = "CUSTOMER#AGGREGATE"

    return DynamoDBStreamEvent(dynamodb_stream_records)


def load_event(filepath: Path) -> dict:
    with filepath.open() as event:
        return json.load(event)


@pytest.fixture
def stage():
    return os.getenv("AWS_BRANCH", "develop")


@pytest.fixture
def table_name(stage):
    table = os.getenv("LOYALTY_TABLE_NAME")
    if table is None:
        table = get_parameter(name=f"/{stage}/service/loyalty/storage/table")
    return table
