import os
import uuid
import joblib
import json
import time
import numpy as np
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import MLModel, Prediction, User
from app.schemas.model import MLModelResponse, PredictionResult
from app.core.config import settings
import pandas as pd


class ModelService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def upload_model(
        self,
        file: UploadFile,
        name: str,
        description: str,
        framework: str,
        version: str,
        owner_id: int
    ) -> MLModelResponse:
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1] if file.filename else ".joblib"
        file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{file_ext}")
        
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        file_size = len(contents)
        
        try:
            model = joblib.load(file_path)
            model_type = type(model).__name__
        except Exception:
            model_type = "Unknown"
        
        ml_model = MLModel(
            name=name,
            description=description,
            framework=framework,
            version=version,
            model_type=model_type,
            file_path=file_path,
            file_size=file_size,
            owner_id=owner_id
        )
        
        self.db.add(ml_model)
        await self.db.commit()
        await self.db.refresh(ml_model)
        
        return ml_model
    
    async def predict(
        self,
        model: MLModel,
        input_data: dict,
        user_id: int
    ) -> PredictionResult:
        start_time = time.time()
        
        try:
            loaded_model = joblib.load(model.file_path)
            
            if isinstance(input_data, dict):
                input_df = pd.DataFrame([input_data])
                predictions = loaded_model.predict(input_df)
            elif isinstance(input_data, list):
                input_array = np.array(input_data)
                if len(input_array.shape) == 1:
                    input_array = input_array.reshape(1, -1)
                predictions = loaded_model.predict(input_array)
            else:
                raise ValueError("Unsupported input format")
            
            prediction_time = time.time() - start_time
            predictions_list = predictions.tolist() if hasattr(predictions, 'tolist') else [predictions]
            
            prediction_record = Prediction(
                model_id=model.id,
                user_id=user_id,
                input_data=json.dumps(input_data),
                output_data=json.dumps(predictions_list),
                prediction_time=prediction_time,
                status="success"
            )
            
            model.usage_count += 1
            
            await self.db.commit()
            
            return PredictionResult(
                model_id=model.id,
                model_name=model.name,
                predictions=predictions_list,
                prediction_time=prediction_time,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            prediction_time = time.time() - start_time
            
            prediction_record = Prediction(
                model_id=model.id,
                user_id=user_id,
                input_data=json.dumps(input_data),
                output_data=str(e),
                prediction_time=prediction_time,
                status="error",
                error_message=str(e)
            )
            
            await self.db.commit()
            raise
    
    async def delete_model(self, model: MLModel) -> None:
        if os.path.exists(model.file_path):
            os.remove(model.file_path)
        
        await self.db.delete(model)
        await self.db.commit()
