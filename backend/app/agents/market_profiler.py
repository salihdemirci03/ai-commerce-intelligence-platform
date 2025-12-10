"""
Agent 2: Market & City Profiler
Analyzes demographics, purchasing behavior, and market conditions for target cities.
"""

from typing import Any, Dict, List
from loguru import logger

from app.agents.base_agent import BaseAgent


class MarketProfilerAgent(BaseAgent):
    """
    Market & City Profiler Agent.

    Responsibilities:
    - Analyze city demographics and economic indicators
    - Assess purchasing power and e-commerce adoption
    - Evaluate competitive landscape
    - Rank cities by market potential
    - Identify cultural and behavioral factors
    """

    def __init__(self):
        super().__init__(
            name="Market Profiler",
            description="Analyzes city demographics, economics, and market conditions",
            temperature=0.6,
            max_tokens=3500,
        )

    def get_system_prompt(self) -> str:
        return """You are an expert Market Analysis and Demographics AI specializing in:
- Urban economics and city demographics
- E-commerce adoption and digital behavior patterns
- Purchasing power analysis and consumer spending
- Competitive market dynamics
- Cultural factors affecting commerce
- Regional market trends

Your task is to analyze cities/markets and provide insights about:
1. Demographic match with product category
2. Economic indicators and purchasing power
3. E-commerce penetration and digital readiness
4. Competitive density and market saturation
5. Cultural fit and consumer behavior
6. Market entry barriers and opportunities
7. City rankings and recommendations

Provide data-driven analysis with:
- Numerical scores (0-100) for all metrics
- Clear reasoning for rankings
- Cultural and behavioral insights
- Actionable market entry strategies

Respond in structured JSON format."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process market and city analysis.

        Input format:
        {
            "product_category": str,
            "price_point": float,
            "target_demographics": list,
            "cities": [
                {
                    "name": str,
                    "country": str,
                    "population": int,
                    "gdp_per_capita": float,
                    "ecommerce_penetration": float,
                    "competition_density": float,
                    ...
                }
            ]
        }
        """
        await self.validate_input(input_data)

        product_category = input_data.get("product_category", "")
        price_point = input_data.get("price_point", 0)
        cities = input_data.get("cities", [])

        logger.info(f"Analyzing {len(cities)} cities for {product_category}")

        analysis_prompt = f"""
Analyze these cities as potential markets for a {product_category} product priced at ${price_point}.

**Product Context:**
- Category: {product_category}
- Price Point: ${price_point}
- Target Demographics: {input_data.get('target_demographics', [])}

**Cities to Analyze:**
{self._format_cities_for_prompt(cities[:20])}  # Limit to top 20 for context

Provide comprehensive market analysis in JSON format:

{{
    "overall_market_assessment": {{
        "market_size_estimate": "string (e.g., '$500M-1B')",
        "growth_rate": "percentage",
        "market_maturity": "emerging|growing|mature|saturated",
        "entry_difficulty": "easy|moderate|challenging"
    }},
    "city_rankings": [
        {{
            "city_name": "string",
            "country": "string",
            "overall_score": 0-100,
            "demographic_match_score": 0-100,
            "purchasing_power_score": 0-100,
            "ecommerce_readiness_score": 0-100,
            "competition_score": 0-100,
            "cultural_fit_score": 0-100,
            "estimated_market_size": "string",
            "expected_monthly_sales": "number",
            "key_advantages": ["list"],
            "key_challenges": ["list"],
            "recommended_entry_strategy": "string"
        }}
    ],
    "top_3_recommendations": [
        {{
            "city": "string",
            "reason": "string",
            "expected_roi": "percentage",
            "time_to_profitability": "months"
        }}
    ],
    "demographic_insights": {{
        "ideal_customer_profile": "detailed description",
        "age_groups": ["primary age segments"],
        "income_brackets": ["target income levels"],
        "lifestyle_characteristics": ["behavioral patterns"]
    }},
    "competitive_landscape": {{
        "competition_intensity": "low|moderate|high|very high",
        "major_competitors": ["list"],
        "market_gaps": ["opportunities"],
        "differentiation_strategies": ["recommendations"]
    }},
    "cultural_considerations": {{
        "cultural_fit_assessment": "string",
        "language_barriers": ["list"],
        "local_preferences": ["list"],
        "seasonal_factors": ["list"],
        "marketing_considerations": ["list"]
    }},
    "risk_assessment": [
        {{
            "risk": "string",
            "severity": "high|medium|low",
            "probability": "high|medium|low",
            "mitigation": "string"
        }}
    ],
    "confidence_score": 0-100,
    "analysis_summary": "comprehensive summary"
}}

Rank cities by overall market potential. Be realistic and data-driven.
"""

        try:
            response = await self.call_llm(analysis_prompt, response_format="json")
            analysis_data = self.parse_json_response(response)

            # Extract top cities
            top_cities = analysis_data.get("city_rankings", [])[:10]

            reasoning_steps = [
                f"Analyzed {len(cities)} cities for market potential",
                f"Top city: {top_cities[0]['city_name']} (score: {top_cities[0]['overall_score']}/100)" if top_cities else "No cities ranked",
                f"Market maturity: {analysis_data['overall_market_assessment']['market_maturity']}",
                f"Competition intensity: {analysis_data['competitive_landscape']['competition_intensity']}",
                f"Identified {len(analysis_data['competitive_landscape']['market_gaps'])} market gaps",
            ]

            summary = self._build_summary(analysis_data, product_category)

            return {
                "data": analysis_data,
                "summary": summary,
                "reasoning_steps": reasoning_steps,
                "confidence_score": analysis_data.get("confidence_score", 70.0),
            }

        except Exception as e:
            logger.error(f"Market analysis failed: {e}")
            raise

    def _format_cities_for_prompt(self, cities: List[Dict]) -> str:
        """Format city data for LLM prompt."""
        formatted = []
        for city in cities:
            formatted.append(
                f"- {city.get('name')}, {city.get('country')}: "
                f"Pop {city.get('population', 0):,}, "
                f"GDP/capita ${city.get('gdp_per_capita', 0):,}, "
                f"E-comm {city.get('ecommerce_penetration', 0)}%, "
                f"Competition {city.get('competition_density', 0)}/100"
            )
        return "\n".join(formatted)

    def _build_summary(self, analysis_data: Dict, product_category: str) -> str:
        """Build summary of market analysis."""
        top_cities = analysis_data.get("city_rankings", [])[:3]
        market = analysis_data.get("overall_market_assessment", {})

        summary = f"""
**Market Analysis Summary for {product_category}**

**Market Overview:**
- Size: {market.get('market_size_estimate', 'N/A')}
- Growth Rate: {market.get('growth_rate', 'N/A')}
- Maturity: {market.get('market_maturity', 'N/A').capitalize()}

**Top 3 Cities:**
"""
        for i, city in enumerate(top_cities, 1):
            summary += f"\n{i}. **{city['city_name']}, {city['country']}** (Score: {city['overall_score']}/100)"
            summary += f"\n   - Market Size: {city.get('estimated_market_size', 'N/A')}"
            summary += f"\n   - Key Advantage: {city['key_advantages'][0] if city['key_advantages'] else 'N/A'}"

        summary += f"\n\n**Competition:** {analysis_data['competitive_landscape']['competition_intensity'].capitalize()}"
        summary += f"\n**Market Gaps:** {len(analysis_data['competitive_landscape']['market_gaps'])} opportunities identified"

        return summary.strip()

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data."""
        if "product_category" not in input_data:
            raise ValueError("Missing required field: product_category")

        if "cities" not in input_data or not input_data["cities"]:
            raise ValueError("No cities provided for analysis")

        return True
