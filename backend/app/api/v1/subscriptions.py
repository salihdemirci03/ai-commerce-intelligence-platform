"""
Subscription API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.db.session import get_db
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.subscription_schemas import (
    SubscriptionResponse,
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    SubscriptionCancelRequest,
)
from app.api.dependencies import get_current_user

router = APIRouter()


@router.get("/current", response_model=SubscriptionResponse)
async def get_current_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's subscription.
    """
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )

    return subscription


@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create Stripe checkout session for subscription.
    """
    if request.plan_type not in ['basic', 'pro', 'master']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan type"
        )

    logger.info(f"Creating checkout session for user {current_user.email} with plan {request.plan_type}")

    return CheckoutSessionResponse(
        checkout_url="https://checkout.stripe.com/demo",
        session_id="cs_test_demo123",
    )


@router.post("/cancel")
async def cancel_subscription(
    request: SubscriptionCancelRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel user's subscription.
    """
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )

    if request.cancel_immediately:
        subscription.status = "cancelled"
    else:
        subscription.cancel_at_period_end = True

    await db.commit()

    logger.info(f"Subscription cancelled for user {current_user.email}")

    return {"message": "Subscription cancelled successfully"}


@router.get("/plans")
async def get_subscription_plans():
    """
    Get available subscription plans.
    """
    return {
        "plans": [
            {
                "id": "basic",
                "name": "Basic",
                "price": 29,
                "currency": "USD",
                "interval": "month",
                "features": [
                    "50 forecasts/month",
                    "Top 10 cities analyzed",
                    "Summary reports",
                    "Email support"
                ]
            },
            {
                "id": "pro",
                "name": "Pro",
                "price": 79,
                "currency": "USD",
                "interval": "month",
                "features": [
                    "250 forecasts/month",
                    "Top 50 cities analyzed",
                    "Detailed reports",
                    "API access",
                    "3 marketplace integrations",
                    "Priority support"
                ]
            },
            {
                "id": "master",
                "name": "Master",
                "price": 149,
                "currency": "USD",
                "interval": "month",
                "features": [
                    "Unlimited forecasts",
                    "All cities analyzed",
                    "Full analysis reports",
                    "API access",
                    "Unlimited marketplace integrations",
                    "Custom reports",
                    "Priority support",
                    "Dedicated account manager"
                ]
            }
        ]
    }
