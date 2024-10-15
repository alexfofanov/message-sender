import asyncio
import json

from redis.asyncio import Redis

from src.core.config import EMAIL_QUEUE
from src.services.email_sender import send_email


async def process_queue(redis: Redis):
    """
    Обработка очереди на отправку сообщений
    """

    while True:
        message = await redis.lpop(EMAIL_QUEUE)
        if message:
            await send_email(json.loads(message), redis)
        else:
            await asyncio.sleep(1)
