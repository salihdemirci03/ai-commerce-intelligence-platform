"""
Agent log model for tracking AI agent executions.
"""

import enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum, ForeignKey, String, Integer, Float, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.forecast import Forecast


class AgentType(str, enum.Enum):
    """AI Agent types."""

    PRODUCT_ANALYST = "product_analyst"
    MARKET_PROFILER = "market_profiler"
    ADVERTISING_PLANNER = "advertising_planner"
    SUPPLY_CHAIN_ADVISOR = "supply_chain_advisor"
    SALES_STRATEGY = "sales_strategy"
    ORCHESTRATOR = "orchestrator"


class AgentLog(Base):
    """Agent execution log model."""

    __tablename__ = "agent_logs"

    # Relationships
    forecast_id = Column(UUID(as_uuid=True), ForeignKey("forecasts.id", ondelete="CASCADE"), nullable=False, index=True)

    # Agent Information
    agent_name = Column(Enum(AgentType), nullable=False, index=True)
    agent_version = Column(String(50), nullable=True)

    # Execution Status
    status = Column(String(50), nullable=False, default="started")  # started, completed, failed
    is_successful = Column(Boolean, default=False, nullable=False)
    error_message = Column(Text, nullable=True)

    # Timing
    started_at = Column(String, nullable=False)
    completed_at = Column(String, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)

    # Input Data
    input_data = Column(Text, nullable=True)  # JSON

    # Output Data
    output_data = Column(Text, nullable=True)  # JSON
    summary = Column(Text, nullable=True)  # Human-readable summary

    # AI Model Usage
    model_name = Column(String(100), nullable=True)  # e.g., "gpt-4-turbo"
    tokens_used = Column(Integer, nullable=True)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    cost_usd = Column(Float, nullable=True)

    # Chain of Thought
    reasoning_steps = Column(Text, nullable=True)  # JSON array of reasoning steps
    confidence_score = Column(Float, nullable=True)  # 0-100

    # Performance Metrics
    cache_hit = Column(Boolean, default=False, nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)

    # Metadata
    metadata = Column(Text, nullable=True)  # JSON

    # Relationships
    forecast = relationship("Forecast", back_populates="agent_logs")

    def __repr__(self) -> str:
        return f"AgentLog(id={self.id}, agent={self.agent_name}, status={self.status}, duration={self.execution_time_ms}ms)"
