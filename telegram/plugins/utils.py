import os
from urllib import parse

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import Directory
from database.engine import engine


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
