from fastapi import Request
from starlette.responses import JSONResponse

from src.exceptions.base import AppException
from src.schemas.error import ErrorResponse


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=exc.detail).model_dump(),
    )
