from pyrogram import Client
import os
from database.models import Statistics
from database.engine import engine
from sqlalchemy.orm import Session


app = Client(
    "Mega archive",
    api_id=os.environ.get('API_ID'),
    api_hash=os.environ.get('API_HASH'),
    bot_token=os.environ.get('BOT_TOKEN'),
    plugins=dict(root="plugins")
)

# with Session(engine) as session:
#     stats = Statistics()
#     session.add(stats)
#     session.commit()


app.run()
