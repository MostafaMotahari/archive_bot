from telethon import TelegramClient
import os


app = TelegramClient(
    os.environ.get('PROJECT_NAME'),
    api_id=int(os.environ.get('API_ID')),
    api_hash=os.environ.get('API_HASH'),
    bot_token=os.environ.get('BOT_TOKEN')
)

app.start()
app.run_until_disconnected()
