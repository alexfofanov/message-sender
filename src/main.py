import asyncio
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.api.v1.base import api_router
from src.core.config import settings
from src.db.redis import redis
from src.services.tasks import process_queue


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(process_queue(redis))
    yield


def get_application(lifespan_func: Callable) -> FastAPI:
    app = FastAPI(
        title=settings.app_title,
        docs_url='/api/openapi',
        openapi_url='/api/openapi.json',
        default_response_class=ORJSONResponse,
        lifespan=lifespan_func,
    )
    app.include_router(api_router, prefix='/api/v1')

    return app


app = get_application(lifespan)
