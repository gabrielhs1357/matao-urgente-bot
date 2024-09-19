from datetime import datetime, timedelta
import json
import logging
import os
import time
import requests
import tweepy
from bs4 import BeautifulSoup
from openai import OpenAI
from selenium import webdriver

logging = logging.getLogger(__name__)

MODEL = os.environ["GPT_MODEL"]
BASE_PROMPT = (
    "Crie um resumo dessa notícia que chame a atenção do público. Use um emoji e duas hashtags. "
    f'Sua resposta deve ter no máximo {0} caracteres. Aqui está a notícia: "{1}"'
)
BASE_TWEET = "{0}\n\n{1}"
MT_URGENTE_URL = "https://noticias.mturgentesys.com.br/search/all/1.json?x={0}"


def get_tweepy_client():
    # App
    consumer_key = os.environ["CONSUMER_KEY"]
    consumer_secret = os.environ["CONSUMER_SECRET"]

    # Twitter account
    access_token = os.environ["ACCESS_TOKEN"]
    access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]

    client = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )

    return client


def get_openai_client():
    client = OpenAI(api_key=os.environ["OPENAI_KEY"])

    if not client.api_key:
        raise ValueError("OPENAI_KEY is not set in the environment variables.")

    return client


def get_last_hour_news():
    logging.info("Getting last hour news...")

    current_datetime = datetime.now()

    # Final da última hora
    final_datetime = current_datetime.replace(minute=0, second=0, microsecond=0)
    final_epoch = int(final_datetime.timestamp())

    # Início da última hora
    start_datetime = final_datetime - timedelta(hours=1)
    start_epoch = int(start_datetime.timestamp())

    logging.info(f"Final datetime: {final_datetime} - Final epoch: {final_epoch}")
    logging.info(f"Start datetime: {start_datetime} - Start epoch: {start_epoch}")

    try:
        news = open("src/data/news.json", "r")

        news_json = json.load(news)

        last_hour_news_list = [
            news_item
            for news_item in news_json
            # if start_epoch <= news_item["publicar"] < final_epoch
        ]

        logging.info(f"Found {len(last_hour_news_list)} last news.")

        return last_hour_news_list

    except Exception as e:
        logging.error(f"Error when getting last hour news: {e}.")
        raise e


def ask_gpt(client, prompt):
    response = client.chat.completions.create(
        model=MODEL, messages=[{"role": "user", "content": prompt}]
    )

    response_message = response.choices[0].message.content

    return response_message


def get_news_text(news_url):
    try:
        logging.info(f'Getting news text from "{news_url}"...')

        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(5)
        driver.get(news_url)
        driver.find_element("class name", "show-shell")

        news_content = driver.page_source

        driver.quit()

        soup = BeautifulSoup(news_content, "html.parser")
        paragraphs = soup.find_all("p", class_="texto")

        if not paragraphs:
            raise ValueError("No paragraphs with 'texto' class found.")

        full_text = " ".join(paragraph.text for paragraph in paragraphs)

        logging.info(f'Succesfully got news text from "{news_url}".')

        return full_text

    except Exception as e:
        logging.error(f'Error when getting news text from "{news_url}": {e}')
        raise e


def get_tiny_url(url):
    try:
        logging.info(f'Getting shortened url for "{url}"...')

        tiny_url_api_key = os.environ["TINY_URL_API_KEY"]

        if not tiny_url_api_key:
            raise ValueError(
                "TINY_URL_API_KEY is not set in the environment variables."
            )

        params = {
            "api_token": tiny_url_api_key,
        }

        json_data = {"url": url}

        tiny_url = requests.post(
            "https://api.tinyurl.com/create", params=params, json=json_data
        )

        response_json = tiny_url.json()

        tiny_url = response_json["data"]["tiny_url"]

        if not tiny_url:
            raise ValueError(f'Could not generate Tiny URL for "{url}".')

        return tiny_url

    except Exception as e:
        logging.error(f'Error when getting shortened url for "{url}": {e}')
        raise e


def build_tweet_content(news_url):
    news_text = get_news_text(news_url)

    tiny_url = get_tiny_url(news_url)

    max_characters = 278 - len(tiny_url)

    prompt = BASE_PROMPT.format(max_characters, news_text)

    openai_client = get_openai_client()

    response = ask_gpt(openai_client, prompt)

    tweet_content = BASE_TWEET.format(response, tiny_url)

    return tweet_content


def run():
    try:
        last_news = get_last_hour_news()

        if not last_news:
            logging.info("Skipping Tweeting last news execution.")
            return

        client = get_tweepy_client()

        for index, news_item in enumerate(last_news, start=1):
            url = news_item["url"]

            tweet_content = build_tweet_content(url)

            logging.info(f"Tweet content:\n{tweet_content}")

            client.create_tweet(text=tweet_content)

            if index < len(last_news):
                logging.info(
                    f"Waiting 5 minutes before tweeting the next news ({index}/{len(last_news)})..."
                )
                time.sleep(300)  # 5 minutos

        logging.info(f"Successfully Tweeted {len(last_news)} new(s)!")

    except Exception as e:
        logging.error(f"Error when Tweeting last news:{e}.")
        raise e
