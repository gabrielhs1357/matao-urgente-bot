import logging
import sys

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])

load_dotenv()

if __name__ == "__main__":
    logging.info("Starting the application...")

    import scripts.find_and_save_filtered_tweets as find_and_save_filtered_tweets
    import scripts.tweet_last_news as tweet_last_news

    find_and_save_filtered_tweets.run()
    tweet_last_news.run()
