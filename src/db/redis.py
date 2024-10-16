import redis.asyncio
from redis.asyncio import Redis

from src.core.config import settings

redis: Redis = redis.asyncio.from_url(settings.redis_url, db=settings.redis_num_db)


async def get_redis() -> Redis:
    try:
        yield redis
    finally:
        await redis.aclose()
