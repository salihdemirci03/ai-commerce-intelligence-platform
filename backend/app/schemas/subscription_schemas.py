"""
Subscription-related Pydantic schemas.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class SubscriptionResponse(BaseModel):
    """Subscription data response."""
    id: UUID
    user_id: UUID
    stripe_subscription_id: Optional[str]
    plan_type: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    cancelled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CheckoutSessionRequest(BaseModel):
    """Stripe checkout session creation request."""
    plan_type: str


class CheckoutSessionResponse(BaseModel):
    """Stripe checkout session response."""
    checkout_url: str
    session_id: str


class SubscriptionCancelRequest(BaseModel):
    """Subscription cancellation request."""
    cancel_immediately: bool = False
