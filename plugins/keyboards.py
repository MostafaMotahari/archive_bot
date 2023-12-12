import subprocess
import re
import os

from pyrogram import Client, filters
from pathlib import Path
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import Statistics
from database.engine import engine


@Client.on_message(filters.private & filters.regex("^📖 لیست رشته ها 📖$"))
def show_study_fields(client: Client, message: Message):
    message.reply_text(
        "رشته تون رو انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(
            [
                [KeyboardButton("⚡️ مهندسی برق ⚡️")],
                [KeyboardButton("💻 مهندسی کامپیوتر 💻")],
                [KeyboardButton("↩️ بازگشت به منوی قبل")]
            ],
            resize_keyboard=True
            )
        )


@Client.on_message(filters.private & filters.regex("^⚡️ مهندسی برق ⚡️$"))
def show_electrical_engineering_contents(client: Client, message: Message):
    folders = subprocess.run(["mega-ls", "ee"], capture_output=True).stdout.decode().split("\n")
    message.reply_text(
        f"لیست فولدر های موجود برای {message.text} :",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(label, callback_data=f"ls-ee/{label}")] for label in folders],
        )
    )


@Client.on_message(filters.private & filters.regex("^💻 مهندسی کامپیوتر 💻$"))
def show_computer_engineering_contents(client: Client, message: Message):
    folders = subprocess.run(["mega-ls", "ce"], capture_output=True).stdout.decode().split("\n")
    message.reply_text(
        f"📂 آرشیو موجود برای {message.text}:",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(label, callback_data=f"ls-ce/{label}")] for label in folders],
        )
    )


@Client.on_callback_query(filters.regex("^ls-(.*)"))
def show_folder_content(client: Client, callback_query: CallbackQuery):
    print("mega-ls", callback_query.data.split("-")[-1])
    contents = subprocess.run(["mega-ls", callback_query.data.split("-")[-1]], capture_output=True).stdout.decode().strip().split("\n")
    file_pattern = re.compile(r".*\..+")

    # Content keyboard
    keyboard = [[
        InlineKeyboardButton( label,
            callback_data=f"{'dn-' if file_pattern.match(label) else 'ls-'}{callback_query.data.split('-')[-1]}/{label}")
    ] for label in contents]

    # Place return button
    if len(callback_query.data.split('/')) != 1:
        keyboard.append([
            InlineKeyboardButton("🔝 برگشت به فولدر قبلی 🔝", callback_data="/".join(callback_query.data.split('/')[:-1]))
        ])
    print(keyboard)

    callback_query.message.edit_text(
        "🗄 فولدر یا فایل مورد نظرتو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@Client.on_callback_query(filters.regex("^dn-(.*)/(.*)"))
def download_content(client: Client, callback_query: CallbackQuery):
    file_name = callback_query.data.split('/')[-1]
    file_path = Path('downloads/' + file_name)

    # Check if the file exists
    if not file_path.is_file():
        response = subprocess.run(["mega-get", callback_query.data.split('-')[-1], "downloads/"], capture_output=True)

    file_size = os.path.getsize(file_path)

    with Session(engine) as session:
        bot_stats: Statistics = session.scalar(select(Statistics).where(Statistics.id == 1))
        bot_stats.download += file_size
        session.commit()

    callback_query.message.delete()
    msg = client.send_message(callback_query.message.chat.id, "درحال آپلود فایل ...")

    client.send_document(
        callback_query.message.chat.id,
        file_path,
        caption=f"{callback_query.data.split('/')[-1]} - {int(file_size / 1000000)} MB"
    )

    msg.delete()
