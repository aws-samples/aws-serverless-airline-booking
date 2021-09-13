from typing import Dict, List

from loyalty.shared.constants import LOYALTY_TIER_MIN_POINTS
from loyalty.shared.models import LoyaltyPointAggregate, LoyaltyTier
from copy import deepcopy


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


def calculate_aggregate_points(records: List[LoyaltyPointAggregate]) -> Dict[str, LoyaltyPointAggregate]:
    transactions = {}
    data = deepcopy(records)
    for record in data:
        if record.customerId in transactions:
            if record.increment:
                transactions[record.customerId].points += record.points
            else:
                transactions[record.customerId].points -= record.points
        else:
            transactions[record.customerId] = record

    for transaction in transactions.values():
        transaction.tier = calculate_tier(transaction.points).value

    return transactions
