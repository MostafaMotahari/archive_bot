import re
from pyrogram import filters


def user_cmd_regex(pattern):
    def func(flt, _, message):
        return re.compile(flt.pattern).match(message.text)
    return filters.create(func, pattern=pattern)
