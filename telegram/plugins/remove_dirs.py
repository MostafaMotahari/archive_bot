import os
import shutil

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import Directory, Document
from database.engine import engine
from plugins.utils import cmd_to_path


@Client.on_message(filters.private & filters.user(os.environ.get('ADMIN_ID')) & filters.regex("^/remove_dir$"))
def remove_directory(client: Client, message: Message):
    with Session(engine) as session:
        directories = session.scalars(select(Directory).where(Directory.parent_id == None)).all()
        keyboard = [[InlineKeyboardButton(directory.persian_title, callback_data=f"rmdirls-{directory.id}/")]
                    for directory in directories]
        keyboard.append([InlineKeyboardButton("حذف همه فایل ها و فولدرها", callback_data="rmdir-root/")])
        message.reply_text(
            "⬅️فولدر رو انتخاب کن:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


@Client.on_callback_query(filters.user(os.environ.get('ADMIN_ID')) & filters.regex("^rmdirls-(.*)/"))
def removedir_ls(client: Client, callback_query: CallbackQuery):
    with Session(engine) as session:
        directory_id = callback_query.data.split('-')[-1].split('/')[-2]
        sub_directories = session.scalars(select(Directory).where(Directory.parent_id == int(directory_id))).all()
        documents = session.scalars(select(Document).where(Document.directory_id == directory_id)).all()

        keyboard = [[InlineKeyboardButton(sub_directory.persian_title, callback_data=f"{callback_query.data}{sub_directory.id}/")]
                    for sub_directory in sub_directories]

        for document in documents:
            keyboard.append([InlineKeyboardButton(document.persian_title, callback_data=f"rmfile-{callback_query.data.split('-')[-1]}{document.id}")])

        if len(directory_path := callback_query.data.split('/')) > 2:
            keyboard.append([InlineKeyboardButton("بازگشت به فولدر قبلی", callback_data=f"{'/'.join(directory_path[:-1])}")])
        keyboard.append([InlineKeyboardButton("حذف همین فولدر", callback_data=f"rmdir-{callback_query.data.split('-')[-1]}")])

        callback_query.message.edit_text(
            "⬅️فولدر رو انتخاب کن:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


@Client.on_callback_query(filters.user(os.environ.get('ADMIN_ID')) & filters.regex("^rmdir-(.*)/"))
def confirm_remove_dir(client: Client, callback_query: CallbackQuery):
    callback_query.message.edit_text(
        "❌ مطمعنی میخوای حذفش کنی؟",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ آره دا", callback_data=f"confrmdir-{callback_query.data.split('-')[-1]}"),
             InlineKeyboardButton("❌ نه دا", callback_data=f"rmdirls-{callback_query.data.split('-')[-1]}")]
        ])
    )


@Client.on_callback_query(filters.user(os.environ.get('ADMIN_ID')) & filters.regex("^confrmdir-(.*)/"))
def removing_directory(client: Client, callback_query: CallbackQuery):
    with Session(engine) as session:
        if callback_query.data.split('-')[-1] == 'root/':
            directories = session.scalars(select(Directory)).all()
            for directory in directories:
                shutil.rmtree(os.path.join(os.environ.get('ROOT_DIR')))
                os.makedirs(os.environ.get('ROOT_DIR'))
                session.delete(directory)
            session.commit()
        else:
            directory_id = callback_query.data.split('-')[-1].split('/')[-2]
            directory = session.scalar(select(Directory).where(Directory.id == int(directory_id)))
            shutil.rmtree(cmd_to_path(callback_query.data.split('-')[-1]))
            session.delete(directory)
            session.commit()

        callback_query.message.edit_text("☑️ تمام! فولدرت حذف شد.", reply_markup=None)



@Client.on_callback_query(filters.user(os.environ.get('ADMIN_ID')) & filters.regex("^rmfile-(.*)/"))
def confirm_remove_file(client: Client, callback_query: CallbackQuery):
    callback_query.message.edit_text(
        "❌ مطمعنی میخوای حذفش کنی؟",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ آره دا", callback_data=f"confrmfile-{callback_query.data.split('-')[-1]}"),
             InlineKeyboardButton("❌ نه دا", callback_data=f"rmdirls-{callback_query.data.split('-')[-1].split('/')[:-1]}")]
        ])
    )



@Client.on_callback_query(filters.user(os.environ.get('ADMIN_ID')) & filters.regex("^confrmfile-(.*)/"))
def removing_file(client: Client, callback_query: CallbackQuery):
    with Session(engine) as session:
        file_id = callback_query.data.split('-')[-1].split('/')[-1]
        file = session.scalar(select(Document).where(Document.id == int(file_id)))
        os.remove(os.path.join(cmd_to_path('/'.join(callback_query.data.split('-')[-1].split('/'))), file.title))
        file.user.uploaded_docs -= 1
        session.delete(file)
        session.commit()

        callback_query.message.edit_text("☑️ تمام! فایلت حذف شد.", reply_markup=None)
