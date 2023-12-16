from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from redis import Redis

engine = create_engine("postgresql+psycopg2://mousiol:1234@0.0.0.0:5432/mydb")
session = Session(engine)
redis = Redis('0.0.0.0', port=6379)

