import json
import os
import time

import requests
import schedule
import tweepy
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv('../.env')

MODEL = 'gpt-4'
# BASE_PROMPT = ('Crie uma chamada que chame atenção do público para essa notícia usando no máximo {0} caracteres: {1}. '
#                'Use o máximo de caracteres possíveis.')
BASE_PROMPT = 'Crie uma chamada que chame atenção do público para essa notícia usando no máximo {0} caracteres: {1}.'
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


def get_last_5_minutes_news():
    current_time = int(time.time())
    initial_time = current_time - 300

    print('current_time = ', current_time)
    print('initial_time = ', initial_time)

    # prod:
    news = requests.get(MT_URGENTE_URL.format(current_time))
    news_json = news.json()

    # local:
    # news_file = open('news.json')
    # news_json = json.load(news_file)

    news_list = [
        news_json[news_id] for news_id in news_json
        if news_json[news_id]['categoriaName'] != 'Publicidade' and
           news_json[news_id]['subcategoriaName'] != 'Falecimentos' and
           initial_time <= news_json[news_id]['publicar'] < current_time
    ]

    return news_list


def find_and_tweet_news():
    news = get_last_5_minutes_news()

    if not news:
        return

    client = get_tweepy_client()
    openai_client = get_openai_client()

    for news_item in news:
        news_url = news_item['url']

        max_characters = 278 - len(news_url)

        prompt = BASE_PROMPT.format(max_characters, news_url)

        response = ask_gpt(openai_client, prompt)

        tweet = BASE_TWEET.format(response, news_url)

        print('tweet = ', tweet)

        # prod:
        client.create_tweet(text=tweet)

        if len(news) > 1:
            time.sleep(5)


def run_scheduler():
    # prod:
    find_and_tweet_news()
    schedule.every(5).minutes.do(find_and_tweet_news)

    # dev:
    # schedule.every(5).seconds.do(find_and_tweet_news)

    while True:
        schedule.run_pending()


if __name__ == '__main__':
    run_scheduler()
