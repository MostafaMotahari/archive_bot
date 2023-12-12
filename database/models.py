from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Boolean


Base = declarative_base()
metadata = Base.metadata


class BotUser(Base):
    __tablename__ = "bot_user"

    id = Column(Integer, unique=True, primary_key=True)
    user_id = Column(Integer, unique=True, index=True)
    uploaded_docs = Column(Integer, default=0)
    is_ban = Column(Boolean, default=False)


class Statistics(Base):
    __tablename__ = "statistics"

    id = Column(Integer, unique=True, primary_key=True)
    users_count = Column(Integer, default=0)
    download = Column(Integer, default=0)
