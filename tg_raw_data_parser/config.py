import os
from dotenv import load_dotenv

load_dotenv()

api_id = os.getenv('TG_ID')
api_hash = os.getenv('TG_HASH')

# telegram channels /betta
channels = (
    'https://t.me/habr_com',
    'https://t.me/d_code',
    'https://t.me/exploitex'
)

# delay 4 crawler
my_host = '127.0.0.1'
get_info_delay = 60  # in minutes
