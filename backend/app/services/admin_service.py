from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models import User, MLModel, Prediction, AuditLog
from app.core.dependencies import get_current_admin
from app.schemas.user import UserResponse
from typing import List
from datetime import datetime, timedelta


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        result = await self.db.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def get_user_stats(self) -> dict:
        result = await self.db.execute(
            select(func.count(User.id))
        )
        total_users = result.scalar()
        
        result = await self.db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        active_users = result.scalar()
        
        return {"total_users": total_users, "active_users": active_users}
    
    async def get_model_stats(self) -> dict:
        result = await self.db.execute(
            select(func.count(MLModel.id))
        )
        total_models = result.scalar()
        
        result = await self.db.execute(
            select(func.sum(MLModel.usage_count))
        )
        total_predictions = result.scalar() or 0
        
        return {"total_models": total_models, "total_predictions": total_predictions}
    
    async def get_analytics(self, days: int = 30) -> dict:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            select(Prediction).where(Prediction.created_at >= start_date)
        )
        predictions = result.scalars().all()
        
        daily_predictions = {}
        for pred in predictions:
            date_key = pred.created_at.strftime("%Y-%m-%d")
            daily_predictions[date_key] = daily_predictions.get(date_key, 0) + 1
        
        avg_prediction_time = 0
        if predictions:
            total_time = sum(p.prediction_time or 0 for p in predictions)
            avg_prediction_time = total_time / len(predictions)
        
        result = await self.db.execute(
            select(Prediction.status, func.count(Prediction.id))
            .group_by(Prediction.status)
        )
        status_counts = {row[0]: row[1] for row in result.all()}
        
        return {
            "total_predictions": len(predictions),
            "daily_predictions": daily_predictions,
            "avg_prediction_time": avg_prediction_time,
            "status_counts": status_counts,
            "success_rate": status_counts.get("success", 0) / max(len(predictions), 1) * 100
        }
    
    async def get_audit_logs(
        self, 
        user_id: int = None, 
        action: str = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[AuditLog]:
        query = select(AuditLog).order_by(AuditLog.created_at.desc())
        
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if action:
            query = query.where(AuditLog.action == action)
        
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create_audit_log(
        self,
        user_id: int = None,
        action: str = None,
        resource_type: str = None,
        resource_id: int = None,
        details: dict = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> AuditLog:
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log
    
    async def toggle_user_active(self, user_id: int, active: bool) -> User:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.is_active = active
            await self.db.commit()
            await self.db.refresh(user)
        return user
