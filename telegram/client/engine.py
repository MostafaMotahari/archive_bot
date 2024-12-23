from os import environ
from telethon import TelegramClient


client = TelegramClient(
    'QutArchive',
    api_id=environ.get('API_ID'),
    api_hash=environ.get('API_HASH')
)
