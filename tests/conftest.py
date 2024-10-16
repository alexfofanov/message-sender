import asyncio
from contextlib import asynccontextmanager
from email.header import decode_header

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis, from_url

from src.core.config import settings
from src.db.redis import get_redis
from src.main import get_application
from src.services.tasks import process_queue

URL_PATH_SEND_EMAIL = '/api/v1/send_email/'
MAIL_FROM = 'from@example.com'
RCPT_TO = 'example1@example.com'
SUBJECT = 'Тема сообщения'
BODY = 'Текст сообщения'


@pytest.fixture(scope='session')
def anyio_backend():
    return 'asyncio'


redis: Redis = from_url(settings.redis_url, db=settings.redis_num_db_test)


async def get_redis_test():
    try:
        yield redis
    finally:
        await redis.aclose()


@asynccontextmanager
async def lifespan_test(app: FastAPI):
    task = asyncio.create_task(process_queue(redis))
    yield


@pytest.fixture(scope='module')
async def clear_redis_db():
    await redis.flushdb()


@pytest.fixture(scope='module')
def set_settings_for_test():
    settings.smtp_servers_file = 'tests/smtp_servers_test.json'
    settings.sending_interval_sec = 0.1


@pytest.fixture(scope='module')
async def async_client(clear_redis_db, set_settings_for_test):
    app = get_application(lifespan_test)
    app.dependency_overrides[get_redis] = get_redis_test
    transport = ASGITransport(app=app)

    async with LifespanManager(app):
        async with AsyncClient(
                transport=transport, base_url='http://test'
        ) as ac:
            yield ac


@asynccontextmanager
async def lifespan_empty_test(app: FastAPI):
    yield


@pytest.fixture(scope='module')
async def async_client_without_lifespan(clear_redis_db):
    app = get_application(lifespan_empty_test)
    app.dependency_overrides[get_redis] = get_redis_test
    transport = ASGITransport(app=app)

    async with LifespanManager(app):
        async with AsyncClient(
                transport=transport, base_url='http://test'
        ) as ac:
            yield ac


def decode_item(item: str) -> str:
    decoded_subject, encoding = decode_header(item)[0]
    if isinstance(decoded_subject, bytes):
        decoded_subject = decoded_subject.decode(encoding or 'utf-8')

    return decoded_subject
