from http import HTTPStatus

from src.exceptions.base import AppException


class ValidationException(AppException, ValueError):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY

    def __init__(self, field: str, message: str):
        AppException.__init__(self, f"{field}: {message}")
