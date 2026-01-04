"""
Admin API endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.forecast import Forecast
from app.models.product import Product
from app.models.subscription import Subscription
from app.api.dependencies import get_current_user

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Require admin role.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/stats")
async def get_platform_stats(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get platform statistics.
    """
    users_count = await db.execute(select(func.count(User.id)))
    active_users = await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    forecasts_count = await db.execute(select(func.count(Forecast.id)))
    products_count = await db.execute(select(func.count(Product.id)))
    subscriptions_count = await db.execute(
        select(func.count(Subscription.id)).where(Subscription.status == 'active')
    )

    return {
        "users": {
            "total": users_count.scalar(),
            "active": active_users.scalar(),
        },
        "forecasts": {
            "total": forecasts_count.scalar(),
        },
        "products": {
            "total": products_count.scalar(),
        },
        "subscriptions": {
            "active": subscriptions_count.scalar(),
        },
    }


@router.get("/users")
async def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    List all users (admin only).
    """
    result = await db.execute(
        select(User)
        .order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    users = list(result.scalars().all())

    total_result = await db.execute(select(func.count(User.id)))
    total = total_result.scalar()

    return {
        "users": [
            {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "role": user.role,
                "created_at": user.created_at.isoformat(),
            }
            for user in users
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Activate a user account.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = True
    await db.commit()

    logger.info(f"Admin {admin.email} activated user {user.email}")

    return {"message": "User activated successfully"}


@router.post("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Deactivate a user account.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate admin users"
        )

    user.is_active = False
    await db.commit()

    logger.info(f"Admin {admin.email} deactivated user {user.email}")

    return {"message": "User deactivated successfully"}
