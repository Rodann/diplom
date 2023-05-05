import os
from dotenv import load_dotenv

load_dotenv()

api_id = os.getenv('TG_ID')
api_hash = os.getenv('TG_HASH')
phone = os.getenv('TG_PHONE')

# mongodb
base_host = 'mongodb'
base_port = 27017
client_name = 'data_parser'

# elasticsearch
# elastic исключен из проекта в связи с тем что жрет ресурсов он много а особо функций важных не несет а те что несет можно заменить nlp

# nlp options
keywords_count = 3


# telegram channels /betta
channels = (
    'https://t.me/habr_com',
)

# delay 4 crawler
my_host = '0.0.0.0'
get_info_delay = 60  # in minutes
