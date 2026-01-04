"""
Product API endpoints.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger

from app.db.session import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product_schemas import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
    ProductListResponse,
)
from app.api.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    request: ProductCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new product.
    """
    product = Product(
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        category=request.category,
        base_price=request.base_price,
        production_method=request.production_method,
        target_market=request.target_market,
    )

    db.add(product)
    await db.commit()
    await db.refresh(product)

    logger.info(f"Product created: {product.name} by user {current_user.email}")

    return product


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get product by ID.
    """
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.user_id == current_user.id
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


@router.get("/", response_model=ProductListResponse)
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List user's products.
    """
    query = select(Product).where(Product.user_id == current_user.id)

    if is_active is not None:
        query = query.where(Product.is_active == is_active)

    if category:
        query = query.where(Product.category == category)

    query = query.order_by(Product.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    products = list(result.scalars().all())

    total_query = select(func.count(Product.id)).where(Product.user_id == current_user.id)
    if is_active is not None:
        total_query = total_query.where(Product.is_active == is_active)
    if category:
        total_query = total_query.where(Product.category == category)

    total_result = await db.execute(total_query)
    total = total_result.scalar()

    return ProductListResponse(
        products=products,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    request: ProductUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update product.
    """
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.user_id == current_user.id
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    logger.info(f"Product updated: {product.name}")

    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete product.
    """
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.user_id == current_user.id
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    await db.delete(product)
    await db.commit()

    logger.info(f"Product deleted: {product.name}")

    return None
