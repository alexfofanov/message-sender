import json

import pytest
from fastapi import status

from src.core.config import EMAIL_QUEUE
from tests.conftest import redis, RCPT_TO, SUBJECT, BODY, URL_PATH_SEND_EMAIL


@pytest.mark.anyio
async def test_get_email_status_not_empty(async_client_without_lifespan):
    await redis.flushdb()
    await redis.rpush(
        EMAIL_QUEUE,
        json.dumps(
            {
                'email': RCPT_TO,
                'subject': SUBJECT,
                'body': BODY,
            }
        ),
    )
    response = await async_client_without_lifespan.get(
        f'{URL_PATH_SEND_EMAIL}status'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'total': 1,
        'messages': [{'number': 1, 'email': RCPT_TO, 'subject': SUBJECT}],
    }


@pytest.mark.anyio
async def test_get_email_status_empty(async_client_without_lifespan):
    await redis.flushdb()
    response = await async_client_without_lifespan.get(
        f'{URL_PATH_SEND_EMAIL}status'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'total': 0, 'messages': []}
