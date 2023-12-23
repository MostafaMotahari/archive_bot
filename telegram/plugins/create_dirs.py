import os

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import Directory
from database.engine import engine, redis
from plugins.utils import cmd_to_path
from plugins.filters import user_cmd_regex


@Client.on_message(filters.private & filters.user(os.environ.get('ADMIN_ID')) & filters.regex("^/create_dir$"))
def create_directory(client: Client, message: Message):
    with Session(engine) as session:
        directories = session.scalars(select(Directory).where(Directory.parent_id == None)).all()
        keyboard = [[InlineKeyboardButton(directory.persian_title, callback_data=f"mkdirls-{directory.id}/")]
                    for directory in directories]
        keyboard.append([InlineKeyboardButton("ساخت فولدر همینجا", callback_data="mkdir-root/")])
        message.reply_text(
            "⬅️ محل ایجاد فولدر رو انتخاب کن:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


@Client.on_callback_query(filters.user(os.environ.get('ADMIN_ID')) & filters.regex("^mkdirls-(.*)/"))
def makedir_ls(client: Client, callback_query: CallbackQuery):
    with Session(engine) as session:
        directory_id = callback_query.data.split('-')[-1].split('/')[-2]
        sub_directories = session.scalars(select(Directory).where(Directory.parent_id == int(directory_id))).all()
        keyboard = [[InlineKeyboardButton(sub_directory.persian_title, callback_data=f"{callback_query.data}{sub_directory.id}/")]
                    for sub_directory in sub_directories]
        if len(directory_path := callback_query.data.split('/')) > 1:
            keyboard.append([InlineKeyboardButton("بازگشت به فولدر قبلی", callback_data=f"{'/'.join(directory_path[:-1])}")])
        keyboard.append([InlineKeyboardButton("ساخت فولدر همینجا", callback_data=f"mkdir-{callback_query.data.split('-')[-1]}")])

        callback_query.message.edit_text(
            "⬅️ محل ایجاد فولدر رو انتخاب کن:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


@Client.on_callback_query(filters.user(os.environ.get('ADMIN_ID')) & filters.regex("^mkdir-(.*)/"))
def makedir(client: Client, callback_query: CallbackQuery):
    redis.set(f"cmd-{callback_query.from_user.id}", f"makedir_name-{callback_query.data.split('-')[-1]}")

    callback_query.message.edit_text(
        "✅ بسیار خب!\n"
        "نام فارسی و تایتل انگلیسی مد نظرتو به فرمت زیر بفرست:\n"
        "persian_title-english_name",
        reply_markup=None
    )


@Client.on_message(filters.private & filters.user(os.environ.get('ADMIN_ID')) & filters.regex("(.*)-(.*)") & user_cmd_regex("^makedir_name-(.*)"))
def naming_made_directory(client: Client, message: Message):
    with Session(engine) as session:
        persian_title, title = message.text.split('-')
        user_cmd = redis.get(f"cmd-{message.from_user.id}").decode()

        if user_cmd.split('-')[-1] == 'root/':
            directory = Directory( name=title, persian_title=persian_title)
            path = os.path.join(os.environ.get('ROOT_DIR'), title)
        else:
            parent_directory = user_cmd.split('-')[-1].split('/')[-2]
            parent_directory_obj = session.scalar(select(Directory).where(Directory.id == int(parent_directory)))
            directory = Directory( name=title, persian_title=persian_title, parent=parent_directory_obj)
            directory_path = cmd_to_path(user_cmd.split('-')[-1])
            path = os.path.join(directory_path, title)

        os.mkdir(path)
        redis.delete(f"cmd-{message.from_user.id}")
        session.add(directory)
        session.commit()

        message.reply_text("☑️ تمام! فولدرت ساخته شد.")
