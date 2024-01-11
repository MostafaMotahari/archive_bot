from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
import os

from database.engine import engine
from database.models import BotUser, Statistics, Document


@Client.on_message(filters.private & filters.regex("^/leaderboard$"))
def leaderboard(client: Client, message: Message):
    with Session(engine) as session:
        top_docers = session.scalars(select(BotUser).where(BotUser.uploaded_docs != 0)\
                .where(BotUser.user_id != 608470908).order_by(desc(BotUser.uploaded_docs))).all()
        template_text = "🏅 لیست نفرات برتری که مشارکت بیشتری تو تکمیل آرشیو مطالب داشتند:\n\n"

        for index, user in enumerate(top_docers):
            template_text += f"{index + 1}. {client.get_users(user.user_id).first_name} ({user.uploaded_docs} فایل)\n"

        message.reply_text(template_text)


@Client.on_message(filters.private & filters.user(os.environ.get("ADMIN_ID")) & filters.regex("^/stats$"))
def get_stats(client: Client, message: Message):
    with Session(engine) as session:
        users_count = session.scalar(select(func.count()).select_from(BotUser))
        total_docs = session.scalar(select(func.count()).select_from(Document))
        total_traffics = session.scalar(select(Statistics).where(Statistics.id == 1))
        
        message.reply_text(
            f"👤 [{users_count}] کاربر\n"
            f"🌐 [{int(total_traffics.downloaded / 1000000)}] مگابایت دانلود\n"
            f"🌐 [{int(total_traffics.uploaded / 1000000)}] مگابایت آپلود\n"
            f"📁 [{total_docs}] کل فایل های آپلود شده\n"
        )
