from dataclasses import dataclass
from typing import Type


@dataclass
class ProcessBookingModel:
    """Process Booking State Machine Input model

    Selection of important keys used across logging and tracing

    Parameters
    ----------
    customer_id: str
        Unique customer identifier, by default "UNDEFINED"
    booking_id: str
        Unique booking identifier, by default "UNDEFINED"
    charge_id: str
        Payment token identifier, by default "UNDEFINED"
    outbound_flight_id: str
        Unique flight identifier, by default "UNDEFINED"
    state_machine_execution_id: str
        Unique process booking state machine execution identifier, by default "UNDEFINED"
    """

    outbound_flight_id: str
    customer_id: str
    charge_id: str
    state_machine_execution_id: str
    booking_id: str


ProcessBookingState = Type[ProcessBookingModel]
