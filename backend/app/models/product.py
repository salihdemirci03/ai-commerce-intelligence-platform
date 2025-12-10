"""
Product model for storing product information.
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


class ProductCategory(str, enum.Enum):
    """Product category enumeration."""

    ELECTRONICS = "electronics"
    FASHION = "fashion"
    HOME_GARDEN = "home_garden"
    BEAUTY_HEALTH = "beauty_health"
    SPORTS_OUTDOORS = "sports_outdoors"
    TOYS_GAMES = "toys_games"
    BOOKS_MEDIA = "books_media"
    FOOD_BEVERAGES = "food_beverages"
    AUTOMOTIVE = "automotive"
    JEWELRY = "jewelry"
    PET_SUPPLIES = "pet_supplies"
    OFFICE_SUPPLIES = "office_supplies"
    BABY_KIDS = "baby_kids"
    INDUSTRIAL = "industrial"
    OTHER = "other"


class Product(Base):
    """Product model."""

    __tablename__ = "products"

    # User relationship
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Basic Information
    name = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(Enum(ProductCategory), nullable=False, index=True)

    # Pricing
    base_price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)  # ISO 4217 currency code

    # Manufacturing
    production_method = Column(String(100), nullable=True)  # e.g., "FASON", "In-house", "Dropshipping"
    production_cost = Column(Float, nullable=True)
    production_time_days = Column(Float, nullable=True)

    # Physical attributes
    weight_kg = Column(Float, nullable=True)
    dimensions = Column(String(100), nullable=True)  # e.g., "30x20x10 cm"

    # Quality & Specifications
    quality_tier = Column(String(50), nullable=True)  # e.g., "Premium", "Standard", "Budget"
    specifications = Column(Text, nullable=True)  # JSON string
    materials = Column(String(500), nullable=True)

    # Sourcing
    supplier_info = Column(Text, nullable=True)
    country_of_origin = Column(String(100), nullable=True)

    # Images & Media
    image_urls = Column(Text, nullable=True)  # JSON array of URLs
    video_url = Column(String(500), nullable=True)

    # SEO & Marketing
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    sku = Column(String(100), nullable=True, unique=True, index=True)
    barcode = Column(String(100), nullable=True)

    # Additional metadata
    metadata = Column(Text, nullable=True)  # JSON string for flexible data

    # Relationships
    user = relationship("User", back_populates="products")
    forecasts = relationship(
        "Forecast",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"Product(id={self.id}, name={self.name}, category={self.category}, price={self.base_price})"
