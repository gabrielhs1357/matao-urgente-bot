import os

import tweepy
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv('.env')

MODEL = 'gpt-4'
BASE_PROMPT = 'Crie um longo resumo sensacionalista dessa notícia usando no máximo {0} caracteres: {1}'
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

    responseMessage = response.choices[0].message.content

    return responseMessage


if __name__ == '__main__':
    print('Starting the application')

    # tweepy_client = get_tweepy_client()
    # tweepy_client.create_tweet(text="Hello, world!")
    # openai_client = get_openai_client()

    # link = 'https://site.mataourgente.com.br/noticias/1706723433/policiais-militares-abordam-condutor-de-uma-moto-frankenstein-.html'
    # max_chars = 278 - len(link)
    # prompt = BASE_PROMPT.format(max_chars, link)

    # responseMessage = ask_gpt(openai_client, prompt)
    #
    # print(responseMessage)
