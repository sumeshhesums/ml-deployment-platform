# Import all schemas for easy importing
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    Token,
    TokenData,
    LoginRequest
)

from app.schemas.model import (
    MLModelBase,
    MLModelCreate,
    MLModelUpdate,
    MLModelResponse,
    PredictionRequest,
    PredictionResponse,
    PredictionResult,
    ModelStatsResponse
)
