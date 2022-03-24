from aioredis import Redis, from_url

from components.getsetter import GetSetTer
from setting import setting

pool = GetSetTer()


async def register_redis():
    pool.val = await from_url(
        f"redis://{setting.redis.host}",
        port=setting.redis.port,
        password=setting.redis.password,
    )


def client() -> Redis:
    return pool.val
