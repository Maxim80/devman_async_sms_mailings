import asyncio
import aioredis


async def main():
    redis = aioredis.from_url(
        'redis://127.0.0.1:6379', encoding='utf-8', decode_responses=True
    )
    await redis.set('phone', 'MYPHONENUMBER')
    value = await redis.get('phone')
    await redis.close()
    print(value)


if __name__ == '__main__':
    asyncio.run(main())
