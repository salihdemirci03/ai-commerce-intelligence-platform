"""
Payment model for tracking all financial transactions.
"""

import enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum, ForeignKey, String, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.deep_report import DeepReport


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentType(str, enum.Enum):
    """Payment type enumeration."""

    SUBSCRIPTION = "subscription"
    DEEP_REPORT = "deep_report"
    ADDON = "addon"
    CUSTOM = "custom"


class Payment(Base):
    """Payment transaction model."""

    __tablename__ = "payments"

    # User relationship
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Stripe Integration
    stripe_payment_intent_id = Column(String(255), unique=True, nullable=True, index=True)
    stripe_charge_id = Column(String(255), nullable=True, index=True)
    stripe_invoice_id = Column(String(255), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)

    # Payment Details
    payment_type = Column(Enum(PaymentType), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False, index=True)

    # Amount
    amount = Column(Float, nullable=False)  # In smallest currency unit (cents for USD)
    currency = Column(String(3), default="USD", nullable=False)
    amount_refunded = Column(Float, default=0, nullable=False)

    # Description
    description = Column(String(500), nullable=True)
    item_name = Column(String(255), nullable=True)

    # Payment Method
    payment_method_type = Column(String(50), nullable=True)  # card, bank_transfer, etc.
    payment_method_brand = Column(String(50), nullable=True)  # visa, mastercard, etc.
    payment_method_last4 = Column(String(4), nullable=True)

    # Timestamps
    paid_at = Column(String, nullable=True)
    refunded_at = Column(String, nullable=True)
    failed_at = Column(String, nullable=True)

    # Error Handling
    failure_code = Column(String(100), nullable=True)
    failure_message = Column(Text, nullable=True)

    # Receipt
    receipt_url = Column(String(500), nullable=True)
    invoice_pdf_url = Column(String(500), nullable=True)

    # Metadata
    metadata = Column(Text, nullable=True)  # JSON

    # Relationships
    user = relationship("User")
    deep_report = relationship("DeepReport", back_populates="payment", uselist=False)

    def __repr__(self) -> str:
        return f"Payment(id={self.id}, type={self.payment_type}, amount={self.amount/100:.2f}, status={self.status})"

    @property
    def amount_in_dollars(self) -> float:
        """Get amount in dollars (from cents)."""
        return self.amount / 100 if self.currency == "USD" else self.amount
