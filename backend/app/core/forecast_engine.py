"""
Forecast Engine - Custom algorithms for demand scoring and market potential calculation.
"""

from typing import Any, Dict, List
import math

from loguru import logger

from app.models.city import City


class ForecastEngine:
    """
    Custom forecast engine with proprietary algorithms for:
    - Demand score calculation
    - Competition index
    - Profitability score
    - Market fit analysis
    - Risk assessment
    """

    def __init__(self):
        # Weights for overall score calculation
        self.weights = {
            "demand": 0.40,
            "profitability": 0.30,
            "competition": 0.20,
            "market_fit": 0.10,
        }

        logger.info("ForecastEngine initialized")

    def calculate_forecast_scores(
        self,
        product_data: Dict[str, Any],
        market_data: Dict[str, Any],
        cities: List[City],
    ) -> Dict[str, Any]:
        """
        Calculate all forecast scores and metrics.

        Args:
            product_data: Product analysis results
            market_data: Market analysis results
            cities: List of target cities

        Returns:
            Dictionary with all calculated scores
        """
        logger.info("Calculating forecast scores")

        # Extract key metrics
        product_demand_score = (
            product_data.get("demand_analysis", {}).get("demand_score", 50)
        )
        product_quality_score = (
            product_data.get("quality_assessment", {}).get("quality_score", 50)
        )
        market_fit_score = (
            product_data.get("market_fit", {}).get("market_fit_score", 50)
        )

        # Get top city from market analysis
        city_rankings = market_data.get("city_rankings", [])
        top_city = city_rankings[0] if city_rankings else {}

        # Calculate demand score (0-100)
        demand_score = self._calculate_demand_score(
            product_demand_score=product_demand_score,
            market_size=top_city.get("estimated_market_size", "medium"),
            ecommerce_readiness=top_city.get("ecommerce_readiness_score", 50),
            demographic_match=top_city.get("demographic_match_score", 50),
        )

        # Calculate competition index (0-100, higher = more competition)
        competition_index = self._calculate_competition_index(
            competition_score=top_city.get("competition_score", 50),
            market_maturity=market_data.get("overall_market_assessment", {}).get(
                "market_maturity", "mature"
            ),
        )

        # Calculate profitability score (0-100)
        profitability_score = self._calculate_profitability_score(
            purchasing_power=top_city.get("purchasing_power_score", 50),
            product_quality=product_quality_score,
            competition=competition_index,
        )

        # Calculate risk score (0-100, higher = more risk)
        risk_score = self._calculate_risk_score(
            competition_index=competition_index,
            market_maturity=market_data.get("overall_market_assessment", {}).get(
                "market_maturity", "mature"
            ),
            entry_difficulty=market_data.get("overall_market_assessment", {}).get(
                "entry_difficulty", "moderate"
            ),
        )

        # Calculate overall score
        overall_score = self._calculate_overall_score(
            demand_score=demand_score,
            profitability_score=profitability_score,
            competition_index=competition_index,
            market_fit_score=market_fit_score,
        )

        # Estimate sales and revenue
        sales_metrics = self._estimate_sales_metrics(
            demand_score=demand_score,
            market_size=top_city.get("estimated_market_size", "medium"),
            competition_index=competition_index,
        )

        # Pricing recommendations
        pricing = self._calculate_pricing_recommendations(
            base_price=product_data.get("pricing_analysis", {}).get(
                "optimal_price_range", "N/A"
            ),
            competition_pricing=top_city.get("average_competitor_price", 0),
            quality_tier=product_data.get("quality_assessment", {}).get("quality_tier", "standard"),
        )

        return {
            "demand_score": round(demand_score, 2),
            "competition_index": round(competition_index, 2),
            "profitability_score": round(profitability_score, 2),
            "market_fit_score": round(market_fit_score, 2),
            "risk_score": round(risk_score, 2),
            "overall_score": round(overall_score, 2),
            "expected_monthly_sales_volume": sales_metrics["monthly_volume"],
            "expected_annual_revenue": sales_metrics["annual_revenue"],
            "expected_profit_margin": sales_metrics["profit_margin"],
            "recommended_price": pricing["recommended_price"],
            "recommended_price_min": pricing["price_min"],
            "recommended_price_max": pricing["price_max"],
            "price_elasticity": pricing["elasticity"],
            "city_rankings": self._format_city_rankings(city_rankings),
        }

    def _calculate_demand_score(
        self,
        product_demand_score: float,
        market_size: str,
        ecommerce_readiness: float,
        demographic_match: float,
    ) -> float:
        """
        Calculate demand score using weighted combination.

        Formula:
        demand_score = (product_demand * 0.4) + (market_size_factor * 0.3) +
                       (ecommerce_readiness * 0.2) + (demographic_match * 0.1)
        """
        # Convert market size to numeric
        market_size_map = {
            "small": 30,
            "medium": 60,
            "large": 85,
            "very large": 95,
        }
        market_size_score = market_size_map.get(market_size.lower(), 60)

        demand = (
            product_demand_score * 0.4
            + market_size_score * 0.3
            + ecommerce_readiness * 0.2
            + demographic_match * 0.1
        )

        return min(100, max(0, demand))

    def _calculate_competition_index(
        self,
        competition_score: float,
        market_maturity: str,
    ) -> float:
        """
        Calculate competition intensity index.

        Higher score = more competition
        """
        # Maturity multiplier
        maturity_multiplier = {
            "emerging": 0.7,
            "growing": 0.85,
            "mature": 1.0,
            "saturated": 1.2,
        }

        multiplier = maturity_multiplier.get(market_maturity.lower(), 1.0)

        competition = competition_score * multiplier

        return min(100, max(0, competition))

    def _calculate_profitability_score(
        self,
        purchasing_power: float,
        product_quality: float,
        competition: float,
    ) -> float:
        """
        Calculate profitability potential.

        Formula considers:
        - Purchasing power of market
        - Product quality (higher quality = better margins)
        - Competition (inverse - less competition = higher margins)
        """
        # Inverse competition (less competition = better)
        competition_factor = 100 - competition

        profitability = (
            purchasing_power * 0.45
            + product_quality * 0.35
            + competition_factor * 0.20
        )

        return min(100, max(0, profitability))

    def _calculate_risk_score(
        self,
        competition_index: float,
        market_maturity: str,
        entry_difficulty: str,
    ) -> float:
        """
        Calculate market entry risk score.

        Higher score = more risk
        """
        # Base risk from competition
        risk = competition_index * 0.5

        # Maturity risk
        maturity_risk = {
            "emerging": 45,  # Higher risk but higher reward
            "growing": 25,
            "mature": 15,
            "saturated": 60,  # Very risky
        }
        risk += maturity_risk.get(market_maturity.lower(), 30) * 0.3

        # Entry difficulty
        entry_risk = {
            "easy": 10,
            "moderate": 30,
            "challenging": 60,
        }
        risk += entry_risk.get(entry_difficulty.lower(), 30) * 0.2

        return min(100, max(0, risk))

    def _calculate_overall_score(
        self,
        demand_score: float,
        profitability_score: float,
        competition_index: float,
        market_fit_score: float,
    ) -> float:
        """
        Calculate weighted overall market potential score.

        Uses configurable weights from self.weights
        """
        # Invert competition (lower competition = better score)
        competition_score = 100 - competition_index

        overall = (
            self.weights["demand"] * demand_score
            + self.weights["profitability"] * profitability_score
            + self.weights["competition"] * competition_score
            + self.weights["market_fit"] * market_fit_score
        )

        return min(100, max(0, overall))

    def _estimate_sales_metrics(
        self,
        demand_score: float,
        market_size: str,
        competition_index: float,
    ) -> Dict[str, Any]:
        """
        Estimate sales volume and revenue.

        This is a simplified model - in production, would use ML models
        trained on historical data.
        """
        # Base monthly volume by market size
        base_volume = {
            "small": 50,
            "medium": 200,
            "large": 800,
            "very large": 2000,
        }
        monthly_volume = base_volume.get(market_size.lower(), 200)

        # Adjust by demand score
        demand_multiplier = demand_score / 50  # Normalize to ~1.0

        # Adjust by competition (inverse)
        competition_multiplier = (100 - competition_index) / 50

        # Calculate adjusted volume
        adjusted_volume = int(monthly_volume * demand_multiplier * competition_multiplier)

        # Estimate revenue (assuming average price $50)
        avg_price = 50
        monthly_revenue = adjusted_volume * avg_price
        annual_revenue = monthly_revenue * 12

        # Estimate profit margin based on competition
        base_margin = 40  # 40% base
        margin_adjustment = (100 - competition_index) * 0.2  # Up to 20% adjustment
        profit_margin = min(70, max(15, base_margin + margin_adjustment))

        return {
            "monthly_volume": adjusted_volume,
            "annual_revenue": round(annual_revenue, 2),
            "profit_margin": round(profit_margin, 2),
        }

    def _calculate_pricing_recommendations(
        self,
        base_price: Any,
        competition_pricing: float,
        quality_tier: str,
    ) -> Dict[str, Any]:
        """
        Calculate optimal pricing recommendations.
        """
        # Quality tier multiplier
        quality_multipliers = {
            "premium": 1.3,
            "standard": 1.0,
            "budget": 0.7,
        }
        multiplier = quality_multipliers.get(quality_tier.lower(), 1.0)

        # Parse base price if it's a string range
        if isinstance(base_price, str) and "-" in base_price:
            try:
                parts = base_price.replace("$", "").split("-")
                price_min = float(parts[0].strip())
                price_max = float(parts[1].strip())
                recommended = (price_min + price_max) / 2
            except:
                recommended = 50  # Default
                price_min = 40
                price_max = 60
        else:
            recommended = float(base_price) if base_price else 50
            price_min = recommended * 0.8
            price_max = recommended * 1.2

        # Adjust by quality tier
        recommended *= multiplier
        price_min *= multiplier
        price_max *= multiplier

        # Price elasticity (simplified)
        if quality_tier == "premium":
            elasticity = "inelastic"
        elif quality_tier == "budget":
            elasticity = "elastic"
        else:
            elasticity = "neutral"

        return {
            "recommended_price": round(recommended, 2),
            "price_min": round(price_min, 2),
            "price_max": round(price_max, 2),
            "elasticity": elasticity,
        }

    def _format_city_rankings(self, city_rankings: List[Dict]) -> str:
        """Format city rankings as JSON string."""
        import json

        return json.dumps(city_rankings[:10])  # Top 10 cities
