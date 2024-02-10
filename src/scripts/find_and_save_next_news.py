import json
import logging
import os
import sys
import time

import requests

current_script_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_script_dir)
news_path = os.path.join(parent_dir, 'data', 'news.json')

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

MT_URGENTE_URL = 'https://noticias.mturgentesys.com.br/search/all/1.json?x={0}'


def get_future_news():
    logging.info('Getting future news...')
    current_time = int(time.time())

    logging.info(
        'Getting future news using current_time as "{0}" -> "{1}"'.format(current_time, time.ctime(current_time)))

    try:
        news = requests.get(MT_URGENTE_URL.format(current_time))

        logging.info('news: {}'.format(news.status_code))

        news_json = news.json()

        logging.info('news_json: {}'.format(news_json))

        news_list = [
            news_json[news_id] for news_id in news_json
            if news_json[news_id]['categoriaName'] != 'Publicidade' and
               news_json[news_id]['subcategoriaName'] != 'Falecimentos' and
               news_json[news_id]['publicar'] >= current_time
        ]

        logging.info('news_list: {}'.format(news_list))

        return news_list
    except Exception as e:
        logging.error('Error when getting future news: ' + e)
        return None


def find_and_save_future_news():
    news = get_future_news()

    logging.info('Saving future news...')

    logging.info('news_path: {}'.format(news_path))

    if not news:
        logging.info('No news found')
        return
    try:
        with open(news_path, 'w+') as news_file:
            json.dump(news, news_file)

    except Exception as e:
        logging.error('Error when saving news: ' + e)


find_and_save_future_news()

# with open(news_path, 'w+') as news_file:
#     logging.info('news_path: {}'.format(news_path))
#
#     news_file.write('hello world')
