from telethon.events import NewMessage, register

from plugins.utils import assistant_decorators


@assistant_decorators
@register(NewMessage(pattern='درباره ما'))
async def support(event: NewMessage.Event):
    await event.reply('')
