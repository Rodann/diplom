from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
from source.decorators import default_decorator


@default_decorator(errormessage='Cant crawl data from channel')
def crawl_channel(client, channel_link: str) -> list:
    # собирет последние 10 постов из канала
    if 'https://t.me/' in channel_link:
        channel_link = channel_link.replace('https://t.me/', '')
    channel_entity = client.get_entity(channel_link)
    posts = client(
        GetHistoryRequest(
            peer=channel_entity,
            limit=10,
            offset_date=None,
            offset_id=0,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0
        )
    )
    data = []
    messages = posts.messages
    for message in messages:
        data.append(message.message)
    return data
