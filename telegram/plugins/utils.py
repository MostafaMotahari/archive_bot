from functools import wraps
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select
from telethon.events import NewMessage

from database.engine import redis, engine, session
from database.models import BotUser


def anti_spam(func):
    @wraps(func)
    async def wrapper(event: NewMessage.Event, *args, **kwargs) -> bool:
        user_cache_key = 'spam_cache_' + str(await event.get_sender().user_id)
        if redis.get(user_cache_key, None):
            await event.reply('لطفاً از ارسال پیام‌های تکراری یا غیرمرتبط خودداری کنید.')
            return False
        redis.setex(user_cache_key, 1, user_cache_key)
        return await func(event, *args, **kwargs)
    return wrapper


def check_registration(func):
    @wraps(func)
    async def wrapper(event: NewMessage.Event, *args, **kwargs):
        user = await event.get_sender()
        user_id = str(user.id)
        if not redis.sismember('cached_user_ids', user_id):
            async with session() as async_session:
                user = BotUser(user_id=user_id)
                async_session.add(user)
                async_session.commit()
                redis.sadd('cached_user_ids', user_id)
        return await func(event, *args, **kwargs)
    return wrapper



async def load_caches():
    async with async_sessionmaker(engine, expire_on_commit=True) as session:
        users = await session.scalars(select(BotUser.user_id)).all()
        redis.sadd('cached_user_ids', list(users))
