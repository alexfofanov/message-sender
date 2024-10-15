import json
import shutil
import uuid
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Form, UploadFile, status, Depends
from pydantic import EmailStr
from redis.asyncio import Redis

from src.core.config import EMAIL_QUEUE, settings
from src.db.redis import get_redis
from src.schemas.send_email import EmailMessageInfo, SendEmailStatus

send_email_router = APIRouter()


@send_email_router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    summary='Отправка сообщения',
    description='Отправка отдельного сообщения каждому получателю из списка',
)
async def send_email(
    *,
    redis: Redis = Depends(get_redis),
    emails: list[EmailStr] = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    files: Optional[list[UploadFile]] = None,
) -> Any:
    """
    Отправка отдельного сообщения каждому получателю из списка
    """

    attach_files_paths = []
    for file in files:
        upload_folder = Path(
            f'{settings.upload_folder}/{str(uuid.uuid4())}'
        )
        upload_folder.mkdir(parents=True, exist_ok=True)
        file_path = upload_folder / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        attach_files_paths.append(str(file_path))

    for email in emails:
        await redis.rpush(
            EMAIL_QUEUE,
            json.dumps(
                {
                    'email': email,
                    'subject': subject,
                    'body': body,
                    'attach_files_paths': attach_files_paths,
                }
            ),
        )


    for file_path in attach_files_paths:
        await redis.set(file_path, len(emails), ex=settings.redis_ttl_sec)

    return {
        'status': (
            f'В очередь на отправку добавлены сообщения в количестве: '
            f'{len(emails)}'
        )
    }


@send_email_router.get(
    '/status',
    response_model=SendEmailStatus,
    summary='Получение статуса',
    description='Получение статуса очереди отправки сообщений',
)
async def get_email_status(redis: Redis = Depends(get_redis)) -> Any:
    """
    Получение статуса очереди отправки сообщений
    """

    total_messages = await redis.llen(EMAIL_QUEUE)
    messages_in_queue = await redis.lrange(EMAIL_QUEUE, 0, -1)
    messages = []
    for number, message in enumerate(map(json.loads, messages_in_queue), 1):
        messages.append(
            EmailMessageInfo(
                number=number,
                email=message['email'],
                subject=message['subject'],
            )
        )

    return {'total': total_messages, 'messages': messages}
