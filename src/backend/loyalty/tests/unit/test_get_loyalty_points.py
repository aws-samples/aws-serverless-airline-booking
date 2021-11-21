import json

from aws_lambda_powertools.utilities.typing import LambdaContext
from pytest_mock import MockerFixture

from loyalty.get import app
from loyalty.shared.constants import LOYALTY_TIER_MIN_POINTS
from loyalty.shared.models import LoyaltyTier
from loyalty.shared.storage import FakeStorage
from tests.utils import make_loyalty_point


def test_get_loyalty_points_not_found_defaults_to_bronze():
    storage = FakeStorage()
    expected = {"level": LoyaltyTier.BRONZE.value, "points": 0, "remainingPoints": LOYALTY_TIER_MIN_POINTS["SILVER"]}
    assert app.get_loyalty_points(customer_id="blah", storage_client=storage) == expected


def test_get_loyalty_points():
    storage = FakeStorage()
    loyalty_point = make_loyalty_point(points=50_000)
    storage.add(item=loyalty_point)

    ret = app.get_loyalty_points(customer_id=loyalty_point.customerId, storage_client=storage)
    assert ret["level"] == "SILVER"
    assert ret["points"] == 50_000


def test_get_loyalty_points_no_remaining_points_next_tier():
    storage = FakeStorage()
    loyalty_point = make_loyalty_point(points=100_000)
    storage.add(item=loyalty_point)

    ret = app.get_loyalty_points(customer_id=loyalty_point.customerId, storage_client=storage)
    assert ret["level"] == "GOLD"
    assert ret["remainingPoints"] == 0


def test_get_loyalty_points_lambda_handler(mocker: MockerFixture, lambda_context: LambdaContext):
    storage = FakeStorage()
    loyalty_point = make_loyalty_point(points=5000)
    event = {"path": f"/loyalty/{loyalty_point.customerId}", "httpMethod": "GET"}
    storage.add(item=loyalty_point)

    mocker.patch.object(app.DynamoDBStorage, "from_env", return_value=storage)
    ret = app.lambda_handler(event=event, context=lambda_context)

    expected = json.dumps(
        {
            "level": "BRONZE",
            "points": loyalty_point.points,
            "remainingPoints": LOYALTY_TIER_MIN_POINTS["SILVER"] - loyalty_point.points,
        },
        separators=(",", ":"),
    )
    assert ret["body"] == expected
