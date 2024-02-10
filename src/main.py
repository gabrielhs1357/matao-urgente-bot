import logging
import os
import sys

from dotenv import load_dotenv
from crontab import CronTab

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

load_dotenv()

if __name__ == '__main__':
    cron = CronTab(user=True)

    script_name = 'find_and_tweet_next_news.py'
    
    script_path = '/app/src/scripts/' + script_name

    logs_path = '/app/src/logs/cron.log'

    logging.info('Script name {0} -> {1} script path'.format(script_name, script_path))

    command = 'python3 {0} >> {1} 2>&1'.format(
        script_path, logs_path)

    find_and_tweet_job = cron.new(
        command=command,
        comment='find_and_tweet_next_news'
    )

    find_and_tweet_job.minute.every(1)

    cron.write()

    logging.info('Tasks scheduled!')
