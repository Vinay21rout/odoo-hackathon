import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import logger

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate execution time in milliseconds
        process_time = (time.time() - start_time) * 1000
        
        # Log the request details
        logger.info(
            f"Method: {request.method} | "
            f"Path: {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Time: {process_time:.2f}ms"
        )
        
        return response
