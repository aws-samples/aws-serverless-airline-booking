from dataclasses import dataclass
from enum import Enum
from typing import TypedDict


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


@dataclass
class LoyaltyPointAggregate(LoyaltyPoint):
    increment: bool = True


class LoyaltyPointAggregateDynamoDB(TypedDict):
    pk: str
    sk: str
    total_points: int
    tier: str
    increment: bool
    updatedAt: str
    bookingId: str
