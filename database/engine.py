from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine("postgresql+psycopg2://mousiol:1234@0.0.0.0:5432/mydb")
session = Session(engine)

