import json
import logging
from pathlib import Path
import time
import requests

script_directory = Path(__file__).resolve().parent
news_file_path = script_directory.parent / "data" / "news.json"

logging = logging.getLogger(__name__)

MT_URGENTE_URL = "https://noticias.mturgentesys.com.br/search/all/1.json?x={0}"


def get_filtered_news():
    logging.info("Getting filtered news...")

    current_time = int(time.time())

    logging.info(
        f"Using current timestamp: {current_time} ({time.ctime(current_time)})"
    )

    try:
        news_json = requests.get(MT_URGENTE_URL.format(current_time)).json()

        news_list = [
            news_json[news_id]
            for news_id in news_json
            if news_json[news_id]["categoriaName"] != "Publicidade"
            and news_json[news_id]["subcategoriaName"] != "Falecimentos"
            and news_json[news_id]["publicar"] <= current_time
        ]

        logging.info(f"Found {len(news_list)} news")

        return news_list

    except Exception as e:
        logging.error(f"Error when getting filtered news: {e}.")
        raise e


def run():
    news = get_filtered_news()

    logging.info(f'Saving news to "{news_file_path}..."')

    if not news:
        logging.info("No news found.")
        return False

    try:
        with open(news_file_path, "w+") as news_file:
            json.dump(news, news_file)

        logging.info("News saved successfully.")
        return True

    except Exception as e:
        logging.error("Error when saving news: " + e)
        raise e
