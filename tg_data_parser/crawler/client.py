from time import sleep
from loguru import logger
from telethon.sync import TelegramClient, events
from config import api_hash, api_id


while True:
    try:
        client = TelegramClient('session_name', api_id, api_hash)
        client.start()
        break
    except Exception as e:
        logger.exception(e)
        sleep(5)
