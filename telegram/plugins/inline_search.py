# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import async_sessionmaker
# from telethon.events import InlineQuery, register
# 
# from database.models import Document, Tag
# from database.engine import engine
# from plugins.utils import check_registration
# 
# 
# def distinct(objects: list):
#     distinct_objects = []
#     distinct_objects_ids = []
# 
#     for obj in objects:
#         if obj.id not in distinct_objects_ids:
#             distinct_objects_ids.append(obj.id)
#             distinct_objects.append(obj)
#     return distinct_objects
# 
# 
# @check_registration
# @register.on(InlineQuery)
# async def search_document(event: InlineQuery.Event):
#     async with async_sessionmaker(engine, expire_on_commit=True) as session:
#         if not event.query:
#             return
#         event.
# 
#         text_query = event.query
#         tags = session.scalars(select(Tag).where(Tag.name.icontains(text_query)))
#         documents = session.scalars(select(Document).where(Document.persian_title.icontains(text_query)))
#         all_documents = []
#         
#         for tag in tags:
#             for doc in tag.documents:
#                 all_documents.append(doc)
#         for doc in documents:
#             all_documents.append(doc)
# 
#         all_documents = distinct(all_documents)
#         results = []
# 
#         for document in all_documents:
#             description = ""
#             for tag in document.tags:
#                 description += f"#{tag.name} "
# 
#             results.append(InlineQueryResultCachedDocument(
#                 document_file_id=document.file_id,
#                 title=document.persian_title,
#                 description=description,
#                 caption="Powered by: @Qut_archive_bot"
#             ))
# 
#         event.answer(results)
