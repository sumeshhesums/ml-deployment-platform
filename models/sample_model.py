"""
Sample ML model for testing the deployment platform
This creates a simple scikit-learn model that we can deploy
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
import joblib

def create_sample_model(output_path="sample_iris_model.joblib"):
    """Create and save a sample Iris classification model"""
    
    # Load Iris dataset
    iris = load_iris()
    X, y = iris.data, iris.target
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create and train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate model
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"Model trained successfully!")
    print(f"Training accuracy: {train_score:.3f}")
    print(f"Test accuracy: {test_score:.3f}")
    
    # Save model
    joblib.dump(model, output_path)
    print(f"Model saved to: {output_path}")
    
    return model

if __name__ == "__main__":
    create_sample_model()
    
    # Show example prediction
    print("\nExample prediction:")
    model = joblib.load("sample_iris_model.joblib")
    sample_input = [[5.1, 3.5, 1.4, 0.2]]  # Example iris features
    prediction = model.predict(sample_input)
    print(f"Input: {sample_input}")
    print(f"Predicted class: {prediction[0]} (Iris class)")
    print(f"Class names: {load_iris().target_names}")