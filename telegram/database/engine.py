import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from redis import Redis

engine = create_engine(os.environ.get("DB_URL"))
session = Session(engine)
redis = Redis('redis', port=6379)

