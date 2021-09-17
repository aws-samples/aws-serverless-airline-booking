import datetime
import calendar
import os
from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import Dict, List, Optional, Tuple, cast

import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes.dynamo_db_stream_event import (
    DynamoDBRecord,
    DynamoDBRecordEventName,
    DynamoDBStreamEvent,
)
from botocore.exceptions import ClientError
from cyksuid import ksuid
from mypy_boto3_dynamodb import service_resource
from mypy_boto3_dynamodb.type_defs import (
    GetItemInputTableTypeDef,
    GetItemOutputTypeDef,
    PutItemInputTableTypeDef,
    UpdateItemInputTableTypeDef,
)

from loyalty.shared.functions import calculate_aggregate_points
from loyalty.shared.models import Booking, LoyaltyPoint, LoyaltyPointAggregate, LoyaltyTier, Payment


class BaseStorage(ABC):
    @abstractmethod
    def add(self, item: LoyaltyPoint) -> None:
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def add_aggregate(self, items: Dict[str, LoyaltyPointAggregate]) -> None:
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def get_customer_tier_points(self, customer_id: str) -> Tuple[LoyaltyTier, int]:
        raise NotImplementedError()  # pragma: no cover


class FakeStorage(BaseStorage):
    def __init__(self):
        self.data: Dict[str, List[LoyaltyPoint]] = {}
        self.aggregates: Dict[str, LoyaltyPointAggregate] = {}

    def add(self, item: LoyaltyPoint) -> None:
        item.points = item.payment.amount
        if item.customerId in self.data:
            self.data[item.customerId].append(item)
        else:
            self.data[item.customerId] = [item]

        self.process_aggregate()  # mimic async aggregation

    def process_aggregate(self):
        for _, transactions in self.data.items():
            agg = calculate_aggregate_points(records=transactions)
            self.add_aggregate(items=agg)

    def add_aggregate(self, items: Dict[str, LoyaltyPointAggregate]) -> None:
        for customer_id, transaction in items.items():
            self.aggregates[customer_id] = transaction

    def get_customer_tier_points(self, customer_id: str) -> Tuple[LoyaltyTier, int]:
        if customer_id in self.aggregates:
            return (LoyaltyTier[self.aggregates[customer_id].tier], self.aggregates[customer_id].total_points)

        return LoyaltyTier.BRONZE, 0

    def __contains__(self, item):
        return item in self.data[item.customerId]


class DynamoDBStorage(BaseStorage):
    DYNAMODB_BATCH_WRITE_ITEM_LIMIT = 25
    MAX_THREADS = 4

    def __init__(self, client: service_resource.Table, logger: Optional[Logger] = None) -> None:
        self.client = client
        self.logger = logger or Logger(child=True)

    # TODO:
    def add(self, item: LoyaltyPoint) -> None:
        """Add a single loyalty point transaction

        Parameters
        ----------
        item : LoyaltyPoint
            Loyalty Point to be added

        """
        try:
            self.logger.info("Adding loyalty points")
            self.client.put_item(**self.build_add_put_item_input(item))
            self.logger.info("Loyalty points added successfully")
        except ClientError:
            self.logger.exception("Unable to add loyalty points")
            raise

    def add_aggregate(self, items: Dict[str, LoyaltyPointAggregate]) -> None:
        """Update aggregate point to unique bookings

        Parameters
        ----------
        items : Dict[str, LoyaltyPointAggregate]
            Aggregate of Loyalty point per customer
        """
        transactions = self.build_add_aggregate_update_item_input(customers=items)
        self.logger.info(transactions)
        try:
            for transaction in transactions:
                self.logger.append_keys(
                    customer_id=transaction["Key"]["pk"].lstrip("CUSTOMER#"),  # type: ignore
                    booking_id=next(iter(transaction["ExpressionAttributeValues"][":booking"])),  # type: ignore
                )
                self.logger.debug("Adding aggregate points")
                self.client.update_item(**transaction)
                self.logger.info("Points and tier aggregated successfully")
        except self.client.meta.client.exceptions.ConditionalCheckFailedException:
            self.logger.info("Detected duplicate transaction; safely ignoring...")
        except self.client.meta.client.exceptions.ClientError:
            self.logger.exception("Unable to add aggregate transaction")
            raise

    def get_customer_tier_points(self, customer_id: str) -> Tuple[LoyaltyTier, int]:
        """Get aggregate points and loyalty tier from given customer id

        Parameters
        ----------
        customer_id : str
            Loyalty Customer ID

        Returns
        -------
        LoyaltyTier
            Customer loyalty tier
        int
            Aggregated loyalty points
        """
        try:
            self.logger.info("Fetching aggregate points")
            ret: GetItemOutputTypeDef = self.client.get_item(
                **self.build_get_loyalty_tier_points_get_item_input(customer_id)
            )
            self.logger.info("Fetched loyalty tier and aggregate points successfully")

            data: Dict[str, str] = cast(dict, ret.get("Item", {}))
            tier = data.get("tier", "BRONZE")
            aggregate_points = int(data.get("totalPoints", 0))
        except ClientError:
            self.logger.exception("Unable to fetch aggregate points")
            raise

        return LoyaltyTier[tier.upper()], aggregate_points

    @staticmethod
    def build_get_loyalty_tier_points_get_item_input(customer_id: str) -> GetItemInputTableTypeDef:
        return {
            "Key": {"pk": f"CUSTOMER#{customer_id}", "sk": "AGGREGATE"},
            "AttributesToGet": ["totalPoints", "tier"],
        }

    @staticmethod
    def build_add_put_item_input(item: LoyaltyPoint) -> PutItemInputTableTypeDef:
        sortable_id = ksuid.ksuid()
        ttl: datetime.datetime = sortable_id.datetime + datetime.timedelta(days=365)
        return {
            "Item": {
                "pk": f"CUSTOMER#{item.customerId}",
                "sk": f"TRANSACTION#{str(sortable_id)}",
                "outboundFlightId": item.booking.outboundFlightId,
                "points": item.payment.amount,
                "status": item.status,
                "bookingDetails": asdict(item.booking),
                "paymentDetails": asdict(item.payment),
                "createdAt": calendar.timegm(ttl.timetuple()),
            }
        }

    @staticmethod
    def build_add_aggregate_update_item_input(
        customers: Dict[str, LoyaltyPointAggregate]
    ) -> List[UpdateItemInputTableTypeDef]:
        """Builds a list of conditional loyalty transaction updates for DynamoDB


        We use a set of bookings for idempotency,
        and ADD operation to take into account increment/decrement

        Parameters
        ----------
        customers : Dict[str, LoyaltyPointAggregate]
            Dict of unique customers and their transactions

        Returns
        -------
        List[UpdateItemInputTableTypeDef]
            List of loyalty transactions to be updated in DynamoDB
        """
        transactions = []
        for customer, transaction in customers.items():
            input_item: UpdateItemInputTableTypeDef = {
                "Key": {"pk": customer, "sk": "AGGREGATE"},
                "UpdateExpression": "ADD totalPoints :incr, bookings :booking SET tier = :tier, updatedAt = :timestamp",  # noqa: E501
                "ExpressionAttributeValues": {
                    ":incr": transaction.total_points,
                    ":booking": {transaction.booking},
                    ":tier": transaction.tier,
                    ":timestamp": str(transaction.updatedAt),
                },
            }
            if transaction.increment:
                # Only update aggregate points if booking has not been processed before
                input_item["ConditionExpression"] = "not(contains(bookings, :booking))"

            transactions.append(input_item)

        return transactions

        # for customer, transaction in customers.items()

    @staticmethod
    def build_loyalty_point_list(event: DynamoDBStreamEvent) -> List[LoyaltyPoint]:
        """Convert DynamoDB Stream event into a list of loyalty transactions

        Parameters
        ----------
        event : DynamoDBStreamEvent
            DynamoDB Stream event

        Returns
        -------
        List[LoyaltyPoint]
            List of loyalty transactions
        """
        aggregates = []
        for record in event.records:
            if DynamoDBStorage.detect_run_away_transaction(record):
                continue

            if record.event_name == DynamoDBRecordEventName.REMOVE:
                data = record.dynamodb.old_image  # type: ignore
            else:
                data = record.dynamodb.new_image  # type: ignore

            booking: Dict = {k: v.get_value for k, v in data.get("bookingDetails").get_value.items()}  # type: ignore
            payment: Dict = {k: v.get_value for k, v in data.get("paymentDetails").get_value.items()}  # type: ignore
            aggregates.append(
                LoyaltyPoint(
                    customerId=data.get("pk").get_value,  # type: ignore
                    booking=Booking(**booking),
                    payment=Payment(**payment),
                    points=int(data.get("points").get_value),  # type: ignore
                    increment=record.event_name != DynamoDBRecordEventName.REMOVE,
                )
            )

        return aggregates

    @classmethod
    def from_env(cls, logger: Optional[Logger] = None) -> "DynamoDBStorage":
        """Factory to create DynamoDBStorage instance using `TABLE_NAME` env

        Parameters
        ----------
        logger : Optional[Logger], optional
            Logger, by default None

        Returns
        -------
        DynamoDBStorage
            Instance of DynamoDB Storage
        """
        table = os.getenv("LOYALTY_TABLE_NAME", "")
        session = boto3.Session()
        dynamodb = session.resource("dynamodb").Table(table)
        return cls(client=dynamodb, logger=logger)

    @staticmethod
    def detect_run_away_transaction(record: DynamoDBRecord) -> bool:
        """Detect whether is a Modify event or an admin call updating aggregate points

        Parameters
        ----------
        record : DynamoDBRecord
            DynamoDB Stream Event Record

        Returns
        -------
        bool
            Whether it's a runaway transaction
        """
        return (
            record.event_name == DynamoDBRecordEventName.MODIFY
            or "AGGREGATE" in record.dynamodb.keys.get("sk").get_value  # type: ignore
        )
