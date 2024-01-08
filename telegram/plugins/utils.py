import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import Directory
from database.engine import engine


def cmd_to_path(cmd: str):
    with Session(engine) as session:
        directory_ids = cmd.split('/')[:-1]
        print(directory_ids)
        path = ""
        for directory_id in directory_ids:
            try:
                directory = session.scalar(select(Directory).where(Directory.id == int(directory_id)))
                path += f"{directory.name}/"
            except ValueError:
                continue
    return os.environ.get('ROOT_DIR') + path
