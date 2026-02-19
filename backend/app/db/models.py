from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    models = relationship("MLModel", back_populates="owner", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")


class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    framework = Column(String(50), nullable=False)
    model_type = Column(String(100))
    version = Column(String(50), default="1.0.0")
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    input_schema = Column(Text)
    output_schema = Column(Text)
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="models")
    predictions = relationship("Prediction", back_populates="model", cascade="all, delete-orphan")
    versions = relationship("ModelVersion", back_populates="model", cascade="all, delete-orphan")


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ml_models.id"), nullable=False)
    version = Column(String(50), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    changelog = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    model = relationship("MLModel", back_populates="versions")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ml_models.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    input_data = Column(Text, nullable=False)
    output_data = Column(Text, nullable=False)
    prediction_time = Column(Float)
    status = Column(String(50), default="success")
    error_message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    model = relationship("MLModel", back_populates="predictions")
    user = relationship("User", back_populates="predictions")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="audit_logs")
