"""
Forecast-related Pydantic schemas.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class ForecastCreateRequest(BaseModel):
    """Forecast creation request."""
    product_id: UUID
    max_cities: Optional[int] = Field(default=10, ge=1, le=100)
    target_cities: Optional[list[UUID]] = None


class ForecastResponse(BaseModel):
    """Forecast data response."""
    id: UUID
    user_id: UUID
    product_id: UUID
    target_city_id: Optional[UUID]
    demand_score: Optional[int]
    competition_index: Optional[int]
    profitability_score: Optional[int]
    expected_sales_volume: Optional[int]
    recommended_price: Optional[Decimal]
    confidence_level: Optional[Decimal]
    status: str
    error_message: Optional[str]
    processing_started_at: Optional[datetime]
    processing_completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ForecastListResponse(BaseModel):
    """Forecast list response."""
    forecasts: list[ForecastResponse]
    total: int
    skip: int
    limit: int
