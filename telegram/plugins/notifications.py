from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy.orm import Session
from sqlalchemy import select
import os

from database.engine import engine
from database.models import BotUser


@Client.on_message(filters.private & filters.user(os.environ.get('ADMIN_ID')) & filters.regex("^/broadcast$") & filters.reply)
def send_broadcast(client: Client, message: Message):
    message.reply_text(
        "📲 ارسال پیام به کاربران:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("ارسال پیام به رشته برق", "send-electrical_engineering"),],
            [InlineKeyboardButton("ارسال پیام به رشته کامپیوتر", "send-computer_engineering"),],
            [InlineKeyboardButton("ارسال به همه", "send-all"),],
            # InlineKeyboardButton("", "send_electrical_engineering"),
        ]),
        reply_to_message_id=message.reply_to_message_id
    )


@Client.on_callback_query(filters.user(os.environ.get('ADMIN_ID')) & filters.regex("^send-(.*)$"))
def set_study_field(client: Client, callback_query: CallbackQuery):
    study_field = callback_query.data.split('-')[-1]
    callback_query.message.edit_text(
        "📩 ارسال پیام به صورت:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("فوروارد شده", callback_data=f"send_as_forwarded-{study_field}"),
             InlineKeyboardButton("کپی شده", callback_data=f"send_as_copy-{study_field}")]
        ])
    )


@Client.on_callback_query(filters.user(os.environ.get('ADMIN_ID')) & filters.regex("^send_as_forwarded-(.*)$"))
def forward_broad_cast(client: Client, callback_query: CallbackQuery):
    study_field = callback_query.data.split('-')[-1]

    if study_field == "all":
        with Session(engine) as session:
            bot_users = session.scalars(select(BotUser)).all()
            for user in bot_users:
                try:
                    callback_query.message.reply_to_message.forward(user.user_id)
                except:
                    continue
    else:
        with Session(engine) as session:
            selected_users = session.scalars(select(BotUser).where(BotUser.study_field == study_field).where(BotUser.receive_notifications == True)).all()
            for user in selected_users:
                try:
                    callback_query.message.reply_to_message.forward(user.user_id)
                except:
                    continue
    callback_query.message.edit_text("پیام با موفقیت ارسال شد!")


@Client.on_callback_query(filters.user(os.environ.get('ADMIN_ID')) & filters.regex("^send_as_copy-(.*)$"))
def copy_broad_cast(client: Client, callback_query: CallbackQuery):
    study_field = callback_query.data.split('-')[-1]

    if study_field == "all":
        with Session(engine) as session:
            bot_users = session.scalars(select(BotUser)).all()
            for user in bot_users:
                try:
                    callback_query.message.reply_to_message.copy(user.user_id)
                except Exception as e:
                    print(e)
                    continue
    else:
        with Session(engine) as session:
            selected_users = session.scalars(select(BotUser).where(BotUser.study_field == study_field).where(BotUser.receive_notifications == True)).all()
            for user in selected_users:
                try:
                    callback_query.message.reply_to_message.copy(user.user_id)
                except:
                    continue
    callback_query.message.edit_text("پیام با موفقیت ارسال شد!")
