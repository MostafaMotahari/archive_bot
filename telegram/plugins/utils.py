from os import environ
from pytz import timezone
from datetime import datetime
from functools import wraps
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select
from telethon.events import NewMessage

from database.engine import redis, engine, session
from database.models import BotUser


def assistant_decorators(func, anti_spam: bool = False, check_registration: bool = True, log_tracebacks: bool = True):
    @wraps(func)
    async def wrapper(event: NewMessage.Event, *args, **kwargs):
        user = await event.get_sender()
        user_id = str(user.id)
        if anti_spam:
            user_cache_key = 'spam_cache_' + str(user_id)
            if redis.get(user_cache_key, None):
                await event.reply('لطفاً از ارسال پیام‌های تکراری یا غیرمرتبط خودداری کنید.')
                return False
            redis.setex(user_cache_key, 1, user_id)

        if check_registration:
            if not redis.sismember('cached_user_ids', user_id):
                async with session() as async_session:
                    user = BotUser(user_id=user_id)
                    async_session.add(user)
                    async_session.commit()
                    redis.sadd('cached_user_ids', user_id)

        if log_tracebacks:
            try:
                return await func(event, *args, **kwargs)
            except Exception as e:
                tehran_tz = timezone('Asia/Tehran')
                log_line = f"{datetime.now(tehran_tz).strftime("%Y-%m-%d %H:%M:%S %Z%z")} - {str(e)}"

                await event.client.send_message(environ.get('LOG_CHANNEL'), log_line)
                with open('errors.log', 'a') as log:
                    log.write(log_line)

                return

        return await func(event, *args, **kwargs)
    return wrapper


async def load_caches():
    async with async_sessionmaker(engine, expire_on_commit=True) as session:
        users = await session.scalars(select(BotUser.user_id)).all()
        redis.sadd('cached_user_ids', list(users))
