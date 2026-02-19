from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class MLModelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    framework: str = Field(..., pattern="^(scikit-learn|tensorflow|pytorch|xgboost|lightgbm)$")
    version: str = Field(default="1.0.0", pattern="^\d+\.\d+\.\d+$")
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None


class MLModelCreate(MLModelBase):
    pass


class MLModelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    version: Optional[str] = Field(None, pattern="^\d+\.\d+\.\d+$")
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class MLModelResponse(MLModelBase):
    id: int
    model_type: Optional[str]
    file_size: Optional[int]
    is_active: bool
    usage_count: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class PredictionRequest(BaseModel):
    input_data: Dict[str, Any]


class PredictionResponse(BaseModel):
    id: int
    model_id: int
    input_data: str
    output_data: str
    prediction_time: Optional[float]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class PredictionResult(BaseModel):
    model_id: int
    model_name: str
    predictions: Any
    prediction_time: float
    timestamp: datetime


class ModelStatsResponse(BaseModel):
    model_info: MLModelResponse
    statistics: Dict[str, Any]
    recent_predictions: Optional[List[PredictionResponse]] = None
