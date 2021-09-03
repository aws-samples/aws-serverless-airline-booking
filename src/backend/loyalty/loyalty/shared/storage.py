import datetime
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, cast

import boto3
from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError
from cyksuid import ksuid  # type: ignore
from loyalty.shared.models import LoyaltyPoint, LoyaltyTier
from mypy_boto3_dynamodb import service_resource
from mypy_boto3_dynamodb.type_defs import GetItemOutputTypeDef, UpdateItemOutputTypeDef

logger = Logger(child=True)


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
    def compute_aggregate_points(self, item: LoyaltyPoint, increment: bool = True):
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
        self.compute_aggregate_points(item=item, increment=True)

    def compute_aggregate_points(self, item: LoyaltyPoint, increment: bool = True):
        if increment:
            self.data[item.customerId].total_points += item.points
        else:
            self.data[item.customerId].total_points -= item.points

    def get_customer_tier_points(self, customer_id: str) -> Tuple[LoyaltyTier, int]:
        if customer_id in self.data:
            return (LoyaltyTier[self.data[customer_id].tier], self.data[customer_id].total_points)

        return LoyaltyTier.BRONZE, 0

    def __contains__(self, item):
        return item in self.data[item.customerId].transactions


class DynamoDBStorage(BaseStorage):
    def __init__(self, client: service_resource.Table) -> None:
        self.client = client

    def add(self, item: LoyaltyPoint):
        try:
            logger.debug(f"Adding Loyalty points into '{self.client.table_name}' table")
            self.client.put_item(Item=self.build_add_transaction_item(item))
        except ClientError:
            logger.exception(f"Failed to add loyalty points into '{self.client.table_name}' table")
            raise

    def compute_aggregate_points(self, item: LoyaltyPoint, increment: bool = True) -> int:
        composite_key = {
            "pk": f"CUSTOMER#{item.customerId}",
            "sk": f"AGGREGATE",
        }
        aggregate_expression = "+" if increment else "-"

        try:
            logger.debug(
                f"Adding aggregate points into '{self.client.table_name}' table with {aggregate_expression} expr"
            )
            ret: UpdateItemOutputTypeDef = self.client.update_item(
                Key=composite_key,  # type: ignore
                UpdateExpression=f"SET totalPoints = totalPoints {aggregate_expression} :incr",
                ExpressionAttributeValues={":incr": {"N": item.points}},
            )

        except ClientError:
            logger.exception(f"Failed to aggregate loyalty points into '{self.client.table_name}' table")
            raise

        return cast(int, ret["Attributes"]["totalPoints"])

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
            logger.debug(f"Fetching '{customer_id}' aggregate points from '{self.client.table_name}' table")
            ret: GetItemOutputTypeDef = self.client.get_item(
                Key=composite_key, AttributesToGet=["total_points", "tier"]  # type: ignore
            )
            tier = cast(str, ret["Item"].get("tier", "BRONZE"))
            aggregate_points: int = cast(int, ret["Item"].get("total_points", 0))
        except ClientError:
            logger.exception(f"Failed to fetch '{customer_id}' aggregate points from '{self.client.table_name}' table")
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

    @classmethod
    def from_env(cls):
        table = os.getenv("TABLE_NAME", "")
        session = boto3.Session()
        dynamodb = session.resource("dynamodb").Table(table)
        return cls(client=dynamodb)
