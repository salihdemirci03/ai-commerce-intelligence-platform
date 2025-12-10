"""
Agent 4: Supply Chain & FASON Manufacturing Advisor
Provides manufacturing, sourcing, and logistics optimization strategies.
"""

from typing import Any, Dict
from loguru import logger

from app.agents.base_agent import BaseAgent


class SupplyChainAdvisorAgent(BaseAgent):
    """
    Supply Chain & Manufacturing Advisor Agent.

    Responsibilities:
    - FASON manufacturing recommendations
    - Supplier sourcing strategies
    - Cost optimization
    - Quality control planning
    - Logistics and fulfillment optimization
    """

    def __init__(self):
        super().__init__(
            name="Supply Chain Advisor",
            description="Optimizes manufacturing, sourcing, and logistics strategies",
            temperature=0.6,
            max_tokens=3500,
        )

    def get_system_prompt(self) -> str:
        return """You are an expert Supply Chain and Manufacturing Operations AI with deep knowledge of:
- FASON (contract manufacturing) and production methods
- Global sourcing and supplier selection
- Manufacturing cost optimization
- Quality control and assurance
- Logistics and fulfillment strategies
- Inventory management
- E-commerce supply chain best practices

Your task is to provide comprehensive supply chain strategies including:
1. Manufacturing method recommendations (in-house, FASON, dropshipping, hybrid)
2. Supplier sourcing strategies with regional recommendations
3. Cost breakdowns and optimization opportunities
4. Lead time estimates and production planning
5. Quality control requirements and protocols
6. Packaging and shipping optimization
7. Inventory management strategies

Provide:
- Detailed cost analysis
- Specific supplier recommendations
- Risk mitigation strategies
- Scalability considerations

Respond in structured JSON format with actionable insights."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process supply chain analysis.

        Input format:
        {
            "product_name": str,
            "product_category": str,
            "specifications": dict,
            "target_volume": int,
            "quality_requirements": str,
            "target_cost": float,
            "target_market": str
        }
        """
        await self.validate_input(input_data)

        product = input_data.get("product_name")
        category = input_data.get("product_category")
        volume = input_data.get("target_volume", 1000)
        quality = input_data.get("quality_requirements", "standard")

        logger.info(f"Creating supply chain strategy for {product}")

        analysis_prompt = f"""
Create a comprehensive supply chain and manufacturing strategy:

**Product Information:**
- Name: {product}
- Category: {category}
- Target Monthly Volume: {volume} units
- Quality Requirements: {quality}
- Specifications: {input_data.get('specifications', {})}
- Target Production Cost: ${input_data.get('target_cost', 0)}
- Target Market: {input_data.get('target_market', 'Global')}

Provide detailed supply chain analysis in JSON:

{{
    "manufacturing_recommendations": {{
        "primary_method": "in-house|fason|dropshipping|hybrid|print-on-demand",
        "method_rationale": "detailed explanation",
        "scalability_score": 0-100,
        "fason_suitability": {{
            "score": 0-100,
            "advantages": ["list"],
            "disadvantages": ["list"],
            "recommended_regions": ["list of countries/regions"]
        }}
    }},
    "supplier_recommendations": [
        {{
            "region": "string (e.g., 'China - Guangdong', 'Turkey - Istanbul')",
            "supplier_type": "manufacturer|wholesaler|distributor",
            "estimated_moq": "minimum order quantity",
            "unit_cost_range": "min-max USD",
            "lead_time_days": "number range",
            "quality_tier": "premium|standard|budget",
            "pros": ["list"],
            "cons": ["list"],
            "recommended": true|false
        }}
    ],
    "cost_analysis": {{
        "per_unit_breakdown": {{
            "raw_materials": float,
            "manufacturing": float,
            "quality_control": float,
            "packaging": float,
            "shipping_to_warehouse": float,
            "total_cogs": float
        }},
        "volume_pricing_tiers": [
            {{
                "volume_range": "string",
                "unit_cost": float,
                "total_cost": float
            }}
        ],
        "cost_optimization_opportunities": ["list of ways to reduce costs"]
    }},
    "quality_control": {{
        "inspection_protocol": "description",
        "quality_checkpoints": ["list"],
        "testing_requirements": ["list"],
        "defect_rate_target": "percentage",
        "certification_needed": ["list of certifications"],
        "qa_cost_per_unit": float
    }},
    "logistics_strategy": {{
        "shipping_methods": [
            {{
                "method": "air|sea|land|courier",
                "cost_per_unit": float,
                "transit_time_days": "range",
                "recommended_for": "string"
            }}
        ],
        "warehousing": {{
            "strategy": "fba|3pl|self-fulfillment|hybrid",
            "estimated_monthly_cost": float,
            "locations_recommended": ["list"]
        }},
        "packaging": {{
            "type": "description",
            "cost_per_unit": float,
            "sustainability_score": 0-100,
            "unboxing_experience": "premium|standard|basic"
        }},
        "last_mile_delivery": {{
            "partners": ["list"],
            "estimated_cost": float,
            "delivery_time": "string"
        }}
    }},
    "inventory_management": {{
        "recommended_strategy": "jit|bulk|hybrid",
        "initial_order_quantity": int,
        "reorder_point": int,
        "safety_stock": int,
        "turnover_target": "times per year",
        "storage_requirements": "description"
    }},
    "production_timeline": {{
        "sample_production": "days",
        "sample_approval": "days",
        "bulk_production": "days",
        "quality_inspection": "days",
        "shipping": "days",
        "total_lead_time": "days"
    }},
    "scalability_plan": {{
        "phase_1": "initial volume and strategy",
        "phase_2": "growth phase strategy",
        "phase_3": "scale phase strategy",
        "bottlenecks": ["potential issues"],
        "mitigation_strategies": ["solutions"]
    }},
    "risk_assessment": [
        {{
            "risk": "string",
            "probability": "high|medium|low",
            "impact": "high|medium|low",
            "mitigation": "string"
        }}
    ],
    "fason_specific_guidance": {{
        "finding_manufacturers": ["strategies"],
        "negotiation_tips": ["list"],
        "contract_essentials": ["list"],
        "payment_terms": "recommendations",
        "communication_best_practices": ["list"]
    }},
    "sustainability_considerations": {{
        "eco_friendly_options": ["list"],
        "carbon_footprint": "estimate",
        "sustainable_materials": ["alternatives"],
        "circular_economy_opportunities": ["list"]
    }},
    "recommendations": ["key actionable recommendations"],
    "confidence_score": 0-100
}}

Provide specific, actionable recommendations with realistic cost estimates.
"""

        try:
            response = await self.call_llm(analysis_prompt, response_format="json")
            analysis_data = self.parse_json_response(response)

            total_lead_time = analysis_data.get("production_timeline", {}).get("total_lead_time", "N/A")
            cogs = analysis_data.get("cost_analysis", {}).get("per_unit_breakdown", {}).get("total_cogs", 0)

            reasoning_steps = [
                f"Recommended manufacturing method: {analysis_data['manufacturing_recommendations']['primary_method']}",
                f"Identified {len(analysis_data['supplier_recommendations'])} potential suppliers",
                f"Estimated COGS: ${cogs:.2f} per unit",
                f"Total lead time: {total_lead_time} days",
                f"Found {len(analysis_data['cost_analysis']['cost_optimization_opportunities'])} cost optimization opportunities",
            ]

            summary = self._build_summary(analysis_data, product)

            return {
                "data": analysis_data,
                "summary": summary,
                "reasoning_steps": reasoning_steps,
                "confidence_score": analysis_data.get("confidence_score", 75.0),
            }

        except Exception as e:
            logger.error(f"Supply chain analysis failed: {e}")
            raise

    def _build_summary(self, analysis_data: Dict, product: str) -> str:
        """Build summary of supply chain strategy."""
        method = analysis_data.get("manufacturing_recommendations", {}).get("primary_method", "N/A")
        cogs = analysis_data.get("cost_analysis", {}).get("per_unit_breakdown", {}).get("total_cogs", 0)
        lead_time = analysis_data.get("production_timeline", {}).get("total_lead_time", "N/A")

        summary = f"""
**Supply Chain Strategy for {product}**

**Manufacturing Method:** {method.upper()}
**Cost of Goods Sold:** ${cogs:.2f} per unit
**Total Lead Time:** {lead_time} days

**Top Supplier Recommendations:**
"""
        suppliers = analysis_data.get("supplier_recommendations", [])[:3]
        for i, supplier in enumerate(suppliers, 1):
            summary += f"\n{i}. {supplier['region']} - ${supplier['unit_cost_range']} per unit, {supplier['lead_time_days']} days lead time"

        summary += f"\n\n**Logistics Strategy:** {analysis_data.get('logistics_strategy', {}).get('warehousing', {}).get('strategy', 'N/A')}"
        summary += f"\n**Quality Control:** {len(analysis_data.get('quality_control', {}).get('quality_checkpoints', []))} checkpoints defined"

        summary += f"\n\n**Key Recommendations:**\n"
        summary += "\n".join(f"• {rec}" for rec in analysis_data.get("recommendations", [])[:3])

        return summary.strip()

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data."""
        if "product_name" not in input_data:
            raise ValueError("Missing required field: product_name")
        return True
