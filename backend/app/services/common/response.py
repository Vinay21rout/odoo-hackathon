from typing import Any, Optional
from app.core.constants import MSG_SUCCESS, MSG_FAILED

def success_response(data: Any = None, message: str = MSG_SUCCESS) -> dict:
    return {
        "success": True,
        "message": message,
        "data": data
    }

def failure_response(message: str = MSG_FAILED) -> dict:
    return {
        "success": False,
        "message": message
    }
