from telethon.events import NewMessage, register
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select

from plugins.utils import anti_spam, check_registration
from database.engine import engine
from database.models import BotUser


@check_registration
@anti_spam
@register(NewMessage(pattern=''))
async def panel(event: NewMessage.Event):
    async with async_sessionmaker(engine, expire_on_commit=True) as session:
        user = session.scalar(select(BotUser).where(BotUser.user_id == str(await event.get_sender().user_id)))
        event.reply()
