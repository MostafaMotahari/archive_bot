import os
from sqlalchemy.ext.asyncio import create_async_engine
from redis import Redis

engine = create_async_engine(os.environ.get("DB_URL"))
redis = Redis('localhost', port=6379)

