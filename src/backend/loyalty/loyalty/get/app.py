from typing import Optional

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler.api_gateway import ApiGatewayResolver
from aws_lambda_powertools.logging import correlation_paths
from loyalty.shared.constants import LOYALTY_TIER_MIN_POINTS
from loyalty.shared.models import LoyaltyTier
from loyalty.shared.storage import BaseStorage, DynamoDBStorage

logger = Logger()
tracer = Tracer()
app = ApiGatewayResolver()


def calculate_next_tier_points(tier: LoyaltyTier, points: int) -> int:
    if tier == LoyaltyTier.BRONZE:
        return LOYALTY_TIER_MIN_POINTS["SILVER"] - points
    elif tier == LoyaltyTier.SILVER:
        return LOYALTY_TIER_MIN_POINTS["GOLD"] - points

    return 0


@app.get("/loyalty/<customer_id>")
@tracer.capture_method
def get_loyalty_points(customer_id: str, storage_client: Optional[BaseStorage] = None):
    tracer.put_annotation(key="CustomerId", value=customer_id)

    if storage_client is None:
        storage_client = DynamoDBStorage.from_env()

    tier, total_points = storage_client.get_customer_tier_points(customer_id=customer_id)
    remaining_points = calculate_next_tier_points(tier=tier, points=total_points)
    # TODO: Fix missing customer ID
    logger.info(
        "Retrieved and calculated points and tier successfully",
        extra={"customer_id": "", "tier": tier, "points": total_points, "next_tier": remaining_points},
    )

    return {
        "level": tier.value,
        "points": total_points,
        "remainingPoints": remaining_points,
    }


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
def lambda_handler(event, context):
    return app.resolve(event, context)
