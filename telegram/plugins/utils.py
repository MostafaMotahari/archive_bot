from functools import wraps
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select
from telethon.custom import Message

from database.engine import redis, engine
from database.models import BotUser


def anti_spam():
    def decorator(func):
        @wraps(func)
        async def wrapper(event: Message, *args, **kwargs) -> bool:
            user_cache_key = 'spam_cache_' + str(await event.from_id.user_id)
            if redis.get(user_cache_key, None):
                await event.reply('لطفاً از ارسال پیام‌های تکراری یا غیرمرتبط خودداری کنید.')
                return False
            redis.setex(user_cache_key, 1, user_cache_key)
            return await func(event, *args, **kwargs)
        return wrapper
    return decorator


def check_registration():
    def decorator(func):
        @wraps(func)
        async def wrapper(event: Message, *args, **kwargs):
            user_id = str(event.from_id.user_id)
            if not redis.sismember('cached_user_ids', user_id):
                async with async_sessionmaker(engine, expire_on_commit=True) as session:
                    user = BotUser(user_id=user_id)
                    session.add(user)
                    session.commit()
                    redis.sadd('cached_user_ids', user_id)
            return await func(event, *args, **kwargs)
        return wrapper
    return decorator



async def load_caches():
    async with async_sessionmaker(engine, expire_on_commit=True) as session:
        users = await session.scalars(select(BotUser.user_id)).all()
        redis.sadd('cached_user_ids', list(users))
