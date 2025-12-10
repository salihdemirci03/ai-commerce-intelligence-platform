"""
City model for storing demographic and economic data.
"""

from sqlalchemy import Column, String, Float, Integer, Text, Boolean
from sqlalchemy.orm import relationship

from app.models.base import Base


class City(Base):
    """City demographic and economic data model."""

    __tablename__ = "cities"

    # Location
    name = Column(String(255), nullable=False, index=True)
    country = Column(String(100), nullable=False, index=True)
    country_code = Column(String(3), nullable=False)  # ISO 3166-1 alpha-3
    region = Column(String(255), nullable=True)  # State, province, etc.
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Demographics
    population = Column(Integer, nullable=False, index=True)
    population_density = Column(Float, nullable=True)  # per km²
    median_age = Column(Float, nullable=True)
    age_distribution = Column(Text, nullable=True)  # JSON: {0-18: 25%, 19-35: 30%, ...}

    # Economic Data
    gdp_per_capita = Column(Float, nullable=True)  # USD
    purchasing_power_index = Column(Float, nullable=False, default=100.0)  # Baseline 100
    unemployment_rate = Column(Float, nullable=True)
    average_household_income = Column(Float, nullable=True)  # USD

    # E-commerce Behavior
    ecommerce_penetration = Column(Float, nullable=False, default=50.0)  # Percentage
    online_shopping_frequency = Column(String(50), nullable=True)  # weekly, monthly, etc.
    preferred_payment_methods = Column(Text, nullable=True)  # JSON array
    average_order_value = Column(Float, nullable=True)  # USD
    mobile_commerce_rate = Column(Float, nullable=True)  # Percentage

    # Market Characteristics
    competition_density = Column(Float, nullable=False, default=50.0)  # 0-100 scale
    market_saturation = Column(Float, nullable=True)  # 0-100 scale
    business_friendliness_score = Column(Float, nullable=True)  # 0-100 scale

    # Digital Infrastructure
    internet_penetration = Column(Float, nullable=True)  # Percentage
    average_internet_speed = Column(Float, nullable=True)  # Mbps
    smartphone_penetration = Column(Float, nullable=True)  # Percentage

    # Advertising Costs (estimated)
    facebook_cpm = Column(Float, nullable=True)  # Cost per mille
    google_cpc = Column(Float, nullable=True)  # Cost per click
    tiktok_cpm = Column(Float, nullable=True)

    # Logistics
    shipping_cost_index = Column(Float, nullable=True)  # Relative to baseline
    average_delivery_days = Column(Float, nullable=True)
    logistics_infrastructure_score = Column(Float, nullable=True)  # 0-100

    # Cultural Factors
    primary_language = Column(String(100), nullable=True)
    languages = Column(Text, nullable=True)  # JSON array
    cultural_notes = Column(Text, nullable=True)

    # Seasonality
    peak_shopping_months = Column(Text, nullable=True)  # JSON array
    major_holidays = Column(Text, nullable=True)  # JSON object

    # Data Quality
    data_completeness_score = Column(Float, nullable=False, default=75.0)  # 0-100
    last_data_update = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Additional metadata
    metadata = Column(Text, nullable=True)  # JSON for flexible data

    # Relationships
    forecasts = relationship(
        "Forecast",
        back_populates="city",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"City(id={self.id}, name={self.name}, country={self.country}, population={self.population:,})"

    @property
    def full_location(self) -> str:
        """Get full location string."""
        parts = [self.name]
        if self.region:
            parts.append(self.region)
        parts.append(self.country)
        return ", ".join(parts)

    @property
    def attractiveness_score(self) -> float:
        """
        Calculate overall market attractiveness (0-100).
        Weighted combination of key metrics.
        """
        weights = {
            "purchasing_power": 0.25,
            "ecommerce_penetration": 0.25,
            "population_density": 0.15,
            "competition": 0.20,
            "infrastructure": 0.15,
        }

        # Normalize competition (lower is better)
        competition_score = 100 - (self.competition_density or 50)

        # Calculate infrastructure score
        infrastructure_score = (
            (self.internet_penetration or 50) * 0.5 +
            (self.logistics_infrastructure_score or 50) * 0.5
        )

        # Population density score (log scale, capped)
        pop_density_score = min(100, (self.population_density or 100) / 10) if self.population_density else 50

        score = (
            weights["purchasing_power"] * (self.purchasing_power_index or 100) +
            weights["ecommerce_penetration"] * (self.ecommerce_penetration or 50) +
            weights["population_density"] * pop_density_score +
            weights["competition"] * competition_score +
            weights["infrastructure"] * infrastructure_score
        )

        return round(score, 2)
