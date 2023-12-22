import re
from pyrogram import filters

from database.engine import redis


def user_cmd_regex(pattern):
    def func(flt, _, message):
        return re.compile(flt.pattern).match(redis.get(f"cmd-{message.from_user.id}").decode()) or False
    return filters.create(func, pattern=pattern)
