from loyalty.shared.models import LoyaltyTier
from loyalty.shared.constants import LOYALTY_TIER_MIN_POINTS


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
