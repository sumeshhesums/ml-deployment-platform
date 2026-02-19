"""
Main FastAPI application for ML Model Deployment Platform
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
import joblib
import numpy as np
from typing import Optional, Dict, Any
import json
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="ML Model Deployment Platform",
    description="A platform for deploying and managing machine learning models as APIs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create models directory if it doesn't exist
MODELS_DIR = "deployed_models"
os.makedirs(MODELS_DIR, exist_ok=True)

# Database simulation (in production, use SQLite/PostgreSQL)
models_db = {}

class ModelInfo(BaseModel):
    """Model information schema"""
    model_id: str
    name: str
    framework: str
    upload_date: str
    version: str = "1.0"
    description: Optional[str] = None
    input_shape: Optional[Dict[str, Any]] = None
    output_shape: Optional[Dict[str, Any]] = None

class PredictionRequest(BaseModel):
    """Prediction request schema"""
    input_data: Dict[str, Any]

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ML Model Deployment Platform",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "upload_model": "/models/upload",
            "list_models": "/models",
            "predict": "/predict/{model_id}",
            "model_stats": "/models/{model_id}/stats"
        }
    }

@app.post("/models/upload")
async def upload_model(
    file: UploadFile = File(...),
    name: str = "Unnamed Model",
    framework: str = "scikit-learn",
    description: Optional[str] = None
):
    """Upload a trained ML model"""
    try:
        # Generate unique model ID
        model_id = str(uuid.uuid4())
        
        # Save model file
        model_path = os.path.join(MODELS_DIR, f"{model_id}.joblib")
        
        # Read and save the file
        contents = await file.read()
        with open(model_path, "wb") as f:
            f.write(contents)
        
        # Load model to get metadata (simple validation)
        try:
            model = joblib.load(model_path)
            # Try to get some basic info about the model
            model_type = type(model).__name__
        except Exception as e:
            # Clean up if model loading fails
            os.remove(model_path)
            raise HTTPException(status_code=400, detail=f"Invalid model file: {str(e)}")
        
        # Store model metadata
        upload_date = datetime.now().isoformat()
        models_db[model_id] = {
            "model_id": model_id,
            "name": name,
            "framework": framework,
            "upload_date": upload_date,
            "description": description,
            "file_path": model_path,
            "model_type": model_type,
            "usage_count": 0
        }
        
        return {
            "status": "success",
            "message": "Model uploaded successfully",
            "model_info": models_db[model_id]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading model: {str(e)}")

@app.get("/models")
async def list_models():
    """List all deployed models"""
    return {
        "status": "success",
        "count": len(models_db),
        "models": list(models_db.values())
    }

@app.post("/predict/{model_id}")
async def predict(model_id: str, request: PredictionRequest):
    """Make predictions using a deployed model"""
    try:
        # Check if model exists
        if model_id not in models_db:
            raise HTTPException(status_code=404, detail="Model not found")
        
        model_info = models_db[model_id]
        model_path = model_info["file_path"]
        
        # Load the model
        model = joblib.load(model_path)
        
        # Convert input data to numpy array
        input_data = request.input_data
        
        # Simple input processing - in production, add proper validation
        if isinstance(input_data, dict):
            # Handle dictionary input (for structured data)
            # Convert to DataFrame or appropriate format
            import pandas as pd
            input_df = pd.DataFrame([input_data])
            predictions = model.predict(input_df)
        elif isinstance(input_data, list):
            # Handle list/array input
            input_array = np.array(input_data)
            if len(input_array.shape) == 1:
                input_array = input_array.reshape(1, -1)
            predictions = model.predict(input_array)
        else:
            raise HTTPException(status_code=400, detail="Unsupported input format")
        
        # Update usage count
        models_db[model_id]["usage_count"] += 1
        
        return {
            "status": "success",
            "model_id": model_id,
            "model_name": model_info["name"],
            "predictions": predictions.tolist(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/models/{model_id}/stats")
async def get_model_stats(model_id: str):
    """Get model statistics and metadata"""
    if model_id not in models_db:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model_info = models_db[model_id]
    
    return {
        "status": "success",
        "model_info": model_info,
        "statistics": {
            "usage_count": model_info.get("usage_count", 0),
            "upload_date": model_info["upload_date"],
            "last_used": datetime.now().isoformat()  # In production, track actual last used
        }
    }

@app.delete("/models/{model_id}")
async def delete_model(model_id: str):
    """Delete a deployed model"""
    if model_id not in models_db:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model_info = models_db[model_id]
    model_path = model_info["file_path"]
    
    try:
        # Remove model file
        if os.path.exists(model_path):
            os.remove(model_path)
        
        # Remove from database
        del models_db[model_id]
        
        return {
            "status": "success",
            "message": "Model deleted successfully",
            "model_id": model_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting model: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)