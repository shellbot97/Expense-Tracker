"""
Exception handler middleware
Converts application exceptions to proper HTTP responses
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from src.utils.exceptions import BaseAppException
import logging

logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exc: BaseAppException):
    """
    Handle application exceptions
    Convert to JSON response with appropriate status code
    """
    logger.error(
        f"Application error: {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "status_code": exc.status_code,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions
    Log full error and return generic message to client
    """
    logger.exception(
        f"Unexpected error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "status_code": 500,
        },
    )
