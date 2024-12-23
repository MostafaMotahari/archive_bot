import os
from urllib import parse

from telethon.custom import Message
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import async_sessionmaker

from database.models import Directory, Document, BotUser
from database.engine import engine, redis


def cmd_to_path(cmd: str):
    with Session(engine) as session:
        directory_ids = cmd.split('/')[:-1]
        path = ""
        for directory_id in directory_ids:
            try:
                directory = session.scalar(select(Directory).where(Directory.id == int(directory_id)))
                path += f"{directory.name}/"
            except ValueError:
                continue
    return os.environ.get('ROOT_DIR') + path


def folder_share_link_generator(folder_id: int):
    with Session(engine) as session:
        directory = session.scalar(select(Directory).where(Directory.id == folder_id))
        share_url = f"http://t.me/Qut_archive_Bot?start=dir_{directory.id}"
        text = f"{share_url}\n\n👆با زدن رو لینک بالا میتونید محتویات فولدر '{directory.persian_title}' رو مشاهده کنید\n🔗 Shared from @Qut_archive_Bot"
        encoded_text = parse.quote(text)
        complete_url = f"tg://msg_url?url={encoded_text}"
        return complete_url


def get_absolute_file_path(file: Document):
    with Session(engine) as session:
        directory = file.directory
        path = f"/{file.title}"
        while True:
            path = f"/{directory.name}" + path
            if not directory.parent_id:
                break
            directory = session.scalar(select(Directory).where(Directory.id == directory.parent_id))
        return "/home/archive_bot/docs_repo" + path


async def anti_spam(event: Message) -> bool:
    user_cache_key = 'spam_cache_' + str(await event.from_id.user_id)
    if redis.get(user_cache_key, None):
        await event.reply('لطفاً از ارسال پیام‌های تکراری یا غیرمرتبط خودداری کنید.')
        return False
    redis.setex(user_cache_key, 1, user_cache_key)
    return True


async def load_caches():
    async with async_sessionmaker(engine, expire_on_commit=True) as session:
        users = await session.scalars(select(BotUser.user_id)).all()
        redis.sadd('cached_user_ids', list(users))
