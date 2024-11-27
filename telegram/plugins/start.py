from telethon import events
from telethon.tl.types import Message, ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy import select
from sqlalchemy.orm import Session

from telegram.client.client_manager import client_object
from database.models import BotUser, Statistics
from database.engine import engine


@client_object.on(events.NewMessage(pattern="/start"))
async def start_message(event):
    async with Session(engine) as session:
        if not session.scalar(select(BotUser).where(BotUser.user_id == message.sender_id)):
            bot_user = BotUser(user_id=message.sender_id)
            session.add(bot_user)

            bot_statistics: Statistics = session.scalar(select(Statistics).where(Statistics.id == 1))
            bot_statistics.users_count += 1
            session.commit()

    await client.send_message(
        message.chat_id,
        "بزن بریم ....\n",
        reply_markup=ReplyKeyboardMarkup(
            [
                [KeyboardButton("📖 لیست رشته ها 📖")],
            ],
            resize_keyboard=True
        )
    )
