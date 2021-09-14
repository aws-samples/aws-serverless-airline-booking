import datetime
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, cast

import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes.dynamo_db_stream_event import (
    DynamoDBRecord,
    DynamoDBRecordEventName,
    DynamoDBStreamEvent,
)
from botocore.exceptions import ClientError
from cyksuid import ksuid  # type: ignore
from loyalty.shared.models import LoyaltyPoint, LoyaltyPointAggregate, LoyaltyPointAggregateDynamoDB, LoyaltyTier
from mypy_boto3_dynamodb import service_resource
from mypy_boto3_dynamodb.type_defs import GetItemOutputTypeDef, UpdateItemOutputTypeDef


@dataclass
class FakeTransactions:
    transactions: List[LoyaltyPoint]
    total_points: int = 0
    tier: str = LoyaltyTier.BRONZE.value


class BaseStorage(ABC):
    @abstractmethod
    def add(self, item: LoyaltyPoint) -> LoyaltyPoint:
        raise NotImplementedError()

    @abstractmethod
    def add_aggregate(self, item: LoyaltyPoint) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get_customer_tier_points(self, customer_id: str) -> Tuple[LoyaltyTier, int]:
        raise NotImplementedError()


class FakeStorage(BaseStorage):
    def __init__(self):
        self.data: dict[str, FakeTransactions] = {}

    def add(self, item: LoyaltyPoint):
        item.points = item.payment["amount"]  # type: ignore
        if item.customerId in self.data:
            return self.data[item.customerId].transactions.append(item)

        self.data[item.customerId] = FakeTransactions(transactions=[item])
        self.add_aggregate(item=item, increment=True)

    def add_aggregate(self, items: Dict[str, LoyaltyPointAggregate]) -> None:
        for customer_id, transaction in items.items():
            self.data[customer_id] = transaction

    def get_customer_tier_points(self, customer_id: str) -> Tuple[LoyaltyTier, int]:
        if customer_id in self.data:
            return (LoyaltyTier[self.data[customer_id].tier], self.data[customer_id].total_points)

        return LoyaltyTier.BRONZE, 0

    def __contains__(self, item):
        return item in self.data[item.customerId].transactions


class DynamoDBStorage(BaseStorage):
    DYNAMODB_BATCH_WRITE_ITEM_LIMIT = 25
    MAX_THREADS = 4

    def __init__(self, client: service_resource.Table, logger: Optional[Logger] = None) -> None:
        self.client = client
        self.logger = logger or Logger(child=True)

    def add(self, item: LoyaltyPoint):
        try:
            self.logger.debug(f"Adding Loyalty points into '{self.client.table_name}' table")
            self.client.put_item(Item=self.build_add_transaction_item(item))
        except ClientError:
            self.logger.exception(f"Unable to add loyalty points into")
            raise

    def add_aggregate(self, items: Dict[str, LoyaltyPointAggregate]) -> None:
        batch = self.build_add_aggregate_transaction_item(customers=items)

        try:
            for transaction in batch:
                self.logger.append_keys(
                    customer_id=transaction["pk"],
                    increment=transaction["increment"],
                    booking_id=transaction["bookingId"],
                )
                self.logger.debug("Adding aggregate points")
                bookings = {transaction["bookingId"]}
                composite_key = {"pk": transaction["pk"], "sk": transaction["sk"]}
                self.client.update_item(
                    Key=composite_key,
                    UpdateExpression="ADD totalPoints :incr, bookings :bookings SET tier = :tier, updatedAt = :timestamp",
                    ExpressionAttributeValues={
                        ":incr": transaction["total_points"],
                        ":bookings": bookings,
                        ":tier": transaction["tier"],
                        ":timestamp": transaction["updatedAt"],
                        ":booking": transaction["bookingId"],
                    },
                    # Only update aggregate points if booking has not been processed before
                    ConditionExpression="not(contains(bookings, :booking))",
                )
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
        composite_key = {"pk": f"CUSTOMER#{customer_id}", "sk": "AGGREGATE"}
        try:
            self.logger.info(f"Fetching '{customer_id}' aggregate points")
            ret: GetItemOutputTypeDef = self.client.get_item(
                Key=composite_key, AttributesToGet=["totalPoints", "tier"]  # type: ignore
            )
            tier: str = ret["Item"].get("tier", "BRONZE")
            aggregate_points = int(ret["Item"].get("totalPoints", 0))
        except ClientError:
            self.logger.exception(f"Unable to fetch '{customer_id}' aggregate points")
            raise

        return LoyaltyTier[tier.upper()], aggregate_points

    @staticmethod
    def build_add_transaction_item(item: LoyaltyPoint) -> dict:
        return {
            "pk": f"CUSTOMER#{item.customerId}",
            "sk": f"TRANSACTION#{ksuid.ksuid().encoded.decode()}",
            "outboundFlightId": item.booking["outboundFlightId"],  # type: ignore
            "points": item.payment["amount"],  # type: ignore
            "status": item.status,
            "bookingDetails": item.booking,
            "paymentDetails": item.payment,
            # Convert ksuid time to utc?
            "createdAt": str(datetime.datetime.utcnow()),
        }

    @staticmethod
    def build_add_aggregate_transaction_item(
        customers: Dict[str, LoyaltyPointAggregate]
    ) -> List[LoyaltyPointAggregateDynamoDB]:
        return [
            {
                "pk": customer.customerId,
                "sk": "AGGREGATE",
                "total_points": customer.points,
                "tier": customer.tier,
                "increment": customer.increment,
                "updatedAt": str(datetime.datetime.utcnow()),
                "bookingId": customer.booking["id"].get_value,
            }
            for customer in customers.values()
        ]

    @staticmethod
    def build_loyalty_point_aggregate(event: DynamoDBStreamEvent) -> List[LoyaltyPointAggregate]:
        aggregates = []
        for record in event.records:
            if DynamoDBStorage.detect_run_away_transaction(record):
                continue

            if record.event_name == DynamoDBRecordEventName.REMOVE:
                data = record.dynamodb.old_image  # type: ignore
            else:
                data = record.dynamodb.new_image  # type: ignore
            aggregates.append(
                LoyaltyPointAggregate(
                    customerId=data.get("pk").get_value,  # type: ignore
                    booking=data.get("bookingDetails").get_value,  # type: ignore
                    payment=data.get("paymentDetails").get_value,  # type: ignore
                    points=int(data.get("points").get_value),  # type: ignore
                    increment=record.event_name != DynamoDBRecordEventName.REMOVE,
                )
            )

        return aggregates

    @classmethod
    def from_env(cls, logger: Optional[Logger] = None):
        table = os.getenv("TABLE_NAME", "")
        session = boto3.Session()
        dynamodb = session.resource("dynamodb").Table(table)
        return cls(client=dynamodb, logger=logger)

    @staticmethod
    def detect_run_away_transaction(record: DynamoDBRecord) -> bool:
        return (
            record.event_name == DynamoDBRecordEventName.MODIFY
            or "AGGREGATE" in record.dynamodb.keys.get("sk").get_value  # type: ignore
        )
