import logging
import sys

from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

load_dotenv()

if __name__ == '__main__':
    logging.info('Starting the application...')

    import scripts.find_and_save_next_news as find_and_save_next_news
    import scripts.find_and_tweet_next_news as find_and_tweet_next_news

    find_and_save_next_news.run()
    find_and_tweet_next_news.run()
