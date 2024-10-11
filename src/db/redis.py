import redis.asyncio
from redis import Redis

from src.core.config import settings

redis: Redis = redis.asyncio.from_url(settings.redis_url)


async def get_redis() -> Redis:
    try:
        yield redis
    finally:
        await redis.close()
