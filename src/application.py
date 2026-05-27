from fastapi import FastAPI
from fastapi.responses import UJSONResponse

from src.exceptions import AppException
from src.exceptions.handler import app_exception_handler
from src.routers.product_info_router import router as product_info_router


def _include_routers(app: FastAPI) -> None:
    app.include_router(product_info_router, prefix="/api/v1")


def _add_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)


def get_app() -> FastAPI:
    app = FastAPI(
        title="Product Info Service",
        docs_url="/docs",
        openapi_url="/openapi.json",
        default_response_class=UJSONResponse,
    )

    _add_handlers(app)
    _include_routers(app)

    return app
