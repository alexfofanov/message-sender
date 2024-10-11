import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.services.tasks import process_queue
from src.api.v1.base import api_router
from src.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(process_queue())
    yield


app = FastAPI(
    title=settings.app_title,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(api_router, prefix='/api/v1')
