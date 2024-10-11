import asyncio
import json

from src.core.config import EMAIL_QUEUE
from src.db.redis import redis
from src.services.email_sender import send_email


async def process_queue():
    """
    Обработка очереди на отправку сообщений
    """

    while True:
        message = await redis.lpop(EMAIL_QUEUE)
        if message:
            await send_email(json.loads(message))
        else:
            await asyncio.sleep(1)
