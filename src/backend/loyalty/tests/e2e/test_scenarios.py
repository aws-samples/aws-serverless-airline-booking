import json
import os
import time
import uuid
from dataclasses import asdict

import boto3
import pytest
import requests

from loyalty.shared.constants import LOYALTY_TIER_MIN_POINTS
from loyalty.shared.models import Booking, LoyaltyPoint, Payment

# from aws_lambda_powertools.utilities.parameters import get_parameter

MAX_RETRIES = 10
QUERY_TIMEOUT = 2

# TODO: Investigate ~20s E2E before enabling parameter fetching
# TODO: Create a single parameter with all config per service to aid tests


@pytest.fixture
def api_id(stage):
    api_id = os.getenv("LOYALTY_GRAPHQL_API_ID")
    if api_id is None:
        api_id = "jtxiyxesnfablboy2borw2lnqu"
        # api_id = get_parameter(name=f"/{stage}/service/amplify/api/id")
    return api_id


@pytest.fixture
def api_key(api_id):
    """
    API Key for AppSync
    """
    appsync = boto3.client("appsync")
    ret = appsync.create_api_key(apiId=api_id)

    yield ret["apiKey"]["id"]

    appsync.delete_api_key(apiId=api_id, id=ret["apiKey"]["id"])


@pytest.fixture
def api_url():
    api_url = os.getenv("LOYALTY_GRAPHQL_API_URL")
    if api_url is None:
        api_url = "https://bjscququargkllwwjpzlwydqfq.appsync-api.eu-west-1.amazonaws.com/graphql"

    return api_url


@pytest.fixture
def queue_url():
    queue_url = os.getenv("LOYALTY_QUEUE_URL")
    if queue_url is None:
        queue_url = "https://bjscququargkllwwjpzlwydqfq.appsync-api.eu-west-1.amazonaws.com/graphql"

    return queue_url


@pytest.fixture(scope="module")
def fake_transaction():
    return LoyaltyPoint(
        customerId=f"fake-{uuid.uuid4()}",
        points=100,
        booking=Booking(id=str(uuid.uuid4()), reference="dummy", outboundFlightId=str(uuid.uuid4())),
        payment=Payment(receipt="dummy", amount=100),
    )


def fetch_aggregate(customer_id: str, api_url: str, api_key: str) -> dict:
    headers = {"x-api-key": api_key}

    query = """
      query getLoyalty($customer: String) {
        getLoyalty(customer: $customer) {
            points
            level
            remainingPoints
        }
      }
    """

    payload = {"query": query, "variables": {"customer": customer_id}}
    for _ in range(1, MAX_RETRIES + 1):
        response = requests.post(api_url, json=payload, headers=headers).json()
        if response["data"]["getLoyalty"]["points"] != 0:
            return response
        time.sleep(QUERY_TIMEOUT)

    return response


def test_loyalty_processing(api_url: str, api_key: str, queue_url: str, fake_transaction: LoyaltyPoint):
    """Test Loyalty can be ingested and fetched later"""

    sqs = boto3.client("sqs")
    # test idempotency too by sending duplicate messages
    sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(asdict(fake_transaction)))
    sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(asdict(fake_transaction)))

    response = fetch_aggregate(customer_id=fake_transaction.customerId, api_url=api_url, api_key=api_key)

    assert response["data"]["getLoyalty"]["points"] == fake_transaction.points
    assert response["data"]["getLoyalty"]["level"] == fake_transaction.tier
    assert (
        response["data"]["getLoyalty"]["remainingPoints"] == LOYALTY_TIER_MIN_POINTS["SILVER"] - fake_transaction.points
    )
