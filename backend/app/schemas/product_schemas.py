"""
Product-related Pydantic schemas.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class ProductCreateRequest(BaseModel):
    """Product creation request."""
    name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    category: str
    base_price: Decimal = Field(..., gt=0)
    production_method: Optional[str] = Field(None, pattern="^(self|fason|dropship|wholesale)$")
    target_market: Optional[str] = None


class ProductUpdateRequest(BaseModel):
    """Product update request."""
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    base_price: Optional[Decimal] = Field(None, gt=0)
    production_method: Optional[str] = Field(None, pattern="^(self|fason|dropship|wholesale)$")
    target_market: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    """Product data response."""
    id: UUID
    user_id: UUID
    name: str
    description: Optional[str]
    category: str
    base_price: Decimal
    production_method: Optional[str]
    target_market: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Product list response."""
    products: list[ProductResponse]
    total: int
    skip: int
    limit: int
