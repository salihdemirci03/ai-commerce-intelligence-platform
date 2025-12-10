"""
Forecast API endpoints.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.db.session import get_db
from app.models.forecast import Forecast, ForecastStatus
from app.models.product import Product
from app.models.city import City
from app.models.user import User
from app.orchestrator.coordinator import AgentCoordinator
from app.schemas.forecast_schemas import (
    ForecastCreateRequest,
    ForecastResponse,
    ForecastListResponse,
)
from app.api.dependencies import get_current_user

router = APIRouter()


@router.post("/create", response_model=ForecastResponse, status_code=status.HTTP_201_CREATED)
async def create_forecast(
    request: ForecastCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new forecast analysis.

    This endpoint:
    1. Validates user subscription quota
    2. Creates forecast record
    3. Fetches product and city data
    4. Initiates multi-agent analysis (async)
    5. Returns forecast ID for tracking
    """
    try:
        # Check user subscription quota
        # TODO: Implement subscription quota check

        # Get product
        product_result = await db.execute(
            select(Product).where(Product.id == request.product_id)
        )
        product = product_result.scalar_one_or_none()

        if not product or product.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # Get cities (limit to top N based on subscription)
        cities_query = select(City).limit(request.max_cities or 10)
        cities_result = await db.execute(cities_query)
        cities = list(cities_result.scalars().all())

        if not cities:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No cities available for analysis"
            )

        # Create forecast record
        forecast = Forecast(
            user_id=current_user.id,
            product_id=product.id,
            status=ForecastStatus.PENDING,
        )
        db.add(forecast)
        await db.commit()
        await db.refresh(forecast)

        logger.info(f"Created forecast {forecast.id} for user {current_user.id}")

        # Initialize coordinator and create forecast (async process)
        coordinator = AgentCoordinator(db)
        result = await coordinator.create_forecast(
            product=product,
            target_cities=cities,
            user_id=current_user.id,
            forecast_id=forecast.id,
        )

        # Update forecast with results
        if result["success"]:
            forecast_data = result["data"]

            forecast.status = ForecastStatus.COMPLETED
            forecast.demand_score = forecast_data.get("demand_score")
            forecast.competition_index = forecast_data.get("competition_index")
            forecast.profitability_score = forecast_data.get("profitability_score")
            forecast.market_fit_score = forecast_data.get("market_fit_score")
            forecast.overall_score = forecast_data.get("overall_score")
            forecast.expected_monthly_sales_volume = forecast_data.get("expected_monthly_sales_volume")
            forecast.expected_annual_revenue = forecast_data.get("expected_annual_revenue")
            forecast.recommended_price = forecast_data.get("recommended_price")
            forecast.processing_duration_seconds = forecast_data.get("processing_duration_seconds")
            forecast.tokens_used = forecast_data.get("tokens_used")
            forecast.cost_usd = forecast_data.get("cost_usd")

            # Store summaries
            forecast.product_analysis_summary = forecast_data.get("product_analysis_summary")
            forecast.market_analysis_summary = forecast_data.get("market_analysis_summary")
            forecast.advertising_strategy_summary = forecast_data.get("advertising_strategy_summary")
            forecast.supply_chain_summary = forecast_data.get("supply_chain_summary")
            forecast.sales_strategy_summary = forecast_data.get("sales_strategy_summary")

            await db.commit()
            await db.refresh(forecast)

        return ForecastResponse.from_orm(forecast)

    except Exception as e:
        logger.error(f"Forecast creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Forecast creation failed: {str(e)}"
        )


@router.get("/{forecast_id}", response_model=ForecastResponse)
async def get_forecast(
    forecast_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get forecast by ID."""
    result = await db.execute(
        select(Forecast).where(
            Forecast.id == forecast_id,
            Forecast.user_id == current_user.id
        )
    )
    forecast = result.scalar_one_or_none()

    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forecast not found"
        )

    return ForecastResponse.from_orm(forecast)


@router.get("/", response_model=ForecastListResponse)
async def list_forecasts(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's forecasts."""
    result = await db.execute(
        select(Forecast)
        .where(Forecast.user_id == current_user.id)
        .order_by(Forecast.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    forecasts = list(result.scalars().all())

    total_result = await db.execute(
        select(func.count(Forecast.id)).where(Forecast.user_id == current_user.id)
    )
    total = total_result.scalar()

    return ForecastListResponse(
        forecasts=[ForecastResponse.from_orm(f) for f in forecasts],
        total=total,
        skip=skip,
        limit=limit,
    )
