import json
import logging
import os
import sys
import time
import requests

current_script_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_script_dir)
news_path = os.path.join(parent_dir, "data", "news.json")

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])

MT_URGENTE_URL = "https://noticias.mturgentesys.com.br/search/all/1.json?x={0}"


def get_filtered_news():
    logging.info("Getting filtered news...")
    current_time = int(time.time())

    logging.info(
        'Getting filtered news using current_time as "{0}" -> "{1}"'.format(
            current_time, time.ctime(current_time)
        )
    )

    try:
        news = requests.get(MT_URGENTE_URL.format(current_time))

        news_json = news.json()

        news_list = [
            news_json[news_id]
            for news_id in news_json
            if news_json[news_id]["categoriaName"] != "Publicidade"
            and news_json[news_id]["subcategoriaName"] != "Falecimentos"
            and news_json[news_id]["publicar"] <= current_time
        ]

        logging.info("Found {0} filtered news".format(len(news_list)))

        return news_list
    except Exception as e:
        logging.error("Error when getting filtered news: " + e)
        return None


def run():
    news = get_filtered_news()

    logging.info("Saving filtered news...")

    logging.info("news_path: {}".format(news_path))

    if not news:
        logging.info("No news found")
        return
    try:
        with open(news_path, "w+") as news_file:
            json.dump(news, news_file)

    except Exception as e:
        logging.error("Error when saving news: " + e)
