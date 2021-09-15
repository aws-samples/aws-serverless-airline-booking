from loyalty.get import app
from loyalty.shared.constants import LOYALTY_TIER_MIN_POINTS
from loyalty.shared.models import LoyaltyPoint, LoyaltyTier
from loyalty.shared.storage import FakeStorage


def test_get_loyalty_points_not_found_defaults_to_bronze():
    storage = FakeStorage()
    expected = {"level": LoyaltyTier.BRONZE.value, "points": 0, "remainingPoints": LOYALTY_TIER_MIN_POINTS["SILVER"]}
    assert app.get_loyalty_points(customer_id="blah", storage_client=storage) == expected


def test_get_loyalty_points(transaction: LoyaltyPoint):
    storage = FakeStorage()
    transaction.payment.amount = 50_000
    storage.add(item=transaction)
    ret = app.get_loyalty_points(customer_id=transaction.customerId, storage_client=storage)
    assert ret["level"] == "SILVER"
    assert ret["points"] == 50_000


def test_handler_process_api_route(mocker, lambda_context):
    storage = FakeStorage()
    app.DynamoDBStorage.from_env = mocker.MagicMock(return_value=storage)
    event = {"path": "/loyalty/test", "resource": "/loyalty/{customerId}", "httpMethod": "GET"}
    app.lambda_handler(event=event, context=lambda_context)


def test_get_loyalty_points_no_remaining_points_next_tier(transaction: LoyaltyPoint):
    storage = FakeStorage()
    transaction.payment.amount = 100_000
    storage.add(item=transaction)
    ret = app.get_loyalty_points(customer_id=transaction.customerId, storage_client=storage)
    assert ret["level"] == "GOLD"
    assert ret["remainingPoints"] == 0
