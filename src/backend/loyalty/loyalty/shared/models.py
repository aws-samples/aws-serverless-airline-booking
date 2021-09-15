from dataclasses import dataclass, field
from enum import Enum
import datetime


class PointStatus(Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


class LoyaltyTier(Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"


@dataclass
class Booking:
    id: str
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


@dataclass
class LoyaltyPointAggregate:
    total_points: int
    tier: str
    booking: str
    updatedAt: datetime = field(default_factory=datetime.datetime.utcnow)
