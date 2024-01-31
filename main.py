import tweepy
import os
from dotenv import load_dotenv

load_dotenv('.env')


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


if __name__ == '__main__':
    tweepy_client = get_tweepy_client()
    tweepy_client.create_tweet(text="Hello, world!")
