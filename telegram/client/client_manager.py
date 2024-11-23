import os
import pkgutil
from telethon import TelegramClient


client_object = TelegramClient(
    os.environ.get('PROJECT_NAME'),
    api_id=int(os.environ.get('API_ID')),
    api_hash=os.environ.get('API_HASH'),
    bot_token=os.environ.get('BOT_TOKEN')
)

def plugin_manager():
    """Imports plugins from the directory specified by the environment variable PLUGINS_ROOT.

    Returns:
        int: The number of successfully imported plugins.
    """

    plugin_dir = os.environ.get('PLUGINS_ROOT')
    if not os.path.exists(plugin_dir):
        return 0

    plugins = []
    for importer, modname, ispkg in pkgutil.iter_modules([plugin_dir]):
        try:
            module = importer.find_module(modname).load_module(modname)
            plugins.append(module)
        except Exception as e:
            print(f"Error importing plugin {modname}: {e}")
    return len(plugins)
