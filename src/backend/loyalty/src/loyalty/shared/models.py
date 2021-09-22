import calendar
import datetime
from dataclasses import dataclass, field
from enum import Enum


def create_loyalty_expiration_epoch(days: int = 365) -> int:
    """Create expiration utc time in epoch for loyalty transaction

    Parameters
    ----------
    days : int, optional
        days before it expires, by default 365

    Returns
    -------
    int
        expiration in epoch time
    """
    ttl = datetime.datetime.utcnow() + datetime.timedelta(days=days)
    return calendar.timegm(ttl.timetuple())


class PointStatus(Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


class LoyaltyTier(Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"


@dataclass
class Booking:
    id: str  # noqa: A003 VNE003
    reference: str
    outboundFlightId: str


@dataclass
class Payment:
    receipt: str
    amount: int


@dataclass
class LoyaltyPoint:
    customerId: str
    booking: Booking
    payment: Payment
    points: int = 0
    tier: str = LoyaltyTier.BRONZE.value
    status: str = PointStatus.ACTIVE.value
    increment: bool = True
    expireAt: int = field(default_factory=create_loyalty_expiration_epoch)


@dataclass
class LoyaltyPointAggregate:
    total_points: int
    tier: str
    booking: str
    updatedAt: str = field(default_factory=datetime.datetime.utcnow().isoformat)
    increment: bool = True
