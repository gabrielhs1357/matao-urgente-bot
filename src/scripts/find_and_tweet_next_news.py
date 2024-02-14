import json
import logging
import os
import sys
import time

import requests
import tweepy
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI
from selenium import webdriver

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

MODEL = 'gpt-4'
BASE_PROMPT = (
    'Crie um resumo dessa notícia que chame a atenção do público. Use um emoji e duas hashtags. '
    'Sua resposta deve ter no máximo {0} caracteres. Aqui está a notícia:\n\n"{1}"')
BASE_TWEET = '{0}\n\n{1}'
MT_URGENTE_URL = 'https://noticias.mturgentesys.com.br/search/all/1.json?x={0}'
FINAL_TIME_SECONDS = 3600  # 1 hour


def get_tweepy_client():
    # App
    consumer_key = os.environ['CONSUMER_KEY']
    consumer_secret = os.environ['CONSUMER_SECRET']

    # Twitter account
    access_token = os.environ['ACCESS_TOKEN']
    access_token_secret = os.environ['ACCESS_TOKEN_SECRET']

    client = tweepy.Client(
        consumer_key=consumer_key, consumer_secret=consumer_secret,
        access_token=access_token, access_token_secret=access_token_secret
    )

    return client


def get_openai_client():
    client = OpenAI(
        api_key=os.environ['OPENAI_KEY']
    )
    return client


def get_next_news():
    current_time = int(time.time())
    final_time = current_time + FINAL_TIME_SECONDS

    logging.info(
        'Getting next minute news using current_time as "{0}" -> "{1}" and next_minute_time as "{2}" -> "{3}"'.format(
            current_time, time.ctime(current_time), final_time, time.ctime(final_time)
        ))

    try:
        news = open('src/data/news.json', 'r')

        news_json = json.load(news)

        next_minute_news_list = [
            news_item for news_item in news_json
            if current_time <= news_item['publicar'] < final_time
        ]

        logging.info('Found {0} next minute news'.format(len(next_minute_news_list)))

        return next_minute_news_list
    except Exception as e:
        logging.error('Error when getting next minute news: ' + e)
        return None


def ask_gpt(client, prompt):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    response_message = response.choices[0].message.content

    return response_message


def run():
    try:
        next_minute_news = get_next_news()

        if not next_minute_news:
            return

        client = get_tweepy_client()

        openai_client = get_openai_client()

        count = 1

        for news_item in next_minute_news:
            news_url = news_item['url']

            full_text = get_news_text(news_url)

            if not full_text:
                return

            tiny_url = get_tiny_url(news_url)

            max_characters = 278 - len(tiny_url)

            prompt = BASE_PROMPT.format(max_characters, full_text)

            response = ask_gpt(openai_client, prompt)

            tweet_message = BASE_TWEET.format(response, tiny_url)

            logging.info('Tweet message:\n' + tweet_message)

            client.create_tweet(text=tweet_message)

            if count != len(next_minute_news):  # TODO: refactor
                count += 1
                time.sleep(60)

        logging.info('Tweeted {0} new(s)!'.format(len(next_minute_news)))
    except Exception as e:
        logging.error('Error when Tweeting next minute news: ' + e)


def get_news_text(news_url):
    try:
        logging.info('Getting news text from "{0}"'.format(news_url))

        options = webdriver.ChromeOptions()

        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)

        driver.implicitly_wait(5)

        driver.get(news_url)

        driver.find_element('class name', 'show-shell')

        news_content = driver.page_source

        driver.quit()

        soup = BeautifulSoup(news_content, 'html.parser')

        paragraphs = soup.find_all('p', class_='texto')

        if not paragraphs:
            logging.info('No paragraphs with "texto" class found.')
            return

        full_text = ''

        for paragraph in paragraphs:
            full_text += paragraph.text + ' '

        return full_text

    except Exception as e:
        logging.error('Error when getting news text from "{0}": '.format(news_url), e)
        return None


def get_tiny_url(url):
    try:
        logging.info('Getting tiny url for "{0}"'.format(url))

        tiny_url_api_key = os.environ['TINY_URL_API_KEY']

        logging.info('tiny_url_api_key: ' + tiny_url_api_key)

        params = {
            'api_token': tiny_url_api_key,
        }

        json_data = {
            'url': url
        }

        tiny_url = requests.post('https://api.tinyurl.com/create', params=params, json=json_data)

        return tiny_url.json()['data']['tiny_url']
    except Exception as e:
        logging.error('Error when getting tiny url: ' + e)
