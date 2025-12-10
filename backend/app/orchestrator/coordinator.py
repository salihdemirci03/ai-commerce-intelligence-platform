"""
Multi-Agent Orchestrator - Coordinates all AI agents to produce comprehensive forecasts.
"""

import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.product_analyst import ProductAnalystAgent
from app.agents.market_profiler import MarketProfilerAgent
from app.agents.advertising_planner import AdvertisingPlannerAgent
from app.agents.supply_chain_advisor import SupplyChainAdvisorAgent
from app.agents.sales_strategy_agent import SalesStrategyAgent
from app.models.forecast import Forecast, ForecastStatus
from app.models.agent_log import AgentLog, AgentType
from app.models.city import City
from app.models.product import Product
from app.core.forecast_engine import ForecastEngine


class AgentCoordinator:
    """
    Coordinates multiple AI agents to produce comprehensive market forecasts.

    Flow:
    1. Receive forecast request (product + target markets)
    2. Initialize all agents
    3. Execute agents in optimal order with dependencies
    4. Aggregate results
    5. Calculate final scores
    6. Save to database
    """

    def __init__(self, db: AsyncSession):
        self.db = db

        # Initialize agents
        self.product_analyst = ProductAnalystAgent()
        self.market_profiler = MarketProfilerAgent()
        self.advertising_planner = AdvertisingPlannerAgent()
        self.supply_chain_advisor = SupplyChainAdvisorAgent()
        self.sales_strategy = SalesStrategyAgent()

        # Initialize forecast engine
        self.forecast_engine = ForecastEngine()

        logger.info("AgentCoordinator initialized with 5 agents")

    async def create_forecast(
        self,
        product: Product,
        target_cities: List[City],
        user_id: uuid.UUID,
        forecast_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, Any]:
        """
        Create comprehensive forecast by coordinating all agents.

        Args:
            product: Product model instance
            target_cities: List of City model instances to analyze
            user_id: User ID requesting forecast
            forecast_id: Optional forecast ID (for updates)

        Returns:
            Complete forecast results dictionary
        """
        request_id = str(forecast_id or uuid.uuid4())
        logger.info(f"Starting forecast creation: {request_id}")

        start_time = datetime.utcnow()

        try:
            # Update forecast status to processing
            if forecast_id:
                forecast = await self._get_forecast(forecast_id)
                forecast.status = ForecastStatus.PROCESSING
                forecast.processing_started_at = start_time.isoformat()
                await self.db.commit()

            # Phase 1: Product Analysis (runs first)
            logger.info(f"[{request_id}] Phase 1: Product Analysis")
            product_result = await self._run_product_analysis(product, request_id)

            # Phase 2: Market Analysis (depends on product analysis)
            logger.info(f"[{request_id}] Phase 2: Market Analysis")
            market_result = await self._run_market_analysis(
                product, target_cities, product_result, request_id
            )

            # Phase 3: Parallel execution of remaining agents
            logger.info(f"[{request_id}] Phase 3: Parallel agent execution")
            advertising_result, supply_chain_result, sales_result = await asyncio.gather(
                self._run_advertising_planning(product, market_result, request_id),
                self._run_supply_chain_analysis(product, market_result, request_id),
                self._run_sales_strategy(product, market_result, request_id),
                return_exceptions=True,
            )

            # Handle potential errors from parallel execution
            results = {
                "advertising": advertising_result if not isinstance(advertising_result, Exception) else None,
                "supply_chain": supply_chain_result if not isinstance(supply_chain_result, Exception) else None,
                "sales": sales_result if not isinstance(sales_result, Exception) else None,
            }

            # Phase 4: Aggregate results and calculate final scores
            logger.info(f"[{request_id}] Phase 4: Aggregation & scoring")
            final_forecast = await self._aggregate_results(
                product_analysis=product_result,
                market_analysis=market_result,
                advertising_strategy=results["advertising"],
                supply_chain_strategy=results["supply_chain"],
                sales_strategy=results["sales"],
                product=product,
                target_cities=target_cities,
            )

            # Phase 5: Calculate metrics and save
            logger.info(f"[{request_id}] Phase 5: Calculate final metrics")
            final_scores = self.forecast_engine.calculate_forecast_scores(
                product_data=product_result.get("data", {}),
                market_data=market_result.get("data", {}),
                cities=target_cities,
            )

            final_forecast.update(final_scores)

            # Update processing time
            end_time = datetime.utcnow()
            processing_duration = (end_time - start_time).total_seconds()

            final_forecast["processing_completed_at"] = end_time.isoformat()
            final_forecast["processing_duration_seconds"] = processing_duration

            # Calculate total cost
            total_cost = sum([
                product_result.get("cost_usd", 0),
                market_result.get("cost_usd", 0),
                results["advertising"].get("cost_usd", 0) if results["advertising"] else 0,
                results["supply_chain"].get("cost_usd", 0) if results["supply_chain"] else 0,
                results["sales"].get("cost_usd", 0) if results["sales"] else 0,
            ])

            total_tokens = sum([
                product_result.get("tokens_used", 0),
                market_result.get("tokens_used", 0),
                results["advertising"].get("tokens_used", 0) if results["advertising"] else 0,
                results["supply_chain"].get("tokens_used", 0) if results["supply_chain"] else 0,
                results["sales"].get("tokens_used", 0) if results["sales"] else 0,
            ])

            final_forecast["cost_usd"] = total_cost
            final_forecast["tokens_used"] = total_tokens

            logger.info(
                f"[{request_id}] Forecast completed: "
                f"{processing_duration:.2f}s, ${total_cost:.4f}, {total_tokens} tokens"
            )

            return {
                "success": True,
                "forecast_id": request_id,
                "data": final_forecast,
            }

        except Exception as e:
            logger.error(f"[{request_id}] Forecast creation failed: {e}")

            # Update forecast status to failed
            if forecast_id:
                forecast = await self._get_forecast(forecast_id)
                forecast.status = ForecastStatus.FAILED
                forecast.error_message = str(e)
                await self.db.commit()

            return {
                "success": False,
                "forecast_id": request_id,
                "error": str(e),
            }

    async def _run_product_analysis(self, product: Product, request_id: str) -> Dict[str, Any]:
        """Run product analysis agent."""
        input_data = {
            "product_name": product.name,
            "description": product.description,
            "category": product.category.value,
            "base_price": product.base_price,
            "production_method": product.production_method,
            "specifications": product.specifications,
        }

        result = await self.product_analyst.execute(input_data)
        await self._log_agent_execution(request_id, AgentType.PRODUCT_ANALYST, result)

        return result.dict()

    async def _run_market_analysis(
        self,
        product: Product,
        cities: List[City],
        product_analysis: Dict,
        request_id: str,
    ) -> Dict[str, Any]:
        """Run market profiler agent."""
        # Convert city models to dicts
        cities_data = [
            {
                "name": city.name,
                "country": city.country,
                "population": city.population,
                "gdp_per_capita": city.gdp_per_capita,
                "purchasing_power_index": city.purchasing_power_index,
                "ecommerce_penetration": city.ecommerce_penetration,
                "competition_density": city.competition_density,
                "average_order_value": city.average_order_value,
                "internet_penetration": city.internet_penetration,
            }
            for city in cities
        ]

        input_data = {
            "product_category": product.category.value,
            "price_point": product.base_price,
            "target_demographics": product_analysis.get("data", {})
            .get("demand_analysis", {})
            .get("target_demographics", []),
            "cities": cities_data,
        }

        result = await self.market_profiler.execute(input_data)
        await self._log_agent_execution(request_id, AgentType.MARKET_PROFILER, result)

        return result.dict()

    async def _run_advertising_planning(
        self,
        product: Product,
        market_analysis: Dict,
        request_id: str,
    ) -> Dict[str, Any]:
        """Run advertising planner agent."""
        top_city = (
            market_analysis.get("data", {})
            .get("city_rankings", [{}])[0]
            .get("city_name", "N/A")
        )

        input_data = {
            "product_name": product.name,
            "product_category": product.category.value,
            "price": product.base_price,
            "target_city": top_city,
            "target_demographics": market_analysis.get("data", {}).get(
                "demographic_insights", {}
            ),
            "budget_range": {"min": 1000, "max": 5000},
            "campaign_objective": "conversion",
        }

        result = await self.advertising_planner.execute(input_data)
        await self._log_agent_execution(request_id, AgentType.ADVERTISING_PLANNER, result)

        return result.dict()

    async def _run_supply_chain_analysis(
        self,
        product: Product,
        market_analysis: Dict,
        request_id: str,
    ) -> Dict[str, Any]:
        """Run supply chain advisor agent."""
        input_data = {
            "product_name": product.name,
            "product_category": product.category.value,
            "specifications": product.specifications or {},
            "target_volume": 1000,
            "quality_requirements": "standard",
            "target_cost": product.base_price * 0.3,  # 30% COGS target
            "target_market": market_analysis.get("data", {})
            .get("city_rankings", [{}])[0]
            .get("city_name", "Global"),
        }

        result = await self.supply_chain_advisor.execute(input_data)
        await self._log_agent_execution(request_id, AgentType.SUPPLY_CHAIN_ADVISOR, result)

        return result.dict()

    async def _run_sales_strategy(
        self,
        product: Product,
        market_analysis: Dict,
        request_id: str,
    ) -> Dict[str, Any]:
        """Run sales strategy agent."""
        input_data = {
            "product_name": product.name,
            "price": product.base_price,
            "product_category": product.category.value,
            "target_audience": market_analysis.get("data", {}).get("demographic_insights", {}),
            "unique_selling_points": [],
            "competition_level": market_analysis.get("data", {})
            .get("competitive_landscape", {})
            .get("competition_intensity", "moderate"),
        }

        result = await self.sales_strategy.execute(input_data)
        await self._log_agent_execution(request_id, AgentType.SALES_STRATEGY, result)

        return result.dict()

    async def _aggregate_results(
        self,
        product_analysis: Dict,
        market_analysis: Dict,
        advertising_strategy: Optional[Dict],
        supply_chain_strategy: Optional[Dict],
        sales_strategy: Optional[Dict],
        product: Product,
        target_cities: List[City],
    ) -> Dict[str, Any]:
        """Aggregate all agent results into final forecast."""
        return {
            "product_analysis_summary": product_analysis.get("summary", ""),
            "product_analysis_data": product_analysis.get("data", {}),
            "market_analysis_summary": market_analysis.get("summary", ""),
            "market_analysis_data": market_analysis.get("data", {}),
            "advertising_strategy_summary": advertising_strategy.get("summary", "") if advertising_strategy else "",
            "advertising_strategy_data": advertising_strategy.get("data", {}) if advertising_strategy else {},
            "supply_chain_summary": supply_chain_strategy.get("summary", "") if supply_chain_strategy else "",
            "supply_chain_data": supply_chain_strategy.get("data", {}) if supply_chain_strategy else {},
            "sales_strategy_summary": sales_strategy.get("summary", "") if sales_strategy else "",
            "sales_strategy_data": sales_strategy.get("data", {}) if sales_strategy else {},
        }

    async def _log_agent_execution(
        self,
        forecast_id: str,
        agent_type: AgentType,
        result: Any,
    ) -> None:
        """Log agent execution to database."""
        try:
            log = AgentLog(
                forecast_id=uuid.UUID(forecast_id),
                agent_name=agent_type,
                status="completed" if result.success else "failed",
                is_successful=result.success,
                started_at=datetime.utcnow().isoformat(),
                completed_at=datetime.utcnow().isoformat(),
                execution_time_ms=result.execution_time_ms,
                output_data=str(result.data),
                summary=result.summary,
                tokens_used=result.tokens_used,
                cost_usd=result.cost_usd,
                error_message=result.error if hasattr(result, "error") else None,
            )
            self.db.add(log)
            await self.db.commit()
        except Exception as e:
            logger.error(f"Failed to log agent execution: {e}")

    async def _get_forecast(self, forecast_id: uuid.UUID) -> Forecast:
        """Get forecast by ID."""
        result = await self.db.get(Forecast, forecast_id)
        if not result:
            raise ValueError(f"Forecast not found: {forecast_id}")
        return result
