import os

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import Statistics, Directory, Document
from database.engine import engine
from plugins.keyboard_pagination import KeyboardPagination
from plugins.utils import folder_share_link_generator


@Client.on_message(filters.private & filters.regex("^📖 لیست رشته ها 📖$"))
def show_study_fields(client: Client, message: Message):
    with Session(engine) as session:
        parent_directories = session.scalars(select(Directory).where(Directory.parent_id == None)).all()
        keyboard = [[InlineKeyboardButton(directory.persian_title, callback_data=f"lskeyboard-{directory.id}")]
                    for directory in parent_directories]
        message.reply_text( "رشته تون رو انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))


@Client.on_callback_query(filters.regex("^show_root_dir$"))
def show_root_dir(client: Client, callback_query: CallbackQuery):
    with Session(engine) as session:
        parent_directories = session.scalars(select(Directory).where(Directory.parent_id == None)).all()
        keyboard = [[InlineKeyboardButton(directory.persian_title, callback_data=f"lskeyboard-{directory.id}")]
                    for directory in parent_directories]
        callback_query.message.edit_text( "رشته تون رو انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))


@Client.on_callback_query(filters.regex("^lskeyboard-(.*)$"))
def show_folder_content(client: Client, callback_query: CallbackQuery=None, message: Message=None, parsed_directory_id: str=None):
    directory_id = parsed_directory_id or callback_query.data.split('-')[-1]
    with Session(engine) as session:
        directory = session.scalar(select(Directory).where(Directory.id == int(directory_id)))
        pagination_count = int(os.environ.get('PAGINATION_COUNT'))
        keyboard = []

        queryset_paginated = KeyboardPagination(directory.sub_directories + directory.documents, pagination_count, 1, 'keyboard')
        for query_obj in queryset_paginated.get_page_objects():
            if type(query_obj) == Directory:
                keyboard.append([
                    InlineKeyboardButton(
                        f"- {query_obj.persian_title}",
                        callback_data=f"lskeyboard-{query_obj.id}")
                ])
            else:
                keyboard.append([
                    InlineKeyboardButton(
                        f"+ {query_obj.persian_title}",
                        callback_data=f"dn-{query_obj.id}")
                ])

        if queryset_paginated.total_pages > 1:
            pagination_row = []
            if queryset_paginated.has_next_page():
                pagination_row.append(InlineKeyboardButton("بعدی ◀️", callback_data=f"{queryset_paginated.next_page_uri}_{directory.id}"))
            pagination_row.append(InlineKeyboardButton(queryset_paginated, callback_data="page_number"))
            if queryset_paginated.has_previous_page():
                pagination_row.append(InlineKeyboardButton("▶️ قبلی", callback_data=f"{queryset_paginated.previous_page_uri}_{directory.id}"))
            keyboard.append(pagination_row)
            
    # Place return button
        if not directory.parent:
            keyboard.append([
                InlineKeyboardButton("🔝 برگشت به فولدر قبلی 🔝", callback_data="show_root_dir")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("🔝 برگشت به فولدر قبلی 🔝", callback_data=f"lskeyboard-{directory.parent.id}")
            ])

        keyboard.append([
            InlineKeyboardButton("🔗 اشتراک گذاری این فولدر🔗", url=folder_share_link_generator(int(directory_id)))
        ])

    if callback_query:
        callback_query.message.edit_text(
            "🗄 فولدر یا فایل مورد نظرتو انتخاب کن:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        message.reply_text(
            "🗄 فولدر یا فایل مورد نظرتو انتخاب کن:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


@Client.on_callback_query(filters.regex("^dn-(.*)$"))
def download_content(client: Client, callback_query: CallbackQuery):
    with Session(engine) as session:
        document_id = callback_query.data.split('-')[-1]
        document = session.scalar(select(Document).where(Document.id == int(document_id)))
        document_size = os.path.getsize(document.path)
        document.download_count = 1 if not document.download_count else document.download_count + 1

        bot_stats = session.scalar(select(Statistics).where(Statistics.id == 1))
        bot_stats.downloaded += document_size
        session.commit()

        callback_query.message.delete()
        msg = client.send_message(callback_query.message.chat.id, "درحال آپلود فایل ...")

        client.send_document(
            callback_query.message.chat.id,
            document.file_id or document.path,
            caption=f"{document.persian_title}\n{int(document_size / 1000000)} MB\n"
            f"{document.download_count} بار دانلود شده"
        )
        msg.delete()
