"""
API Key model for programmatic access.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class APIKey(Base):
    """API Key model for user authentication."""

    __tablename__ = "api_keys"

    # User relationship
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Key Information
    key = Column(String(255), unique=True, nullable=False, index=True)  # Hashed API key
    name = Column(String(255), nullable=False)  # User-friendly name
    prefix = Column(String(10), nullable=False, index=True)  # First 8 chars for identification

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)

    # Permissions
    scopes = Column(String, nullable=True)  # JSON array of permissions

    # Usage Tracking
    last_used_at = Column(String, nullable=True)
    usage_count = Column(Integer, default=0, nullable=False)

    # Rate Limiting
    rate_limit_per_minute = Column(Integer, default=60, nullable=False)

    # Expiration
    expires_at = Column(String, nullable=True)

    # Metadata
    metadata = Column(String, nullable=True)  # JSON

    # Relationships
    user = relationship("User", back_populates="api_keys")

    def __repr__(self) -> str:
        return f"APIKey(id={self.id}, name={self.name}, prefix={self.prefix}, active={self.is_active})"

    @property
    def is_expired(self) -> bool:
        """Check if API key is expired."""
        if not self.expires_at:
            return False
        from datetime import datetime
        return datetime.fromisoformat(self.expires_at) < datetime.utcnow()

    @property
    def is_valid(self) -> bool:
        """Check if API key is valid for use."""
        return self.is_active and not self.is_revoked and not self.is_expired
