from time import sleep
from zipfile import ZipFile
from bson.json_util import dumps
from pymongo import MongoClient
from loguru import logger
import aiochan as ac
from config import base_host, base_port, client_name, channels
from source.nlp import get_keywords
from source.nlp import get_similar
from source.decorators import default_decorator, categoizing_decorator, file_decorator


while True:
    try:
        client = MongoClient(
            base_host, base_port
        )[client_name]
        channels_list = client['channels']
        articles_list = client['articles']
        category_list = client['category']
        break
    except Exception as e:
        logger.exception(e)
        sleep(5)


@default_decorator(errormessage='error in adding channels')
def add_example_channels():
    for i in channels:
        channels_list.update_one(
            filter={
                'link': i
            },
            update={"$set": {
                'link': i
            }},
            upsert=True
        )


@default_decorator(errormessage='error in adding channels')
def add_new_channel(link):
    channels_list.update_one(
        filter={
            'link': link
        },
        update={"$set": {
            'link': link
        }},
        upsert=True
    )
    return {'info': f'channel {link} added to base'}


@default_decorator(errormessage='error in deleting channels')
def remove_channel(link):
    channels_list.delete_one(
        filter={
            'link': link
        }
    )
    return {'info': f'channel {link} deleted from base'}


@default_decorator(errormessage='error in adding article to base')
def add_new_article(channel_id, text):
    result = articles_list.insert_one(document={
            'channel_id': channel_id,
            'text': text
        }
    )
    return result.inserted_id


@file_decorator
def get_all_articles():
    with ZipFile('dump.zip', 'w') as myzip:
        articles = articles_list.find({})
        with open(f'articles.json', 'w', encoding="utf-8") as file:
            file.write('[')
            for document in articles:
                file.write(dumps(document, ensure_ascii=False))
                file.write(',')
            file.write(']')
        myzip.write(f"articles.json")
    return 'dump.zip'


@file_decorator
def get_all_cats():
    with ZipFile('dump.zip', 'w') as myzip:
        categories = category_list.find({})
        with open(f'cats.json', 'w', encoding="utf-8") as file:
            file.write('[')
            for document in categories:
                file.write(dumps(document, ensure_ascii=False))
                file.write(',')
            file.write(']')
        myzip.write(f"cats.json")
    return 'dump.zip'


@default_decorator(errormessage='error in geting cats and keys')
def get_category_keyword(key_word, keys):
    name = key_word[0]
    for i in keys:
        if name == i['name']:
            return {'name': name, 'count': i['count']+1}
    return {'name': name, 'count': 1}


@categoizing_decorator
async def categorize_article(article, key_words: list, categories):
    existing = False
    max_similar = []
    article_categories = []
    channel_0 = ac.Chan()
    channel_1 = ac.Chan()
    channel_2 = ac.Chan()
    for i in categories:
        ac.go(
            get_similar(
                channel=channel_0,
                word1=key_words[0][0],
                word2=i['name']
            )
        )
        ac.go(
            get_similar(
                channel=channel_1,
                word1=key_words[1][0],
                word2=i['name']
            )
        )
        ac.go(
            get_similar(
                channel=channel_2,
                word1=key_words[2][0],
                word2=i['name']
            )
        )
        sim_0 = await channel_0.get() * key_words[0][1]
        sim_1 = await channel_1.get() * key_words[1][1]
        sim_2 = await channel_2.get() * key_words[2][1]
        similar_key = max(sim_0, sim_1, sim_2)
        # поставил так для мокращения времени
        # при полном запуске - раскомментить строки выше
        # similar_key = sim_0
        if similar_key >= 0.05:
            article_categories.append({'category_id': i['_id'], 'percent': similar_key*100})
            existing = True
            max_similar.append({
                'category': i,
                'article_id': article,
                'key_words': key_words
            })
    if existing:
        keys_upd = []
        for i in max_similar:
            for j in i['key_words']:
                keys_upd.append(get_category_keyword(j, i['category']['keys']))
            new_key_names = []
            for new_key in keys_upd:
                new_key_names.append(new_key['name'])
            for j in i['category']['keys']:
                if j['name'] not in new_key_names:
                    keys_upd.append(j)
            category_list.update_one(
                filter={'_id': i['category']['_id']},
                update={"$set": {
                    'keys': keys_upd
                }}
            )
    else:
        keys_upd = []
        for i in key_words:
            keys_upd.append({'name': i[0], 'count': 1})
        cat_id = category_list.insert_one({'name': key_words[0][0], 'keys': keys_upd})
        article_categories.append({'category_id': cat_id.inserted_id, 'percent': key_words[0][1]*100})
    return article_categories


@default_decorator(errormessage='error in adding articles or getting cats')
async def add_articles(channel_id, articles):
    # keyword example: [('полезная табличка', 0.33), ('chatgpt', 0.21), ()]
    for i in articles:
        article = articles_list.find_one({'text': i})
        if not article:
            c = ac.Chan()
            ac.go(
                get_keywords(
                    channel=c,
                    text=i
                )
            )
            article = add_new_article(channel_id, i)
            categories = category_list.find({})
            key_words = await c.get()
            articles_list.update_one(
                filter={
                    '_id': article
                },
                update={"$set": {
                    'keywords': key_words
                }},
                upsert=True
            )
            if len(key_words) < 3:
                pass
            else:
                articler_categories = await categorize_article(article, key_words, categories)
                if articler_categories:
                    articles_list.update_one(
                        filter={
                            '_id': article
                        },
                        update={"$set": {
                            'categories': articler_categories
                        }},
                        upsert=True
                    )
                else:
                    pass


@default_decorator(errormessage='error in finding articles by category')
def find_articles_bycat(category):
    response = []
    articles = articles_list.find({})
    for i in articles:
        try:
            for cat in i['categories']:
                example = category_list.find_one({'_id': cat['category_id']})
                if example['name'] == category:
                    response.append((i['text'], cat['percent']))
                    break
        except Exception as e:
            logger.warning(i['_id'])
    if len(response) > 0:
        return {
            'info': 'category finded',
            'data': sorted(response, key=lambda element: element[1], reverse=True)
        }
    else:
        return {
            'info': 'cant find that category',
            'data': []
        }
