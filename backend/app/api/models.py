from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.db.models import User, MLModel, Prediction
from app.schemas.model import (
    MLModelCreate, MLModelResponse, MLModelUpdate,
    PredictionRequest, PredictionResult, ModelStatsResponse, PredictionResponse,
    BatchPredictionRequest, BatchPredictionResult
)
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.services.model_service import ModelService
from typing import List
from datetime import datetime
import os
import json

router = APIRouter(prefix="/models", tags=["Models"])


@router.post("/upload", response_model=MLModelResponse, status_code=status.HTTP_201_CREATED)
async def upload_model(
    file: UploadFile = File(...),
    name: str = "Unnamed Model",
    description: str = None,
    framework: str = "scikit-learn",
    version: str = "1.0.0",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    model_service = ModelService(db)
    model = await model_service.upload_model(
        file=file,
        name=name,
        description=description,
        framework=framework,
        version=version,
        owner_id=current_user.id
    )
    return model


@router.get("", response_model=List[MLModelResponse])
async def list_models(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MLModel)
        .where(MLModel.owner_id == current_user.id)
        .order_by(MLModel.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    models = result.scalars().all()
    return models


@router.get("/{model_id}", response_model=MLModelResponse)
async def get_model(
    model_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MLModel).where(
            MLModel.id == model_id,
            MLModel.owner_id == current_user.id
        )
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.put("/{model_id}", response_model=MLModelResponse)
async def update_model(
    model_id: int,
    model_data: MLModelUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MLModel).where(
            MLModel.id == model_id,
            MLModel.owner_id == current_user.id
        )
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    update_data = model_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(model, key, value)
    
    await db.commit()
    await db.refresh(model)
    return model


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MLModel).where(
            MLModel.id == model_id,
            MLModel.owner_id == current_user.id
        )
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model_service = ModelService(db)
    await model_service.delete_model(model)
    return None


@router.post("/{model_id}/predict", response_model=PredictionResult)
async def predict(
    model_id: int,
    request: PredictionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MLModel).where(
            MLModel.id == model_id,
            MLModel.is_active == True
        )
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model_service = ModelService(db)
    prediction = await model_service.predict(model, request.input_data, current_user.id)
    return prediction


@router.post("/{model_id}/batch-predict", response_model=BatchPredictionResult)
async def batch_predict(
    model_id: int,
    request: BatchPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MLModel).where(
            MLModel.id == model_id,
            MLModel.is_active == True
        )
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model_service = ModelService(db)
    all_predictions = []
    total_time = 0.0
    
    for input_item in request.inputs:
        prediction = await model_service.predict(model, input_item, current_user.id)
        all_predictions.append(prediction.predictions)
        total_time += prediction.prediction_time
    
    return BatchPredictionResult(
        model_id=model_id,
        model_name=model.name,
        predictions=all_predictions,
        prediction_time=total_time,
        batch_size=len(request.inputs),
        timestamp=datetime.utcnow()
    )


@router.get("/{model_id}/stats", response_model=ModelStatsResponse)
async def get_model_stats(
    model_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MLModel).where(
            MLModel.id == model_id,
            MLModel.owner_id == current_user.id
        )
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    result = await db.execute(
        select(Prediction)
        .where(Prediction.model_id == model_id)
        .order_by(Prediction.created_at.desc())
        .limit(10)
    )
    recent_predictions = result.scalars().all()
    
    return {
        "model_info": model,
        "statistics": {
            "usage_count": model.usage_count,
            "total_predictions": len(recent_predictions),
            "upload_date": model.created_at
        },
        "recent_predictions": recent_predictions
    }


@router.get("/{model_id}/history", response_model=List[PredictionResponse])
async def get_prediction_history(
    model_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MLModel).where(
            MLModel.id == model_id,
            MLModel.owner_id == current_user.id
        )
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    result = await db.execute(
        select(Prediction)
        .where(Prediction.model_id == model_id)
        .order_by(Prediction.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    predictions = result.scalars().all()
    return predictions
