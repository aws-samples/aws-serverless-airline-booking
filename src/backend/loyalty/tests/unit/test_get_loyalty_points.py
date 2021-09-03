from loyalty.shared.storage import FakeStorage
from loyalty.get import app
from loyalty.shared.constants import LOYALTY_TIER_MIN_POINTS
from loyalty.shared.models import LoyaltyPoint, LoyaltyTier


def test_get_loyalty_points_not_found_defaults_to_bronze():
    storage = FakeStorage()
    expected = {"level": LoyaltyTier.BRONZE.value, "points": 0, "remainingPoints": LOYALTY_TIER_MIN_POINTS["SILVER"]}
    assert app.get_loyalty_points(customer_id="blah", storage_client=storage) == expected


def test_get_loyalty_points(transaction: LoyaltyPoint):
    storage = FakeStorage()
    storage.add(item=transaction)
    ret = app.get_loyalty_points(customer_id=transaction.customerId, storage_client=storage)
    assert ret["level"] == "BRONZE"
    assert ret["points"] == 100
