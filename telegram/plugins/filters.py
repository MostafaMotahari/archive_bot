import re
from pyrogram import filters

from database.engine import redis


def user_cmd_regex(pattern):
    def func(flt, _, message):
        user_cmd = redis.get(f"cmd-{message.from_user.id}")
        if user_cmd:
            return re.compile(flt.pattern).match(user_cmd.decode())
        return False
    return filters.create(func, pattern=pattern)
