from client.engine import client
from plugins import *
from plugins.utils import load_caches

# with Session(engine) as session:
#     stats = Statistics()
#     session.add(stats)
#     session.commit()

# Start-up functions
# Load caches

client.start()
