import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.responses import JSONResponse

from src.clients.kafka_producer import KafkaProducer
from src.exceptions import AppException
from src.exceptions.handler import app_exception_handler
from src.routers.product_info_router import router as product_info_router
from src.workers.kafka_consumer import consume_events


@asynccontextmanager
async def lifespan(app: FastAPI):
    producer = KafkaProducer()
    await producer.start()

    consumer_task = asyncio.create_task(consume_events(producer))

    yield

    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass

    await producer.stop()


def _include_routers(app: FastAPI) -> None:
    app.include_router(product_info_router, prefix="/api/v1")


def _add_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)


def get_app() -> FastAPI:
    app = FastAPI(
        title="Product Info Service",
        docs_url="/docs",
        openapi_url="/openapi.json",
        default_response_class=JSONResponse,
        lifespan=lifespan,
    )

    _add_handlers(app)
    _include_routers(app)

    return app
