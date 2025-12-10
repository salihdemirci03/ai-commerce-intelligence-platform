"""
Forecast model for storing prediction results.
"""

import enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum, ForeignKey, String, Float, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.product import Product
    from app.models.city import City
    from app.models.agent_log import AgentLog


class ForecastStatus(str, enum.Enum):
    """Forecast processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Forecast(Base):
    """Forecast prediction model."""

    __tablename__ = "forecasts"

    # Relationships
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    target_city_id = Column(UUID(as_uuid=True), ForeignKey("cities.id", ondelete="SET NULL"), nullable=True, index=True)

    # Status
    status = Column(Enum(ForecastStatus), default=ForecastStatus.PENDING, nullable=False, index=True)
    error_message = Column(Text, nullable=True)

    # Processing metadata
    processing_started_at = Column(String, nullable=True)
    processing_completed_at = Column(String, nullable=True)
    processing_duration_seconds = Column(Float, nullable=True)

    # Core Prediction Scores (0-100)
    demand_score = Column(Float, nullable=True, index=True)  # Overall demand potential
    competition_index = Column(Float, nullable=True)  # Competition intensity
    profitability_score = Column(Float, nullable=True, index=True)  # Profit potential
    market_fit_score = Column(Float, nullable=True)  # Product-market fit
    risk_score = Column(Float, nullable=True)  # Market entry risk

    # Final Recommendation Score (weighted combination)
    overall_score = Column(Float, nullable=True, index=True)

    # Sales Predictions
    expected_monthly_sales_volume = Column(Integer, nullable=True)
    expected_annual_revenue = Column(Float, nullable=True)  # USD
    expected_profit_margin = Column(Float, nullable=True)  # Percentage

    # Pricing Recommendations
    recommended_price = Column(Float, nullable=True)
    recommended_price_min = Column(Float, nullable=True)
    recommended_price_max = Column(Float, nullable=True)
    price_elasticity = Column(Float, nullable=True)

    # Market Analysis
    target_audience_size = Column(Integer, nullable=True)
    market_growth_rate = Column(Float, nullable=True)  # Percentage
    seasonal_factors = Column(Text, nullable=True)  # JSON

    # Competition Analysis
    competitor_count = Column(Integer, nullable=True)
    average_competitor_price = Column(Float, nullable=True)
    market_leader_price = Column(Float, nullable=True)
    competitive_advantages = Column(Text, nullable=True)  # JSON array

    # City Rankings (if multiple cities analyzed)
    city_rankings = Column(Text, nullable=True)  # JSON array of city scores

    # Agent Results Summary
    product_analysis_summary = Column(Text, nullable=True)  # From Agent 1
    market_analysis_summary = Column(Text, nullable=True)  # From Agent 2
    advertising_strategy_summary = Column(Text, nullable=True)  # From Agent 3
    supply_chain_summary = Column(Text, nullable=True)  # From Agent 4
    sales_strategy_summary = Column(Text, nullable=True)  # From Agent 5

    # Detailed Reports (JSON)
    product_analysis_data = Column(Text, nullable=True)
    market_analysis_data = Column(Text, nullable=True)
    advertising_strategy_data = Column(Text, nullable=True)
    supply_chain_data = Column(Text, nullable=True)
    sales_strategy_data = Column(Text, nullable=True)

    # Recommendations
    top_recommendations = Column(Text, nullable=True)  # JSON array
    action_items = Column(Text, nullable=True)  # JSON array
    warnings = Column(Text, nullable=True)  # JSON array

    # AI Model Info
    model_version = Column(String(50), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    cost_usd = Column(Float, nullable=True)

    # Metadata
    metadata = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="forecasts")
    product = relationship("Product", back_populates="forecasts")
    city = relationship("City", back_populates="forecasts")
    agent_logs = relationship(
        "AgentLog",
        back_populates="forecast",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    deep_reports = relationship(
        "DeepReport",
        back_populates="forecast",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"Forecast(id={self.id}, status={self.status}, overall_score={self.overall_score})"

    @property
    def is_completed(self) -> bool:
        """Check if forecast is completed."""
        return self.status == ForecastStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if forecast failed."""
        return self.status == ForecastStatus.FAILED

    def calculate_overall_score(self) -> float:
        """
        Calculate weighted overall score from individual metrics.
        """
        if not all([self.demand_score, self.competition_index, self.profitability_score]):
            return 0.0

        # Weights for different factors
        weights = {
            "demand": 0.40,
            "profitability": 0.30,
            "competition": 0.20,
            "market_fit": 0.10,
        }

        # Competition is inverse (lower is better)
        competition_score = 100 - self.competition_index

        score = (
            weights["demand"] * self.demand_score +
            weights["profitability"] * self.profitability_score +
            weights["competition"] * competition_score +
            weights["market_fit"] * (self.market_fit_score or 50)
        )

        return round(score, 2)
