from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy.orm import Session
from sqlalchemy import select
import os

from database.engine import engine
from database.models import BotUser


@Client.on_message(filters.private & filters.regex("^/send_doc$"))
def send_document(client: Client, message: Message):
    if message.reply_to_message.document:
        message.reply_to_message.copy(
            # os.environ.get('ADMIN_ID')
            "Mousiol",
            caption="📚 جزوه ارسال شده از:\n"
            f"{message.from_user.first_name} {message.from_user.id}",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("✅ ثبت جزوه", callback_data=f"submit_doc-{message.from_user.id}")]]
            )
        )

        message.reply_text(
            "✅ جزوتون برا ادمین ارسال شد!\n"
            "ممنون ازینکه به دوستاتون کمک میکنید ❤️"
        )

    else:
        message.reply_text("❌لطفا این پیام رو روی یک فایل ریپلای کن")


@Client.on_callback_query(filters.regex("^submit_doc-(.*)$"))
def submit_document(client: Client, callback_query: CallbackQuery):
    user_id = int(callback_query.data.split('-')[-1])
    with Session(engine) as session:
        user_obj: BotUser = session.scalar(select(BotUser).where(BotUser.user_id == user_id))
        user_obj.uploaded_docs += 1
        session.commit()

    callback_query.message.edit_reply_markup(None)
    callback_query.answer("✅جزوه با موفقیت ثبت شد", show_alert=True)
    try:
        client.send_message(
            user_id,
            "✅ یکی از جزوه هایی که فرستاده بودی به آرشیو اضافه شد!\n\n"
            "ازینکه کمک میکنی تا آرشیو کامل تری شکل بگیر ممنونم. دَمِدَم گرم 🫶\n\n"
            "راستی میتونی با دستور /leaderboard لیست افرادی که بیشترین مشارکت رو داشتن دریافت کنی!\n\n"
        )
    except:
        pass
