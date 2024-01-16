from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy.orm import Session
from sqlalchemy import select, exists
import os

from database.engine import engine
from database.models import Tag, Document, Directory
from plugins.keyboard_pagination import KeyboardPagination


@Client.on_message(filters.private & filters.user(os.environ.get("ADMIN_ID")) & filters.regex("^/add_tags "))
def get_tags(client: Client, message: Message):
    with Session(engine) as session:
        tags = message.text.split(" ")[-1].split("-")
        created_tags = []
        for tag in tags:
            if not session.scalar(exists(select(Tag).where(Tag.name == tag)).select()):
                tag_obj = Tag(name=tag)
                session.add(tag_obj)
                created_tags.append(tag)
        session.commit()

    text = "🔗 تگ های زیر ساخته شدند:\n"
    for created_tag in created_tags:
        text += f"`- {created_tag}`\n"
        
    message.reply_text(text)


@Client.on_message(filters.private & filters.user(os.environ.get("ADMIN_ID")) & filters.regex("^/remove_tags "))
def remove_tags(client: Client, message: Message):
    with Session(engine) as session:
        tags = message.text.split(" ")[-1].split("-")
        removed_tags = []
        for tag in tags:
            if session.scalar(exists(select(Tag).where(Tag.name == tag)).select()):
                tag_obj = session.scalar(select(Tag).where(Tag.name == tag))
                session.delete(tag_obj)
                removed_tags.append(tag)
        session.commit()

    text = "🔗 تگ های زیر حذف شدند:\n"
    for removed_tag in removed_tags:
        text += f"`- {removed_tag}`\n"
        
    message.reply_text(text)


@Client.on_message(filters.private & filters.user(os.environ.get("ADMIN_ID")) & filters.regex("^/manage_tags$"))
def manage_tags(client: Client, message: Message):
    with Session(engine) as session:
        parent_directories = session.scalars(select(Directory).where(Directory.parent_id == None)).all()
        keyboard = [[InlineKeyboardButton(directory.persian_title, callback_data=f"lstags-{directory.id}")]
                    for directory in parent_directories]
        message.reply_text( "📑 برو به محل فایل:", reply_markup=InlineKeyboardMarkup(keyboard))


@Client.on_callback_query(filters.regex("^show_root_folder_tags$"))
def show_root_dir(client: Client, callback_query: CallbackQuery):
    with Session(engine) as session:
        parent_directories = session.scalars(select(Directory).where(Directory.parent_id == None)).all()
        keyboard = [[InlineKeyboardButton(directory.persian_title, callback_data=f"lstags-{directory.id}")]
                    for directory in parent_directories]
        callback_query.message.edit_text( "رشته تون رو انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))


@Client.on_callback_query(filters.regex("^lstags-(.*)$") & filters.user(os.environ.get("ADMIN_ID")))
def show_folder_content_for_tags(client: Client, callback_query: CallbackQuery):
    with Session(engine) as session:
        directory_id = callback_query.data.split('-')[-1]
        directory = session.scalar(select(Directory).where(Directory.id == int(directory_id)))
        pagination_count = int(os.environ.get('PAGINATION_COUNT'))
        keyboard = []

        queryset_paginated = KeyboardPagination(directory.sub_directories + directory.documents, pagination_count, 1, 'tags')
        for query_obj in queryset_paginated.get_page_objects():
            if type(query_obj) == Directory:
                keyboard.append([
                    InlineKeyboardButton(
                        f"- {query_obj.persian_title}",
                        callback_data=f"lstags-{query_obj.id}")
                ])
            else:
                keyboard.append([
                    InlineKeyboardButton(
                        f"+ {query_obj.persian_title}",
                        callback_data=f"showtags-{query_obj.id}")
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
        if directory.parent:
            keyboard.append([
                InlineKeyboardButton("🔝 برگشت به فولدر قبلی 🔝", callback_data=f"lstags-{directory.parent.id}")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("🔝 برگشت به فولدر قبلی 🔝", callback_data="show_root_folder_tags")
            ])


    callback_query.message.edit_text(
        "📑 برو به محل فایل:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@Client.on_callback_query(filters.regex("^showtags-(.*)$") & filters.user(os.environ.get("ADMIN_ID")))
def show_file_tags(client: Client, callback_query: CallbackQuery):
    with Session(engine) as session:
        document_id = callback_query.data.split('-')[-1]
        document = session.scalar(select(Document).where(Document.id == int(document_id)))
        all_tags = session.scalars(select(Tag)).all()
        keyboard = []

        if document.tags:
            sliced_doc_tags = [document.tags[i:i+3] for i in range(0, len(document.tags), 3)]
            for row in sliced_doc_tags:
                keyboard.append([InlineKeyboardButton(f"✅ {tag.name}", callback_data=f"rmtag-{tag.id}-{document_id}") for tag in row])

        sliced_tags = [all_tags[i:i+3] for i in range(0, len(all_tags), 3)]
        for row in sliced_tags:
            keyboard.append([InlineKeyboardButton(tag.name, callback_data=f"mktag-{tag.id}-{document_id}") for tag in row if tag not in document.tags])

        callback_query.message.edit_text("🔗تگ هارو مدیریت کن:", reply_markup=InlineKeyboardMarkup(keyboard))


@Client.on_callback_query(filters.regex("^mktag-(.*)-(.*)$") & filters.user(os.environ.get("ADMIN_ID")))
def make_tag(client: Client, callback_query: CallbackQuery):
    with Session(engine) as session:
        tag_id = callback_query.data.split('-')[-2]
        tag = session.scalar(select(Tag).where(Tag.id == tag_id))
        document_id = callback_query.data.split('-')[-1]
        document = session.scalar(select(Document).where(Document.id == document_id))
        document.tags.append(tag)
        session.commit()
        all_tags = session.scalars(select(Tag)).all()
        keyboard = []

        if document.tags:
            sliced_doc_tags = [document.tags[i:i+3] for i in range(0, len(document.tags), 3)]
            for row in sliced_doc_tags:
                keyboard.append([InlineKeyboardButton(f"✅ {tag.name}", callback_data=f"rmtag-{tag.id}-{document_id}") for tag in row])

        sliced_tags = [all_tags[i:i+3] for i in range(0, len(all_tags), 3)]
        for row in sliced_tags:
            keyboard.append([InlineKeyboardButton(tag.name, callback_data=f"mktag-{tag.id}-{document_id}") for tag in row if tag not in document.tags])

        callback_query.message.edit_text("🔗تگ هارو مدیریت کن:", reply_markup=InlineKeyboardMarkup(keyboard))


@Client.on_callback_query(filters.regex("^rmtag-(.*)-(.*)$") & filters.user(os.environ.get("ADMIN_ID")))
def remove_tag(client: Client, callback_query: CallbackQuery):
    with Session(engine) as session:
        tag_id = callback_query.data.split('-')[-2]
        tag = session.scalar(select(Tag).where(Tag.id == tag_id))
        document_id = callback_query.data.split('-')[-1]
        document = session.scalar(select(Document).where(Document.id == document_id))
        document.tags.remove(tag)
        session.commit()
        all_tags = session.scalars(select(Tag)).all()
        keyboard = []

        if document.tags:
            sliced_doc_tags = [document.tags[i:i+3] for i in range(0, len(document.tags), 3)]
            for row in sliced_doc_tags:
                keyboard.append([InlineKeyboardButton(f"✅ {tag.name}", callback_data=f"rmtag-{tag.id}-{document_id}") for tag in row])

        sliced_tags = [all_tags[i:i+3] for i in range(0, len(all_tags), 3)]
        for row in sliced_tags:
            keyboard.append([InlineKeyboardButton(tag.name, callback_data=f"mktag-{tag.id}-{document_id}") for tag in row if tag not in document.tags])

        callback_query.message.edit_text("🔗تگ هارو مدیریت کن:", reply_markup=InlineKeyboardMarkup(keyboard))
