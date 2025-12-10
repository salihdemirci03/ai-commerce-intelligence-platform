"""
Base model class with common fields and utilities.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr


class CustomBase:
    """Base class for all models with common fields."""

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower()

    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        index=True,
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def __repr__(self) -> str:
        """String representation of model."""
        attrs = ", ".join(
            f"{key}={value!r}"
            for key, value in self.to_dict().items()
            if key not in ["created_at", "updated_at"]
        )
        return f"{self.__class__.__name__}({attrs})"


Base = declarative_base(cls=CustomBase)
