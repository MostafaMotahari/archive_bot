from telethon.custom import Message
from telethon.events import NewMessage
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select

from client.engine import client
from plugins.utils import anti_spam, check_registration
from database.engine import engine
from database.models import BotUser


@check_registration
@anti_spam
@client.on(NewMessage(pattern=''))
def panel(event: Message):
    async with async_sessionmaker(engine, expire_on_commit=True) as session:
        user = session.scalar(select(BotUser).where(BotUser.user_id == str(event.from_id.user_id)))
        event.reply()
