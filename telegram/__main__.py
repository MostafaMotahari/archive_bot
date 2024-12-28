from os import environ
@assistant_decorators(anti_spam=True)
@assistant_decorators(anti_spam=True)
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
