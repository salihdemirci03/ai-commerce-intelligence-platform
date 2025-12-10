"""
Subscription model for user plan management.
"""

import enum
from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Column, Enum, ForeignKey, String, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class SubscriptionPlan(str, enum.Enum):
    """Subscription plan tiers."""

    BASIC = "basic"  # $29/month
    PRO = "pro"  # $79/month
    MASTER = "master"  # $149/month


class SubscriptionStatus(str, enum.Enum):
    """Subscription status."""

    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    UNPAID = "unpaid"


class Subscription(Base):
    """User subscription model."""

    __tablename__ = "subscriptions"

    # User relationship
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Stripe integration
    stripe_subscription_id = Column(String(255), unique=True, nullable=True, index=True)
    stripe_customer_id = Column(String(255), nullable=True, index=True)
    stripe_price_id = Column(String(255), nullable=True)

    # Plan details
    plan_type = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.BASIC, nullable=False)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False)

    # Billing period
    current_period_start = Column(DateTime, default=datetime.utcnow, nullable=False)
    current_period_end = Column(DateTime, nullable=True)

    # Trial
    trial_start = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)
    is_trial = Column(Boolean, default=False, nullable=False)

    # Cancellation
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    cancelled_at = Column(DateTime, nullable=True)

    # Usage limits (monthly)
    forecasts_limit = Column(Integer, nullable=False)  # Based on plan
    forecasts_used = Column(Integer, default=0, nullable=False)

    cities_limit = Column(Integer, nullable=False)  # Top N cities to analyze
    api_calls_limit = Column(Integer, nullable=False)
    api_calls_used = Column(Integer, default=0, nullable=False)

    # Metadata
    metadata = Column(String, nullable=True)  # JSON string for additional data

    # Relationships
    user = relationship("User", back_populates="subscriptions")

    def __repr__(self) -> str:
        return f"Subscription(id={self.id}, user_id={self.user_id}, plan={self.plan_type}, status={self.status})"

    @property
    def is_active(self) -> bool:
        """Check if subscription is active."""
        return self.status == SubscriptionStatus.ACTIVE

    @property
    def has_forecast_quota(self) -> bool:
        """Check if user has remaining forecast quota."""
        return self.forecasts_used < self.forecasts_limit

    def reset_monthly_usage(self) -> None:
        """Reset monthly usage counters."""
        self.forecasts_used = 0
        self.api_calls_used = 0
