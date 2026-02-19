import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
import json


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        start_time = time.time()
        
        logger.info(
            f"Request started | ID: {request_id} | Method: {request.method} | Path: {request.url.path}"
        )
        
        try:
            response = await call_next(request)
            
            process_time = time.time() - start_time
            
            logger.info(
                f"Request completed | ID: {request_id} | "
                f"Method: {request.method} | Path: {request.url.path} | "
                f"Status: {response.status_code} | Duration: {process_time:.3f}s"
            )
            
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            logger.error(
                f"Request failed | ID: {request_id} | "
                f"Method: {request.method} | Path: {request.url.path} | "
                f"Error: {str(e)} | Duration: {process_time:.3f}s"
            )
            raise
