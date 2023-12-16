import os

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import Statistics, Directory, Document
from database.engine import engine


@Client.on_message(filters.private & filters.regex("^📖 لیست رشته ها 📖$"))
def show_study_fields(client: Client, message: Message):
    with Session(engine) as session:
        parent_directories = session.scalars(select(Directory).where(Directory.parent_id == None)).all()
        keyboard = [[InlineKeyboardButton(directory.persian_title, callback_data=f"ls-{directory.id}/")]
                    for directory in parent_directories]
        message.reply_text( "رشته تون رو انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))


@Client.on_callback_query(filters.regex("^ls-(.*)"))
def show_folder_content(client: Client, callback_query: CallbackQuery):
    with Session(engine) as session:
        directory_id = callback_query.data.split('-')[-1].split('/')[-1]
        directory = session.scalar(select(Directory).where(Directory.id == int(directory_id)))
        keyboard = [[InlineKeyboardButton(directory.persian_title, callback_data=f"ls-{callback_query.data.split('-')[-1]}/{directory.id}")]
                    for directory in directory.sub_directories]

        for document in directory.documents:
            keyboard.append([InlineKeyboardButton(document.persian_title, callback_data=f"dn-{callback_query.data.split('-')[-1]}/{document.id}")])

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
    with Session(engine) as session:
        document_id = callback_query.data.split('/')[-1]
        document = session.scalar(select(Document).where(Document.id == int(document_id)))
        document_size = os.path.getsize(document.path)

        bot_stats = session.scalar(select(Statistics).where(Statistics.id == 1))
        bot_stats.downloaded += document_size
        session.commit()

        callback_query.message.delete()
        msg = client.send_message(callback_query.message.chat.id, "درحال آپلود فایل ...")

        client.send_document(
            callback_query.message.chat.id,
            document.path,
            caption=f"{document.persian_title}\n{int(document_size / 1000000)} MB"
        )
        msg.delete()
