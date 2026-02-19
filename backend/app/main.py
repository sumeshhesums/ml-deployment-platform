from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from loguru import logger

from app.core.config import settings
from app.db.database import init_db
from app.utils.middleware import LoggingMiddleware
from app.api import auth, models, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application...")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down application...")


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda req, exc: Response(content="Rate limit exceeded", status_code=429))

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/docs",
        "health": "/health"
    }


app.include_router(auth.router, prefix="/api/v1")
app.include_router(models.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
