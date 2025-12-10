"""
User model for authentication and profile management.
"""

import enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Enum, String, Integer
from sqlalchemy.orm import relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.subscription import Subscription
    from app.models.forecast import Forecast
    from app.models.product import Product
    from app.models.api_key import APIKey


class UserRole(str, enum.Enum):
    """User role enumeration."""

    ADMIN = "admin"
    USER = "user"
    ENTERPRISE = "enterprise"


class User(Base):
    """User model."""

    __tablename__ = "users"

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # Profile
    full_name = Column(String(255), nullable=True)
    company_name = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)

    # Role & Status
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # OAuth
    oauth_provider = Column(String(50), nullable=True)  # google, github, etc.
    oauth_id = Column(String(255), nullable=True)

    # Profile Image
    avatar_url = Column(String(500), nullable=True)

    # Settings (JSON stored as text)
    preferences = Column(String, nullable=True)  # JSON string

    # Usage Tracking
    last_login_at = Column(String, nullable=True)
    login_count = Column(Integer, default=0, nullable=False)

    # Relationships
    subscriptions = relationship(
        "Subscription",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    products = relationship(
        "Product",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    forecasts = relationship(
        "Forecast",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    api_keys = relationship(
        "APIKey",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email}, role={self.role})"
