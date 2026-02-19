from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.models import User
from app.schemas.user import UserResponse
from app.schemas.model import PredictionResponse
from app.services.admin_service import AdminService
from app.core.dependencies import get_current_admin
from typing import List

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    admin_service = AdminService(db)
    return await admin_service.get_all_users(skip, limit)


@router.get("/stats")
async def get_system_stats(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    admin_service = AdminService(db)
    user_stats = await admin_service.get_user_stats()
    model_stats = await admin_service.get_model_stats()
    analytics = await admin_service.get_analytics()
    
    return {
        "users": user_stats,
        "models": model_stats,
        "analytics": analytics
    }


@router.get("/analytics")
async def get_analytics(
    days: int = 30,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    admin_service = AdminService(db)
    return await admin_service.get_analytics(days)


@router.get("/audit-logs")
async def get_audit_logs(
    user_id: int = None,
    action: str = None,
    skip: int = 0,
    limit: int = 100,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    admin_service = AdminService(db)
    logs = await admin_service.get_audit_logs(user_id, action, skip, limit)
    return logs


@router.post("/users/{user_id}/toggle")
async def toggle_user(
    user_id: int,
    active: bool,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    admin_service = AdminService(db)
    user = await admin_service.toggle_user_active(user_id, active)
    return {"status": "success", "user": user}
