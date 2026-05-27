from fastapi import Request
from fastapi.responses import UJSONResponse

from src.exceptions.base import AppException


async def app_exception_handler(request: Request, exc: AppException) -> UJSONResponse:
    return UJSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
