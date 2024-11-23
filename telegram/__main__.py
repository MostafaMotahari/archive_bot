from .client.client_manager import client_object, plugin_manager

if __name__ == "__main__":
    num_imported = plugin_manager()
    client_object.start()
    print(f"Number of plugins imported: {num_imported}")
    client_object.run_until_disconnected()
