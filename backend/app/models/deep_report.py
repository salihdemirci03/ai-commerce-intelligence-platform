"""
Deep Report model for premium detailed analysis reports.
"""

import enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum, ForeignKey, String, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.forecast import Forecast
    from app.models.payment import Payment


class ReportType(str, enum.Enum):
    """Deep report types."""

    STANDARD = "standard"  # $10
    PREMIUM = "premium"  # $30
    ENTERPRISE = "enterprise"  # $50


class DeepReport(Base):
    """Premium deep analysis report model."""

    __tablename__ = "deep_reports"

    # Relationships
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    forecast_id = Column(UUID(as_uuid=True), ForeignKey("forecasts.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id", ondelete="SET NULL"), nullable=True, index=True)

    # Report Details
    report_type = Column(Enum(ReportType), nullable=False)
    price_paid = Column(Float, nullable=False)  # USD
    currency = Column(String(3), default="USD", nullable=False)

    # Report Data
    report_data = Column(Text, nullable=False)  # JSON with all analysis
    executive_summary = Column(Text, nullable=True)

    # Sections (detailed analysis)
    market_deep_dive = Column(Text, nullable=True)  # JSON
    competitor_analysis = Column(Text, nullable=True)  # JSON
    customer_personas = Column(Text, nullable=True)  # JSON
    pricing_strategy = Column(Text, nullable=True)  # JSON
    marketing_plan = Column(Text, nullable=True)  # JSON
    financial_projections = Column(Text, nullable=True)  # JSON
    risk_assessment = Column(Text, nullable=True)  # JSON
    action_plan = Column(Text, nullable=True)  # JSON

    # Visual Assets
    charts_data = Column(Text, nullable=True)  # JSON for chart configurations
    infographic_url = Column(String(500), nullable=True)

    # File Export
    pdf_url = Column(String(500), nullable=True)
    excel_url = Column(String(500), nullable=True)
    ppt_url = Column(String(500), nullable=True)

    # Generation Info
    generation_time_seconds = Column(Float, nullable=True)
    ai_model_used = Column(String(100), nullable=True)
    tokens_used = Column(Float, nullable=True)

    # Access Control
    download_count = Column(Float, default=0, nullable=False)
    last_accessed_at = Column(String, nullable=True)
    expires_at = Column(String, nullable=True)  # Optional expiration

    # Metadata
    metadata = Column(Text, nullable=True)

    # Relationships
    user = relationship("User")
    forecast = relationship("Forecast", back_populates="deep_reports")
    payment = relationship("Payment", back_populates="deep_report")

    def __repr__(self) -> str:
        return f"DeepReport(id={self.id}, type={self.report_type}, price={self.price_paid})"
