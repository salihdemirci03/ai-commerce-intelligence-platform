"""
Agent 3: Advertising Planner
Generates advertising strategies for Meta, Google, and TikTok platforms.
"""

from typing import Any, Dict
from loguru import logger

from app.agents.base_agent import BaseAgent


class AdvertisingPlannerAgent(BaseAgent):
    """
    Advertising Strategy Planner Agent.

    Responsibilities:
    - Generate platform-specific ad strategies (Meta, Google, TikTok)
    - Create ad copy variations
    - Define targeting parameters
    - Estimate budget allocation and ROI
    - Provide creative briefs
    """

    def __init__(self):
        super().__init__(
            name="Advertising Planner",
            description="Creates comprehensive advertising strategies across platforms",
            temperature=0.8,  # Higher for creative content
            max_tokens=4000,
        )

    def get_system_prompt(self) -> str:
        return """You are an expert Digital Advertising Strategist and Performance Marketing AI with expertise in:
- Meta Ads (Facebook, Instagram) campaign optimization
- Google Ads (Search, Display, Shopping) strategies
- TikTok Ads for viral product marketing
- Audience targeting and segmentation
- Ad copywriting and creative optimization
- Budget allocation and ROI optimization
- A/B testing strategies

Your task is to create comprehensive advertising plans including:
1. Platform selection and rationale
2. Target audience definitions
3. Ad copy variations (headlines, descriptions, CTAs)
4. Creative briefs for visuals/videos
5. Budget recommendations
6. Expected performance metrics (CTR, CPC, CPA, ROAS)
7. Testing and optimization strategies

Provide:
- Multiple ad copy variations for each platform
- Detailed targeting parameters
- Realistic budget estimates
- Data-driven performance predictions

Respond in structured JSON format with actionable strategies."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process advertising strategy planning.

        Input format:
        {
            "product_name": str,
            "product_category": str,
            "price": float,
            "target_city": str,
            "target_demographics": dict,
            "budget_range": {"min": float, "max": float},
            "campaign_objective": "awareness|consideration|conversion"
        }
        """
        await self.validate_input(input_data)

        product_name = input_data.get("product_name")
        category = input_data.get("product_category")
        price = input_data.get("price")
        city = input_data.get("target_city")
        budget = input_data.get("budget_range", {})

        logger.info(f"Creating advertising plan for {product_name}")

        analysis_prompt = f"""
Create a comprehensive advertising strategy for this product:

**Product Details:**
- Name: {product_name}
- Category: {category}
- Price: ${price}
- Target Market: {city}
- Target Demographics: {input_data.get('target_demographics', {})}
- Monthly Budget Range: ${budget.get('min', 1000)} - ${budget.get('max', 5000)}
- Campaign Objective: {input_data.get('campaign_objective', 'conversion')}

Create detailed advertising strategies in JSON format:

{{
    "platform_recommendations": [
        {{
            "platform": "Meta|Google|TikTok",
            "priority": "high|medium|low",
            "rationale": "why this platform is suitable",
            "budget_allocation_percentage": 0-100
        }}
    ],
    "meta_ads_strategy": {{
        "platforms": ["Facebook", "Instagram"],
        "campaign_objective": "string",
        "ad_formats": ["image", "video", "carousel", "collection"],
        "targeting": {{
            "age_range": "string",
            "gender": "all|male|female",
            "interests": ["list of interests"],
            "behaviors": ["list of behaviors"],
            "custom_audiences": ["lookalike", "website visitors", "engaged users"],
            "geographic": "city/region details"
        }},
        "ad_copy_variations": [
            {{
                "headline": "string (max 40 chars)",
                "primary_text": "string (max 125 chars)",
                "description": "string",
                "cta": "Shop Now|Learn More|Sign Up|etc"
            }}
        ],
        "creative_brief": {{
            "visual_style": "string",
            "key_elements": ["list"],
            "messaging_focus": "string",
            "video_concepts": ["list of ideas"]
        }},
        "estimated_performance": {{
            "cpm": "cost per mille",
            "cpc": "cost per click",
            "ctr": "click-through rate %",
            "cpa": "cost per acquisition",
            "roas": "return on ad spend",
            "expected_reach": "number"
        }}
    }},
    "google_ads_strategy": {{
        "campaign_types": ["Search", "Display", "Shopping", "Performance Max"],
        "targeting": {{
            "keywords": ["list of keywords"],
            "keyword_match_types": ["exact", "phrase", "broad"],
            "negative_keywords": ["list"],
            "audience_segments": ["list"],
            "placements": ["list for display"]
        }},
        "ad_copy_variations": [
            {{
                "headline_1": "string (max 30 chars)",
                "headline_2": "string (max 30 chars)",
                "headline_3": "string (max 30 chars)",
                "description_1": "string (max 90 chars)",
                "description_2": "string (max 90 chars)",
                "path": "url path"
            }}
        ],
        "estimated_performance": {{
            "avg_cpc": "cost per click",
            "ctr": "click-through rate %",
            "conversion_rate": "percentage",
            "cpa": "cost per acquisition",
            "roas": "return on ad spend"
        }}
    }},
    "tiktok_ads_strategy": {{
        "campaign_type": "Traffic|Conversions|App Installs",
        "targeting": {{
            "age_range": "string",
            "gender": "all|male|female",
            "interests": ["list"],
            "device_type": ["iOS", "Android"],
            "behavior": ["list"]
        }},
        "content_strategy": {{
            "video_styles": ["ugc", "product demo", "trending", "educational"],
            "hooks": ["list of opening hooks"],
            "storytelling_approaches": ["list"],
            "trending_sounds": "recommendation",
            "hashtag_strategy": ["list of hashtags"]
        }},
        "ad_concepts": [
            {{
                "concept": "string",
                "script_outline": "string",
                "key_message": "string",
                "cta": "string"
            }}
        ],
        "estimated_performance": {{
            "cpm": "cost per mille",
            "cpc": "cost per click",
            "ctr": "click-through rate %",
            "cpa": "cost per acquisition",
            "viral_potential": "low|medium|high"
        }}
    }},
    "budget_allocation": {{
        "total_monthly_budget": float,
        "meta_budget": float,
        "google_budget": float,
        "tiktok_budget": float,
        "testing_budget": float,
        "allocation_rationale": "string"
    }},
    "campaign_timeline": {{
        "phase_1_testing": "duration and goals",
        "phase_2_scaling": "duration and goals",
        "phase_3_optimization": "duration and goals"
    }},
    "kpi_targets": {{
        "target_cpa": float,
        "target_roas": float,
        "target_monthly_sales": int,
        "target_revenue": float
    }},
    "testing_strategy": {{
        "variables_to_test": ["list"],
        "ab_test_plan": ["list of tests"],
        "optimization_triggers": ["list"]
    }},
    "recommendations": ["list of key recommendations"],
    "confidence_score": 0-100
}}

Be creative with ad copy while maintaining professionalism. Provide realistic estimates based on industry benchmarks.
"""

        try:
            response = await self.call_llm(analysis_prompt, response_format="json")
            analysis_data = self.parse_json_response(response)

            platforms = [p["platform"] for p in analysis_data.get("platform_recommendations", [])]

            reasoning_steps = [
                f"Recommended platforms: {', '.join(platforms)}",
                f"Generated {len(analysis_data['meta_ads_strategy']['ad_copy_variations'])} Meta ad variations",
                f"Created {len(analysis_data['google_ads_strategy']['ad_copy_variations'])} Google ad variations",
                f"Budget allocation: {analysis_data['budget_allocation']['allocation_rationale']}",
                f"Expected ROAS: {analysis_data['kpi_targets']['target_roas']}",
            ]

            summary = self._build_summary(analysis_data, product_name)

            return {
                "data": analysis_data,
                "summary": summary,
                "reasoning_steps": reasoning_steps,
                "confidence_score": analysis_data.get("confidence_score", 80.0),
            }

        except Exception as e:
            logger.error(f"Advertising planning failed: {e}")
            raise

    def _build_summary(self, analysis_data: Dict, product_name: str) -> str:
        """Build summary of advertising strategy."""
        budget = analysis_data.get("budget_allocation", {})
        kpis = analysis_data.get("kpi_targets", {})

        summary = f"""
**Advertising Strategy for {product_name}**

**Budget Allocation:**
- Total Monthly: ${budget.get('total_monthly_budget', 0):,.2f}
- Meta Ads: ${budget.get('meta_budget', 0):,.2f}
- Google Ads: ${budget.get('google_budget', 0):,.2f}
- TikTok Ads: ${budget.get('tiktok_budget', 0):,.2f}

**Expected Performance:**
- Target ROAS: {kpis.get('target_roas', 0)}x
- Target CPA: ${kpis.get('target_cpa', 0)}
- Monthly Sales Target: {kpis.get('target_monthly_sales', 0):,} units
- Expected Revenue: ${kpis.get('target_revenue', 0):,.2f}

**Platform Priorities:**
"""
        for rec in analysis_data.get("platform_recommendations", [])[:3]:
            summary += f"\n- {rec['platform']}: {rec['priority'].upper()} priority - {rec['rationale']}"

        summary += f"\n\n**Key Recommendations:**\n"
        summary += "\n".join(f"• {rec}" for rec in analysis_data.get("recommendations", [])[:3])

        return summary.strip()

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data."""
        required = ["product_name", "product_category", "price"]
        for field in required:
            if field not in input_data:
                raise ValueError(f"Missing required field: {field}")
        return True
