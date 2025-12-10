"""
Agent 5: Sales Strategy Agent
Designs complete sales funnels and channel strategies.
"""

from typing import Any, Dict
from loguru import logger

from app.agents.base_agent import BaseAgent


class SalesStrategyAgent(BaseAgent):
    """
    Sales Strategy & Funnel Optimization Agent.

    Responsibilities:
    - Marketplace selection (Shopify, Amazon, Etsy, etc.)
    - Sales funnel design
    - Email marketing sequences
    - Upsell/downsell strategies
    - Customer journey mapping
    - Conversion optimization
    """

    def __init__(self):
        super().__init__(
            name="Sales Strategy Agent",
            description="Designs complete sales funnels and channel strategies",
            temperature=0.7,
            max_tokens=4000,
        )

    def get_system_prompt(self) -> str:
        return """You are an expert E-commerce Sales Strategy and Conversion Optimization AI with expertise in:
- Marketplace selection (Shopify, Amazon, Etsy, WooCommerce, etc.)
- Sales funnel design and optimization
- Email marketing automation and sequences
- Upselling and cross-selling strategies
- Landing page optimization
- Customer journey mapping
- Conversion rate optimization (CRO)
- Retention and lifecycle marketing

Your task is to create comprehensive sales strategies including:
1. Optimal marketplace/platform selection
2. Complete sales funnel architecture
3. Landing page structure and elements
4. Email sequence outlines
5. Upsell/downsell offers
6. Customer journey maps
7. Retention strategies
8. Conversion optimization tactics

Provide:
- Platform-specific recommendations
- Detailed funnel stages
- Email copy outlines
- Conversion benchmarks
- Testing strategies

Respond in structured JSON format with actionable strategies."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process sales strategy planning.

        Input format:
        {
            "product_name": str,
            "price": float,
            "product_category": str,
            "target_audience": dict,
            "unique_selling_points": list,
            "competition_level": str
        }
        """
        await self.validate_input(input_data)

        product = input_data.get("product_name")
        price = input_data.get("price")
        category = input_data.get("product_category")
        usps = input_data.get("unique_selling_points", [])

        logger.info(f"Creating sales strategy for {product}")

        analysis_prompt = f"""
Create a comprehensive sales and conversion strategy for:

**Product Details:**
- Name: {product}
- Category: {category}
- Price: ${price}
- USPs: {usps}
- Target Audience: {input_data.get('target_audience', {})}
- Competition: {input_data.get('competition_level', 'moderate')}

Provide detailed sales strategy in JSON:

{{
    "marketplace_recommendations": [
        {{
            "platform": "Shopify|Amazon|Etsy|WooCommerce|BigCommerce|etc",
            "priority": "primary|secondary|tertiary",
            "rationale": "why this platform",
            "setup_complexity": "easy|moderate|complex",
            "monthly_cost_estimate": float,
            "pros": ["list"],
            "cons": ["list"],
            "target_monthly_sales": int,
            "commission_structure": "details"
        }}
    ],
    "sales_funnel": {{
        "funnel_type": "direct|tripwire|value_ladder|webinar|etc",
        "stages": [
            {{
                "stage": "awareness|interest|consideration|purchase|retention",
                "objective": "string",
                "tactics": ["list"],
                "conversion_benchmark": "percentage",
                "optimization_tips": ["list"]
            }}
        ],
        "funnel_diagram": "text representation of flow"
    }},
    "landing_page_strategy": {{
        "page_type": "product|sales|squeeze|webinar|etc",
        "structure": {{
            "hero_section": {{
                "headline": "compelling headline",
                "subheadline": "supporting text",
                "cta_text": "button text",
                "visual_elements": ["list"]
            }},
            "sections": [
                {{
                    "section_name": "string",
                    "purpose": "string",
                    "key_elements": ["list"],
                    "copy_outline": "brief content guide"
                }}
            ],
            "trust_elements": ["testimonials", "guarantees", "badges", "etc"],
            "urgency_tactics": ["scarcity", "timer", "limited offer", "etc"]
        }},
        "mobile_optimization": ["key considerations"],
        "load_time_target": "seconds",
        "conversion_goal": "percentage"
    }},
    "email_marketing_sequences": {{
        "welcome_series": [
            {{
                "email_number": 1,
                "send_timing": "immediately|after X hours",
                "subject_line": "string",
                "key_message": "string",
                "cta": "string",
                "goal": "string"
            }}
        ],
        "abandoned_cart_series": [
            {{
                "email_number": 1,
                "send_timing": "string",
                "subject_line": "string",
                "offer": "discount|urgency|social_proof",
                "recovery_rate_target": "percentage"
            }}
        ],
        "post_purchase_series": [
            {{
                "email_number": 1,
                "send_timing": "string",
                "purpose": "thank_you|education|upsell|review_request",
                "content_focus": "string"
            }}
        ],
        "re_engagement_series": ["outline"]
    }},
    "upsell_downsell_strategy": {{
        "upsells": [
            {{
                "offer": "string",
                "price": float,
                "placement": "cart|checkout|post_purchase",
                "expected_take_rate": "percentage",
                "revenue_impact": "estimate"
            }}
        ],
        "downsells": [
            {{
                "offer": "string",
                "price": float,
                "trigger": "when to offer",
                "purpose": "string"
            }}
        ],
        "cross_sells": [
            {{
                "product": "string",
                "bundling_strategy": "string",
                "discount_structure": "string"
            }}
        ]
    }},
    "customer_journey_map": {{
        "stages": [
            {{
                "stage": "string",
                "touchpoints": ["list"],
                "customer_emotions": ["list"],
                "pain_points": ["list"],
                "opportunities": ["list"],
                "kpis": ["metrics to track"]
            }}
        ]
    }},
    "conversion_optimization": {{
        "quick_wins": ["list of immediate improvements"],
        "ab_test_priorities": [
            {{
                "element": "string",
                "variations": ["list"],
                "expected_impact": "high|medium|low",
                "implementation_effort": "easy|moderate|complex"
            }}
        ],
        "psychological_triggers": [
            {{
                "trigger": "scarcity|social_proof|authority|etc",
                "implementation": "how to use it",
                "placement": "where on page/funnel"
            }}
        ],
        "friction_reduction": ["list of ways to reduce friction"]
    }},
    "retention_strategy": {{
        "loyalty_program": "description",
        "referral_program": {{
            "structure": "string",
            "incentive": "string",
            "expected_viral_coefficient": float
        }},
        "content_marketing": ["strategies"],
        "community_building": ["tactics"],
        "ltv_optimization": ["strategies"]
    }},
    "metrics_and_kpis": {{
        "primary_metrics": [
            {{
                "metric": "string",
                "target": "number",
                "tracking_method": "string"
            }}
        ],
        "conversion_funnel_benchmarks": {{
            "visit_to_lead": "percentage",
            "lead_to_customer": "percentage",
            "overall_conversion": "percentage",
            "average_order_value": float,
            "customer_lifetime_value": float,
            "payback_period": "months"
        }}
    }},
    "implementation_roadmap": {{
        "phase_1": {{
            "duration": "timeframe",
            "focus": "string",
            "deliverables": ["list"]
        }},
        "phase_2": {{
            "duration": "timeframe",
            "focus": "string",
            "deliverables": ["list"]
        }},
        "phase_3": {{
            "duration": "timeframe",
            "focus": "string",
            "deliverables": ["list"]
        }}
    }},
    "recommendations": ["top recommendations"],
    "confidence_score": 0-100
}}

Be specific and actionable. Include realistic conversion benchmarks.
"""

        try:
            response = await self.call_llm(analysis_prompt, response_format="json")
            analysis_data = self.parse_json_response(response)

            primary_platform = next(
                (m["platform"] for m in analysis_data["marketplace_recommendations"] if m["priority"] == "primary"),
                "N/A"
            )

            reasoning_steps = [
                f"Primary marketplace: {primary_platform}",
                f"Funnel type: {analysis_data['sales_funnel']['funnel_type']}",
                f"Created {len(analysis_data['email_marketing_sequences']['welcome_series'])} welcome emails",
                f"Identified {len(analysis_data['upsell_downsell_strategy']['upsells'])} upsell opportunities",
                f"Target conversion rate: {analysis_data['metrics_and_kpis']['conversion_funnel_benchmarks']['overall_conversion']}",
            ]

            summary = self._build_summary(analysis_data, product)

            return {
                "data": analysis_data,
                "summary": summary,
                "reasoning_steps": reasoning_steps,
                "confidence_score": analysis_data.get("confidence_score", 80.0),
            }

        except Exception as e:
            logger.error(f"Sales strategy planning failed: {e}")
            raise

    def _build_summary(self, analysis_data: Dict, product: str) -> str:
        """Build summary of sales strategy."""
        marketplaces = analysis_data.get("marketplace_recommendations", [])
        primary = next((m for m in marketplaces if m["priority"] == "primary"), {})
        benchmarks = analysis_data.get("metrics_and_kpis", {}).get("conversion_funnel_benchmarks", {})

        summary = f"""
**Sales Strategy for {product}**

**Primary Marketplace:** {primary.get('platform', 'N/A')}
**Funnel Type:** {analysis_data.get('sales_funnel', {}).get('funnel_type', 'N/A').replace('_', ' ').title()}

**Expected Performance:**
- Overall Conversion Rate: {benchmarks.get('overall_conversion', 'N/A')}
- Average Order Value: ${benchmarks.get('average_order_value', 0)}
- Customer Lifetime Value: ${benchmarks.get('customer_lifetime_value', 0)}

**Email Sequences:**
- Welcome Series: {len(analysis_data.get('email_marketing_sequences', {}).get('welcome_series', []))} emails
- Abandoned Cart: {len(analysis_data.get('email_marketing_sequences', {}).get('abandoned_cart_series', []))} emails
- Post-Purchase: {len(analysis_data.get('email_marketing_sequences', {}).get('post_purchase_series', []))} emails

**Upsell Strategy:**
- {len(analysis_data.get('upsell_downsell_strategy', {}).get('upsells', []))} upsell offers identified
- {len(analysis_data.get('upsell_downsell_strategy', {}).get('cross_sells', []))} cross-sell opportunities

**Top Recommendations:**
"""
        summary += "\n".join(f"• {rec}" for rec in analysis_data.get("recommendations", [])[:3])

        return summary.strip()

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data."""
        required = ["product_name", "price"]
        for field in required:
            if field not in input_data:
                raise ValueError(f"Missing required field: {field}")
        return True
