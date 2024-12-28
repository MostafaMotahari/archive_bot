# from pyrogram import Client, filters
# from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
# from sqlalchemy.orm import Session
# from sqlalchemy import select
# import os
# 
# from client.engine import client
# from database.engine import engine, redis
# from database.models import BotUser, Directory, Document, Statistics
# from plugins.utils import cmd_to_path
# from plugins.filters import user_cmd_regex
# 
# 
# @Client.on_message(filters.private & filters.regex("^/send_doc$") & filters.reply)
# def send_document(client: Client, message: Message):
#     if message.reply_to_message.document:
#         if message.reply_to_message.from_user.username == "Qut_archive_Bot":
#             message.reply_text("د آخه مشتی این فایلو که خودم برات فرستادم")
#             return
# 
#         new_document = message.reply_to_message.copy(os.environ.get('ADMIN_ID'), caption=f"{message.from_user.id}")
#         client.send_message(
#             os.environ.get('ADMIN_ID'),
#             "📚 جزوه ارسال شده از:\n"
#             f"{message.from_user.first_name} {message.from_user.id}",
#             reply_markup=InlineKeyboardMarkup(
#                 [[InlineKeyboardButton("✅ ثبت جزوه", callback_data=f"firstsubmitls-{new_document.id}")]]
#             ),
#             reply_to_message_id=new_document.id
#         )
# 
#         message.reply_text(
#             "✅ جزوتون برا ادمین ارسال شد!\n"
#             "ممنون ازینکه به دوستاتون کمک میکنید ❤️"
#         )
# 
#     else:
#         message.reply_text("❌لطفا این پیام رو روی یک فایل ریپلای کن")
# 
# 
# @Client.on_callback_query(filters.user(os.environ.get('ADMIN_ID')) & filters.regex("^firstsubmitls-(.*)$"))
# def submit_doc_ls(client: Client, callback_query: CallbackQuery):
#     with Session(engine) as session:
#         message_id = callback_query.data.split('-')[-1]
#         directories = session.scalars(select(Directory).where(Directory.parent_id == None)).all()
#         keyboard = [[InlineKeyboardButton(directory.persian_title, callback_data=f"submitls-{directory.id}/{message_id}/")]
#                     for directory in directories]
#         keyboard.append([InlineKeyboardButton("ثبت در اینجا", callback_data=f"submitdoc-root/{message_id}/")])
#         callback_query.message.edit_text(
#             "⬅️ محل ایجاد فولدر رو انتخاب کن:",
#             reply_markup=InlineKeyboardMarkup(keyboard)
#         )
# 
# 
# @Client.on_callback_query(filters.user(os.environ.get('ADMIN_ID')) & filters.regex("^submitls-(.*)/"))
# def submit_docs_ls_explore(client: Client, callback_query: CallbackQuery):
#     with Session(engine) as session:
#         message_id = callback_query.data.split('/')[-2]
#         directory_id = callback_query.data.split('-')[-1].split('/')[-3]
#         sub_directories = session.scalars(select(Directory).where(Directory.parent_id == int(directory_id))).all()
#         keyboard = [[InlineKeyboardButton(sub_directory.persian_title, callback_data=f"submitls-{'/'.join(callback_query.data.split('-')[-1].split('/')[:-2])}/{sub_directory.id}/{message_id}/")]
#                     for sub_directory in sub_directories]
#         if len(callback_query.data.split('/')) > 2:
#             keyboard.append([InlineKeyboardButton("بازگشت به فولدر قبلی", callback_data=f"submitls-{'/'.join(callback_query.data.split('-')[-1].split('/')[:-2])}/{message_id}/")])
#         keyboard.append([InlineKeyboardButton("ثبت در انیجا", callback_data=f"submitdoc-{callback_query.data.split('-')[-1]}")])
# 
#         callback_query.message.edit_text(
#             "⬅️ محل ایجاد فولدر رو انتخاب کن:",
#             reply_markup=InlineKeyboardMarkup(keyboard)
#         )
# 
# 
# @Client.on_callback_query(filters.regex("^submitdoc-(.*)/"))
# def submit_document_name_message(client: Client, callback_query: CallbackQuery):
#     redis.set(f"cmd-{callback_query.from_user.id}", f"submitdoc_name-{callback_query.data.split('-')[-1]}")
#     callback_query.message.edit_text(
#         "✅ بسیار خب!\n"
#         "نام فارسی و تایتل انگلیسی مد نظرتو به فرمت زیر بفرست:\n"
#         "persian_title-english_name.extention",
#         reply_markup=None
#     )
# 
# 
# @Client.on_message(filters.private & user_cmd_regex("^submitdoc_name-(.*)/") & filters.regex("(.*)-(.*)") & filters.user(os.environ.get('ADMIN_ID')))
# def submit_document(client: Client, message: Message):
#     await_message = client.send_message(message.chat.id, "درحال آپلود ...")
#     persian_title, english_name = message.text.split('-')
#     user_cmd = redis.get(f"cmd-{message.from_user.id}").decode()
#     redis.delete(f"cmd-{message.from_user.id}")
#     message_id = user_cmd.split('/')[-2]
#     directory_id = user_cmd.split('/')[-3].split('-')[-1]
#     message: Message = client.get_messages(chat_id=message.chat.id, message_ids=[int(message_id)])[0]
#     user_id = int(message.caption)
#     path_to_upload = cmd_to_path('/'.join(user_cmd.split('-')[-1].split('/')[:-1]))
#     message.download(os.path.join(path_to_upload, english_name))
#     document_size = os.path.getsize(os.path.join(path_to_upload, english_name))
# 
#     with Session(engine) as session:
#         user_obj: BotUser = session.scalar(select(BotUser).where(BotUser.user_id == user_id))
#         user_obj.uploaded_docs += 1
#         directory = session.scalar(select(Directory).where(Directory.id == int(directory_id)))
#         statistics = session.scalar(select(Statistics).where(Statistics.id == 1))
#         statistics.uploaded += document_size
# 
#         new_document = Document(
#             title=english_name,
#             persian_title=persian_title,
#             path=os.path.join(path_to_upload, english_name),
#             file_id=message.document.file_id,
#             user_id=user_obj.id,
#             user=user_obj,
#             directory_id=directory.id,
#             directory=directory
#         )
#         session.add(new_document)
#         session.commit()
# 
#     await_message.edit_text("جزوه با موفقیت ثبت شد!")
# 
#     try:
#         client.send_message(
#             user_id,
#             "✅ یکی از جزوه هایی که فرستاده بودی به آرشیو اضافه شد!\n\n"
#             "ازینکه کمک میکنی تا آرشیو کامل تری شکل بگیر ممنونم. دَمِدَم گرم 🫶\n\n"
#             "راستی میتونی با دستور /leaderboard لیست افرادی که بیشترین مشارکت رو داشتن دریافت کنی!\n\n"
#         )
#     except:
#         pass
# 
# 
# @Client.on_message(filters.private & filters.user(os.environ.get('ADMIN_ID')) & filters.regex('^/bulk_start$'))
# def bulk_start_set(client: Client, message: Message):
#     start_message_id = message.reply_to_message_id
#     redis.set(f"cmd-{message.from_user.id}", f"bulk-{start_message_id}")
#     message.reply_text("◀️ خب حالا آخرین فایلی که میخوای آپلود شه رو مشخص کن:")
# 
# 
# @Client.on_message(filters.private & filters.user(os.environ.get('ADMIN_ID')) & filters.regex('^/bulk_end$'))
# def bulk_end_set(client: Client, message: Message):
#     end_message_id = message.reply_to_message_id
#     current_cmd = redis.get(f"cmd-{message.from_user.id}").decode()
#     redis.set(f"cmd-{message.from_user.id}", f"{current_cmd}_{end_message_id}")
#     message.reply_text(
#         "📚 تعدادی فایل برای آپلود انتخاب شده. آپلود کنم؟",
#         reply_markup=InlineKeyboardMarkup(
#                 [[InlineKeyboardButton("☑️ آره", callback_data="bulkupls")]]
#             )
#         )
# 
# 
# @Client.on_callback_query(filters.user(os.environ.get('ADMIN_ID')) & filters.regex("^bulkupls$"))
# def submit_doc_ls_bulk(client: Client, callback_query: CallbackQuery):
#     with Session(engine) as session:
#         directories = session.scalars(select(Directory).where(Directory.parent_id == None)).all()
#         keyboard = [[InlineKeyboardButton(directory.persian_title, callback_data=f"submitlsbulk-{directory.id}/")]
#                     for directory in directories]
#         keyboard.append([InlineKeyboardButton("ثبت در اینجا", callback_data="submitdoc-root-bulk/")])
#         callback_query.message.edit_text(
#             "⬅️ محل ایجاد فولدر رو انتخاب کن:",
#             reply_markup=InlineKeyboardMarkup(keyboard)
#         )
# 
# 
# @Client.on_callback_query(filters.user(os.environ.get('ADMIN_ID')) & filters.regex("^submitlsbulk-(.*)/"))
# def submit_docs_ls_explore_bulk(client: Client, callback_query: CallbackQuery):
#     with Session(engine) as session:
#         directory_id = callback_query.data.split('-')[-1].split('/')[-2]
#         print(directory_id)
#         sub_directories = session.scalars(select(Directory).where(Directory.parent_id == int(directory_id))).all()
#         keyboard = [[InlineKeyboardButton(sub_directory.persian_title, callback_data=f"submitlsbulk-{'/'.join(callback_query.data.split('-')[-1].split('/')[:-1])}/{sub_directory.id}/")]
#                     for sub_directory in sub_directories]
#         if len(callback_query.data.split('/')) > 2:
#             keyboard.append([InlineKeyboardButton("بازگشت به فولدر قبلی", callback_data=f"submitlsbulk-{'/'.join(callback_query.data.split('-')[-1].split('/')[:-2])}/")])
#         elif len(callback_query.data.split('/')) == 2:
#             keyboard.append([InlineKeyboardButton("بازگشت به فولدر قبلی", callback_data=f"submitlsbulk-{callback_query.data.split('-')[-1]}")])
#         keyboard.append([InlineKeyboardButton("ثبت در انیجا", callback_data=f"submitdocbulk-{callback_query.data.split('-')[-1]}")])
#         print(keyboard)
# 
#         callback_query.message.edit_text(
#             "⬅️ محل ایجاد فولدر رو انتخاب کن:",
#             reply_markup=InlineKeyboardMarkup(keyboard)
#         )
# 
# 
# @Client.on_callback_query(filters.regex("^submitdocbulk-(.*)$") & filters.user(os.environ.get('ADMIN_ID')) & user_cmd_regex("^bulk-(.*)_(.*)$"))
# def bulk_upload_docs(client: Client, callback_query: CallbackQuery):
#     user_cmd = redis.get(f"cmd-{callback_query.from_user.id}").decode()
#     directory_id = callback_query.data.split('-')[-1].split('/')[-2]
#     first_message_id = user_cmd.split('-')[-1].split('_')[0]
#     last_message_id = user_cmd.split('-')[-1].split('_')[-1]
#     message_ids = [message_id for message_id in range(int(first_message_id), int(last_message_id) + 1)]
#     messages = client.get_messages(chat_id=callback_query.message.chat.id, message_ids=message_ids)
# 
#     with Session(engine) as session:
#         await_message = client.send_message(callback_query.message.chat.id, "درحال آپلود ...")
#         directory = session.scalar(select(Directory).where(Directory.id == int(directory_id)))
#         statistics = session.scalar(select(Statistics).where(Statistics.id == 1))
#         user = session.scalar(select(BotUser).where(BotUser.user_id == callback_query.from_user.id))
# 
#         for message in messages:
#             path_to_upload = cmd_to_path(callback_query.data.split('-')[-1])
#             print(path_to_upload)
#             print(callback_query.data)
#             message.download(path_to_upload)
#             document_size = os.path.getsize(os.path.join(path_to_upload, message.document.file_name))
#             statistics.uploaded += document_size
# 
#             new_document = Document(
#                 title=message.document.file_name,
#                 persian_title=message.document.file_name,
#                 path=os.path.join(path_to_upload, message.document.file_name),
#                 file_id=message.document.file_id,
#                 user_id=user.id,
#                 user=user,
#                 directory_id=directory.id,
#                 directory=directory
#             )
#             session.add(new_document)
# 
#         session.commit()
#         await_message.edit_text("جزوات با موفقیت ثبت شد!")
# 
#     redis.delete(f"cmd-{callback_query.message.from_user.id}")

from telethon.events import NewMessage, register

from plugins.utils import assistant_decorators


@assistant_decorators
@register(NewMessage(pattern='درباره ما'))
async def support(event: NewMessage.Event):
    await event.reply('')
