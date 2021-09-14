import datetime
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

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

from loyalty.shared.functions import calculate_aggregate_points


class BaseStorage(ABC):
    @abstractmethod
    def add(self, item: LoyaltyPoint) -> LoyaltyPoint:
        raise NotImplementedError()

    @abstractmethod
    def add_aggregate(self, items: LoyaltyPoint) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get_customer_tier_points(self, customer_id: str) -> Tuple[LoyaltyTier, int]:
        raise NotImplementedError()


class FakeStorage(BaseStorage):
    def __init__(self):
        self.data: Dict[str, List[LoyaltyPoint]] = {}
        self.aggregates: Dict[str, LoyaltyPointAggregate] = {}

    def add(self, item: LoyaltyPoint):
        item.points = item.payment["amount"]  # type: ignore
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
    def build_loyalty_point_list(event: DynamoDBStreamEvent) -> List[LoyaltyPoint]:
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
                    booking=booking,
                    payment=payment,
                    points=int(data.get("points").get_value),  # type: ignore
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
