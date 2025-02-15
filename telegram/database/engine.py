import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from redis import Redis

engine = create_async_engine(os.environ.get("DB_URL"))
async_session: AsyncSession = async_sessionmaker(engine, expire_on_commit=False)
redis = Redis('localhost', port=6379)
