def main():
    load_dotenv()

    logging.info("Starting the application...")

    import scripts.find_and_save_filtered_tweets as find_and_save_filtered_tweets
    import scripts.tweet_last_news as tweet_last_news

    news_saved = find_and_save_filtered_tweets.run()

    if news_saved:
        tweet_last_news.run()
    else:
        logging.info("No news to Tweet, skipping execution.")


if __name__ == "__main__":
    import logging
    import sys

    from dotenv import load_dotenv

    logging.basicConfig(
        level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)]
    )

    main()
