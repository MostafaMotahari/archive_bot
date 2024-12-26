from os import environ
from telethon import TelegramClient

from plugins import start, panel, inline_search, support
from plugins.utils import load_caches

# with Session(engine) as session:
#     stats = Statistics()
#     session.add(stats)
#     session.commit()

# Start-up functions
# Load caches


client = TelegramClient(
    'QutArchive',
    api_id=environ.get('API_ID'),
    api_hash=environ.get('API_HASH')
)

client.add_event_handler(start.start)
client.add_event_handler(panel.panel)
client.add_event_handler(support.support)

client.start()
client.run_until_disconnected()
