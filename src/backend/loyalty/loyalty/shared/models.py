from dataclasses import dataclass
from enum import Enum
from typing import Optional


class PointStatus(Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


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
    status: str = PointStatus.ACTIVE.value
