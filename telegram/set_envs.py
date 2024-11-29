import os

bot_credentials = {
    "PROJECT_TITLE": "value1",
    "API_ID": "value2",
    "API_HASH": "value3",
    "BOT_TOKEN": "value4",
    "DB_URL": "",
    "SITE_URL": "",
}

for key, value in bot_credentials.items():
    os.environ[key] = value

