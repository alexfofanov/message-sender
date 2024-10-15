import asyncio
from email import message_from_string

import pytest
from fastapi import status

from src.services.email_sender import fm
from tests.conftest import (
    BODY,
    RCPT_TO,
    SUBJECT,
    URL_PATH_SEND_EMAIL,
    decode_item,
    redis,
)

RCPT_TOS = [
    'example1@example.com',
    'example2@example.com',
    'example3@example.com',
]

FILE_CONTENT_1 = b'File content one'
FILE_CONTENT_2 = b'File content two'


@pytest.mark.anyio
async def test_send_email_without_required_field(async_client):
    await redis.flushdb()

    with fm.record_messages() as outbox:
        files = [
            ('files', ('test_file1.txt', FILE_CONTENT_1, 'text/plain')),
            ('files', ('test_file2.txt', FILE_CONTENT_2, 'text/plain')),
        ]

        response = await async_client.post(
            URL_PATH_SEND_EMAIL,
            data={
                'emails': RCPT_TO,
                'body': BODY,
            },
            files=files,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert len(outbox) == 0


@pytest.mark.anyio
async def test_send_email_with_files(async_client):
    await redis.flushdb()

    with fm.record_messages() as outbox:
        files = [
            ('files', ('test_file1.txt', FILE_CONTENT_1, 'text/plain')),
            ('files', ('test_file2.txt', FILE_CONTENT_2, 'text/plain')),
        ]

        response = await async_client.post(
            URL_PATH_SEND_EMAIL,
            data={
                'emails': RCPT_TO,
                'subject': SUBJECT,
                'body': BODY,
            },
            files=files,
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            'status': 'В очередь на отправку добавлены сообщения в количестве: 1'
        }
        await asyncio.sleep(2)

        assert len(outbox) == 1
        sent_message = message_from_string(outbox[0].as_string())
        assert sent_message['From'] == 'Your Name1 <from@example.com>'

        subject = decode_item(sent_message['Subject'])
        assert subject == SUBJECT

        email_body = None
        for part in sent_message.walk():
            if part.get_content_type() == "text/html":
                email_body = part.get_payload(decode=True).decode('utf-8')
                assert email_body == BODY
        assert email_body

        has_attachment = False

        idx = 0
        for part in sent_message.walk():
            if part.get_content_disposition() == "attachment":
                has_attachment = True
                file_name = part.get_filename()
                assert file_name == files[idx][1][0]
                file_content = part.get_payload(decode=True)
                assert file_content == files[idx][1][1]
                idx += 1
        assert has_attachment


@pytest.mark.anyio
async def test_send_email_without_files(async_client):
    await redis.flushdb()

    with fm.record_messages() as outbox:
        response = await async_client.post(
            URL_PATH_SEND_EMAIL,
            data={
                'emails': RCPT_TO,
                'subject': SUBJECT,
                'body': BODY,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            'status': (
                'В очередь на отправку добавлены сообщения в количестве: 1'
            )
        }
        await asyncio.sleep(2)

        assert len(outbox) == 1
        sent_message = message_from_string(outbox[0].as_string())
        assert sent_message['From'] == 'Your Name1 <from@example.com>'

        subject = decode_item(sent_message['Subject'])
        assert subject == SUBJECT

        email_body = None
        for part in sent_message.walk():
            if part.get_content_type() == "text/html":
                email_body = part.get_payload(decode=True).decode('utf-8')
                assert email_body == BODY
        assert email_body


@pytest.mark.anyio
async def test_send_several_emails(async_client):
    await redis.flushdb()

    with fm.record_messages() as outbox:
        files = [
            ('files', ('test_file1.txt', FILE_CONTENT_1, 'text/plain')),
            ('files', ('test_file2.txt', FILE_CONTENT_2, 'text/plain')),
        ]

        response = await async_client.post(
            URL_PATH_SEND_EMAIL,
            data={
                'emails': RCPT_TOS,
                'subject': SUBJECT,
                'body': BODY,
            },
            files=files,
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            'status': f'В очередь на отправку добавлены сообщения в количестве: {len(RCPT_TOS)}'
        }
        await asyncio.sleep(len(RCPT_TOS) * 2)

        assert len(outbox) == len(RCPT_TOS)
