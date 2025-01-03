from telethon.events import NewMessage, register

from plugins.utils import assistant_decorators


@assistant_decorators
@register(NewMessage(pattern='/start'))
async def start(event: NewMessage.Event):
    await event.reply("goh")
