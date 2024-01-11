from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy.orm import Session
from sqlalchemy import select

from database.engine import engine
from database.models import BotUser


@Client.on_message(filters.private & (filters.regex("^⚙️ تنظیمات ⚙️$") | filters.regex("^/settings$")))
def show_panel(client: Client, message: Message):
    message.reply_text(
        "🎛 پنل کاربری",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔔 نوتیفیکیشن 🔔", callback_data="turn_notifications")]
        ])
    )


@Client.on_callback_query(filters.regex("^turn_notifications$"))
def turn_notifications(client: Client, callback_query: CallbackQuery):
    with Session(engine) as session:
        bot_user = session.scalar(select(BotUser).where(BotUser.user_id == callback_query.from_user.id))
        callback_query.message.edit_text(
            "🔔 نوتیفیکیشن 🔔",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(f"روشن {'✅' if bot_user.receive_notifications else ''}", callback_data="turn_on_notifications"),
                    InlineKeyboardButton(f"خاموش {'❌' if not bot_user.receive_notifications else ''}", callback_data="turn_off_notifications")]
            ])
        )


@Client.on_callback_query(filters.regex("^turn_(.*)_notifications$"))
def change_notifications_status(client: Client, callback_query: CallbackQuery):
    turn_stage = callback_query.data.split("_")[1]
    with Session(engine) as session:
        bot_user = session.scalar(select(BotUser).where(BotUser.user_id == callback_query.from_user.id))
        if turn_stage == "on":
            bot_user.receive_notifications = True
            callback_query.answer("✅ نوتیفیکیشن های شما روشن شد!")
            callback_query.message.edit_reply_markup(InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(f"روشن {'✅' if bot_user.receive_notifications else ''}", callback_data="turn_on_notifications"),
                    InlineKeyboardButton(f"خاموش {'❌' if not bot_user.receive_notifications else ''}", callback_data="turn_off_notifications")]
                ])
            )
        else:
            bot_user.receive_notifications = False
            callback_query.answer("❌ نوتیفیکیشن های شما خاموش شد!")
            callback_query.message.edit_reply_markup(InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(f"روشن {'✅' if bot_user.receive_notifications else ''}", callback_data="turn_on_notifications"),
                    InlineKeyboardButton(f"خاموش {'❌' if not bot_user.receive_notifications else ''}", callback_data="turn_off_notifications")]
                ])
            )
        session.commit()
