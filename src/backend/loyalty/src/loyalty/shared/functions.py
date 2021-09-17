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
    """Aggregate list of loyalty transactions by incrementing and/or decrementing them

    Parameters
    ----------
    records : List[LoyaltyPoint]
        List of loyalty transactions

    Returns
    -------
    Dict[str, LoyaltyPointAggregate]
        Loyalty transactions aggregated per customer
    """
    seen: Dict[str, LoyaltyPoint] = {}
    aggregates: Dict[str, LoyaltyPointAggregate] = {}
    data = deepcopy(records)

    for record in data:
        if record.customerId not in seen:
            seen[record.customerId] = record
        else:
            # duplicate transaction
            if seen[record.customerId].booking == record.booking:
                continue
            if record.increment:
                seen[record.customerId].points += record.points
            else:
                seen[record.customerId].points -= record.points
    for customer, transaction in seen.items():
        points = transaction.points if transaction.increment else 0 - transaction.points
        aggregates[customer] = LoyaltyPointAggregate(
            total_points=points,
            tier=calculate_tier(points).value,
            booking=transaction.booking.id,
            increment=transaction.increment,
        )

    return aggregates
