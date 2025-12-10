"""
Agent 1: Product Analyst
Analyzes product characteristics, quality, demand potential, and market fit.
"""

from typing import Any, Dict
from loguru import logger

from app.agents.base_agent import BaseAgent


class ProductAnalystAgent(BaseAgent):
    """
    Product Analysis Agent.

    Responsibilities:
    - Analyze product category and classification
    - Assess quality tier and specifications
    - Evaluate production complexity
    - Estimate demand potential
    - Determine market fit score
    """

    def __init__(self):
        super().__init__(
            name="Product Analyst",
            description="Analyzes product characteristics, quality, and demand potential",
            temperature=0.7,
            max_tokens=3000,
        )

    def get_system_prompt(self) -> str:
        return """You are an expert Product Analyst AI with deep knowledge of:
- E-commerce product categorization and market dynamics
- Quality assessment and manufacturing processes
- FASON (contract manufacturing) production methods
- Consumer demand patterns and product-market fit
- Competitive product positioning

Your task is to analyze products and provide detailed insights about:
1. Product classification and category fit
2. Quality tier (Premium, Standard, Budget)
3. Production complexity and method recommendations
4. Demand potential scoring (0-100)
5. Market fit assessment
6. Unique selling propositions
7. Target customer segments

Always provide:
- Clear reasoning for your assessments
- Numerical scores with explanations
- Actionable insights
- Risk factors and considerations

Respond in JSON format with structured data."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process product analysis.

        Input expected format:
        {
            "product_name": str,
            "description": str,
            "category": str,
            "base_price": float,
            "production_method": str (optional),
            "specifications": dict (optional),
            "target_market": str (optional)
        }

        Returns:
            Analyzed product data with scores and insights
        """
        await self.validate_input(input_data)

        product_name = input_data.get("product_name", "Unknown")
        description = input_data.get("description", "")
        category = input_data.get("category", "")
        base_price = input_data.get("base_price", 0)
        production_method = input_data.get("production_method", "Not specified")
        specifications = input_data.get("specifications", {})

        logger.info(f"Analyzing product: {product_name}")

        # Build detailed analysis prompt
        analysis_prompt = f"""
Analyze this product comprehensively:

**Product Information:**
- Name: {product_name}
- Description: {description}
- Category: {category}
- Base Price: ${base_price}
- Production Method: {production_method}
- Specifications: {specifications}

Provide a detailed analysis in JSON format with this exact structure:

{{
    "product_classification": {{
        "primary_category": "string",
        "sub_category": "string",
        "product_type": "string",
        "market_segment": "premium|mid-tier|budget"
    }},
    "quality_assessment": {{
        "quality_tier": "premium|standard|budget",
        "quality_score": 0-100,
        "quality_indicators": ["list of quality factors"],
        "durability_rating": 0-100,
        "perceived_value": "high|medium|low"
    }},
    "demand_analysis": {{
        "demand_score": 0-100,
        "demand_trend": "rising|stable|declining",
        "seasonality": "high|moderate|low",
        "target_demographics": ["list of target groups"],
        "use_cases": ["list of primary use cases"],
        "demand_drivers": ["list of factors driving demand"]
    }},
    "production_analysis": {{
        "production_complexity": "simple|moderate|complex",
        "recommended_method": "in-house|fason|dropshipping|hybrid",
        "fason_suitability_score": 0-100,
        "estimated_production_cost_range": "min-max USD",
        "lead_time_estimate": "X-Y days",
        "quality_control_requirements": ["list of QC needs"]
    }},
    "market_fit": {{
        "market_fit_score": 0-100,
        "competitive_intensity": "low|medium|high",
        "differentiation_potential": 0-100,
        "unique_selling_points": ["list of USPs"],
        "positioning_strategy": "string"
    }},
    "pricing_analysis": {{
        "price_positioning": "premium|competitive|value",
        "price_elasticity": "elastic|neutral|inelastic",
        "optimal_price_range": "min-max USD",
        "profit_margin_potential": "percentage range"
    }},
    "risk_factors": [
        {{
            "risk": "string",
            "severity": "high|medium|low",
            "mitigation": "string"
        }}
    ],
    "opportunities": [
        "list of market opportunities"
    ],
    "recommendations": [
        "actionable recommendations"
    ],
    "confidence_score": 0-100,
    "reasoning": "detailed explanation of analysis"
}}

Be thorough, analytical, and data-driven in your assessment.
"""

        try:
            # Call LLM for analysis
            response = await self.call_llm(analysis_prompt, response_format="json")

            # Parse JSON response
            analysis_data = self.parse_json_response(response)

            # Extract reasoning steps
            reasoning_steps = [
                f"Classified product as {analysis_data['product_classification']['primary_category']}",
                f"Quality assessed as {analysis_data['quality_assessment']['quality_tier']} tier",
                f"Demand score calculated: {analysis_data['demand_analysis']['demand_score']}/100",
                f"Production method recommended: {analysis_data['production_analysis']['recommended_method']}",
                f"Market fit score: {analysis_data['market_fit']['market_fit_score']}/100",
            ]

            # Build summary
            summary = self._build_summary(analysis_data, product_name)

            return {
                "data": analysis_data,
                "summary": summary,
                "reasoning_steps": reasoning_steps,
                "confidence_score": analysis_data.get("confidence_score", 75.0),
            }

        except Exception as e:
            logger.error(f"Product analysis failed: {e}")
            raise

    def _build_summary(self, analysis_data: Dict[str, Any], product_name: str) -> str:
        """Build human-readable summary of analysis."""

        quality = analysis_data.get("quality_assessment", {}).get("quality_tier", "unknown")
        demand_score = analysis_data.get("demand_analysis", {}).get("demand_score", 0)
        market_fit = analysis_data.get("market_fit", {}).get("market_fit_score", 0)
        production = analysis_data.get("production_analysis", {}).get("recommended_method", "unknown")

        summary = f"""
**Product Analysis Summary: {product_name}**

**Quality:** {quality.capitalize()} tier product with strong characteristics
**Demand Potential:** {demand_score}/100 - {"High" if demand_score >= 70 else "Moderate" if demand_score >= 40 else "Low"} demand expected
**Market Fit:** {market_fit}/100 - {"Excellent" if market_fit >= 80 else "Good" if market_fit >= 60 else "Fair"} product-market alignment
**Production:** {production.upper()} recommended for optimal efficiency

**Key Insights:**
{chr(10).join(f"• {rec}" for rec in analysis_data.get("recommendations", [])[:3])}

**Opportunities:** {len(analysis_data.get("opportunities", []))} market opportunities identified
**Risks:** {len(analysis_data.get("risk_factors", []))} risk factors to address
""".strip()

        return summary

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate product input data."""
        required_fields = ["product_name"]

        for field in required_fields:
            if field not in input_data or not input_data[field]:
                raise ValueError(f"Missing required field: {field}")

        return True
