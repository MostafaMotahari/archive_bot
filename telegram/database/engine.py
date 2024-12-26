import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from redis import Redis

engine = create_async_engine(os.environ.get("DB_URL"))
session = async_sessionmaker(engine, expire_on_commit=True)
redis = Redis('localhost', port=6379)
