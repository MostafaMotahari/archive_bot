import os

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import Directory
from database.engine import engine


class KeyboardPagination:
    def __init__(self, queryset: list, obj_count: int, current_page: int):
        self.obj_count = obj_count
        self.current_page = current_page
        self.sliced_queryset = [queryset[i:i+obj_count] for i in range(0, len(queryset), obj_count)]

    def __str__(self):
        return f"{self.current_page} از {len(self.sliced_queryset)}" 

    def has_next_page(self):
        return True if self.current_page < len(self.sliced_queryset) else False

    @property
    def next_page_uri(self):
        return f"pagination_next_{self.current_page + 1}" if self.has_next_page() else None

    def has_previous_page(self):
        return True if self.current_page > 1 else False

    @property
    def previous_page_uri(self):
        return f"pagination_previous_{self.current_page - 1}" if self.has_previous_page() else None

    def get_page_objects(self):
        try:
            return self.sliced_queryset[self.current_page - 1]
        except:
            return []

    @property
    def total_pages(self):
        return len(self.sliced_queryset)


@Client.on_callback_query(filters.regex("^pagination_(.*)_(.*)_(.*)$"))
def paginator(client: Client, callback_query: CallbackQuery):
    switch_type = callback_query.data.split('_')[1]
    intended_page_number = int(callback_query.data.split('_')[2])
    directory_id = int(callback_query.data.split('_')[-1])
    path_format = callback_query.message.reply_markup.inline_keyboard[0][0].callback_data.split('-')[-1].split('/')[:-2]
    path_format = '/'.join(path_format)

    with Session(engine) as session:
        directory = session.scalar(select(Directory).where(Directory.id == directory_id))
        pagination_count = int(os.environ.get('PAGINATION_COUNT'))
        keyboard = []

        if switch_type == "next":
            queryset_paginated = KeyboardPagination(directory.sub_directories + directory.documents, pagination_count, intended_page_number)
        else:
            queryset_paginated = KeyboardPagination(directory.sub_directories + directory.documents, pagination_count, intended_page_number)

        for query_obj in queryset_paginated.get_page_objects():
            if type(query_obj) == Directory:
                keyboard.append([
                    InlineKeyboardButton(
                        f"- {query_obj.persian_title}",
                        callback_data=f"ls-{path_format}/{query_obj.id}/")
                ])
            else:
                keyboard.append([
                    InlineKeyboardButton(
                        f"+ {query_obj.persian_title}",
                        callback_data=f"dn-{path_format}/{query_obj.id}/")
                ])

        if queryset_paginated.total_pages > 1:
            pagination_row = []
            if queryset_paginated.has_next_page():
                pagination_row.append(InlineKeyboardButton("بعدی ◀️", callback_data=f"{queryset_paginated.next_page_uri}_{directory.id}"))
            pagination_row.append(InlineKeyboardButton(queryset_paginated, callback_data="page_number"))
            if queryset_paginated.has_previous_page():
                pagination_row.append(InlineKeyboardButton("▶️ قبلی", callback_data=f"{queryset_paginated.previous_page_uri}_{directory.id}"))
            keyboard.append(pagination_row)

    keyboard.append(callback_query.message.reply_markup.inline_keyboard[-1])

    callback_query.message.edit_text(
        "🗄 فولدر یا فایل مورد نظرتو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
