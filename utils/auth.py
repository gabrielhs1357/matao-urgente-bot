from dotenv import load_dotenv
import os
import tweepy

load_dotenv('.env')

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']

print('CONSUMER_KEY = ' + CONSUMER_KEY)
print('CONSUMER_SECRET = ' + CONSUMER_SECRET)

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, callback='oob')
auth.secure = True
auth_url = auth.get_authorization_url()

print('Please authorize: ' + auth_url)

verifier = input('PIN: ').strip()

auth.get_access_token(verifier)

print("ACCESS_KEY = " + auth.access_token)
print("ACCESS_SECRET = " + auth.access_token_secret)
