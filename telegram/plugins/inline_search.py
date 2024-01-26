import os

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, CallbackQuery, InlineQuery, InlineQueryResultCachedDocument
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import Document, Tag
from database.engine import engine


def distinct(objects: list):
    distinct_objects = []
    distinct_objects_ids = []

    for obj in objects:
        if obj.id not in distinct_objects_ids:
            distinct_objects_ids.append(obj.id)
            distinct_objects.append(obj)
    return distinct_objects

@Client.on_inline_query()
def search_document(client: Client, inline_query: InlineQuery):
    with Session(engine) as session:
        if not inline_query.query:
            return

        text_query = inline_query.query
        tags = session.scalars(select(Tag).where(Tag.name.icontains(text_query)))
        documents = session.scalars(select(Document).where(Document.persian_title.icontains(text_query)))
        all_documents = []
        
        for tag in tags:
            for doc in tag.documents:
                all_documents.append(doc)
        for doc in documents:
            all_documents.append(doc)

        all_documents = distinct(all_documents)
        results = []

        for document in all_documents:
            description = ""
            for tag in document.tags:
                description += f"#{tag.name} "

            results.append(InlineQueryResultCachedDocument(
                document_file_id=document.file_id,
                title=document.persian_title,
                description=description,
                caption="Powered by: @Qut_archive_bot"
            ))

        inline_query.answer(results)
