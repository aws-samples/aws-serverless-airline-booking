from copy import deepcopy
from typing import Dict, List

from loyalty.shared.constants import LOYALTY_TIER_MIN_POINTS
from loyalty.shared.models import LoyaltyPoint, LoyaltyPointAggregate, LoyaltyTier


def calculate_tier(points: int) -> LoyaltyTier:
    """Calculate current tier from given points

    Parameters
    ----------
    points : int
        Total loyalty points to calculate against

    Returns
    -------
    LoyaltyTier
        Loyalty tier
    """
    if points >= LOYALTY_TIER_MIN_POINTS["GOLD"]:
        return LoyaltyTier.GOLD
    elif points >= LOYALTY_TIER_MIN_POINTS["SILVER"] < LOYALTY_TIER_MIN_POINTS["GOLD"]:
        return LoyaltyTier.SILVER
    else:
        return LoyaltyTier.BRONZE


def calculate_aggregate_points(records: List[LoyaltyPoint]) -> Dict[str, LoyaltyPointAggregate]:
    transactions: Dict[str, LoyaltyPoint] = {}
    aggregates: Dict[str, LoyaltyPointAggregate] = {}
    data = deepcopy(records)

    for record in data:
        if record.customerId in transactions:
            if record.increment:
                transactions[record.customerId].points += record.points
            else:
                transactions[record.customerId].points -= record.points
        else:
            transactions[record.customerId] = record

    for customer, transaction in transactions.items():
        aggregates[customer] = LoyaltyPointAggregate(
            total_points=transaction.points,
            tier=calculate_tier(transaction.points).value,
            booking=transaction.booking.id,
        )

    return aggregates
