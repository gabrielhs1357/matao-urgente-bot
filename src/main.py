import json
import logging
import os
import sys
import time

import requests
import schedule
import tweepy
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI
from selenium import webdriver

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

load_dotenv('../.env')

MODEL = 'gpt-4'
BASE_PROMPT = (
    'Crie um resumo dessa notícia que chame a atenção do público. Use um emoji e duas hashtags. '
    'Sua resposta deve ter no máximo {0} caracteres. Aqui está a notícia:\n\n"{1}"')
BASE_TWEET = '{0}\n\n{1}'
MT_URGENTE_URL = 'https://noticias.mturgentesys.com.br/search/all/1.json?x={0}'


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


def get_future_news():
    current_time = int(time.time())

    logging.info(
        'Getting future news using current_time as "{0}" -> "{1}"'.format(current_time, time.ctime(current_time)))

    try:
        news = requests.get(MT_URGENTE_URL.format(current_time))

        news_json = news.json()

        news_list = [
            news_json[news_id] for news_id in news_json
            if news_json[news_id]['categoriaName'] != 'Publicidade' and
               news_json[news_id]['subcategoriaName'] != 'Falecimentos' and
               news_json[news_id]['publicar'] >= current_time
        ]

        return news_list
    except Exception as e:
        logging.error('Error when getting future news: ', e)
        return None


def find_and_save_future_news():
    news = get_future_news()

    logging.info('Saving future news...')

    if not news:
        return
    try:
        with open('src/data/news.json', 'w+') as news_file:
            json.dump(news, news_file)

    except Exception as e:
        logging.error('Error when saving news: ', e)


def get_next_minute_news():
    current_time = int(time.time())
    next_minute_time = current_time + 60

    logging.info(
        'Getting next minute news using current_time as "{0}" -> "{1}" and next_minute_time as "{2}" -> "{3}"'.format(
            current_time, time.ctime(current_time), next_minute_time, time.ctime(next_minute_time)
        ))

    try:
        news = open('src/data/news.json', 'r')

        news_json = json.load(news)

        next_minute_news_list = [
            news_item for news_item in news_json
            # if current_time <= news_item['publicar'] < next_minute_time
        ]

        logging.info('Found {0} next minute news'.format(len(next_minute_news_list)))

        return next_minute_news_list
    except Exception as e:
        logging.error('Error when getting next minute news: ', e)
        return None


def tweet_next_minute_news():
    try:
        next_minute_news = get_next_minute_news()

        if not next_minute_news:
            return

        client = get_tweepy_client()

        openai_client = get_openai_client()

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

            logging.info('Tweet message:\n', tweet_message)

            client.create_tweet(text=tweet_message)

            if len(next_minute_news) > 1:
                time.sleep(5)

        logging.info('Tweeted {0} new(s)!'.format(len(next_minute_news)))
    except Exception as e:
        logging.error('Error when Tweeting next minute news: ', e)


def get_news_text(news_url):
    try:
        logging.info('Getting news text from "{0}"'.format(news_url))

        options = webdriver.ChromeOptions()

        options.add_argument("--headless=new")

        driver = webdriver.Chrome(options=options)

        driver.implicitly_wait(5)

        driver.get(news_url)

        driver.find_element('class name', 'show-shell')

        news_content = driver.page_source

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

        params = {
            'api_token': tiny_url_api_key,
        }

        json_data = {
            'url': url
        }

        tiny_url = requests.post('https://api.tinyurl.com/create', params=params, json=json_data)

        return tiny_url.json()['data']['tiny_url']
    except Exception as e:
        logging.error('Error when getting tiny url: ', e)


def run_scheduler():
    schedule.every(10).minutes.do(find_and_save_future_news)
    schedule.every().minute.do(tweet_next_minute_news)

    while True:
        schedule.run_pending()


if __name__ == '__main__':
    # find_and_save_future_news()
    tweet_next_minute_news()
    # run_scheduler()
