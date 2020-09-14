"""
stream tweets to database driver and stdout
"""

import logging
import signal
import sys

import tweepy
from urllib3.exceptions import ProtocolError
from tweepy.streaming import StreamListener

import config as c
import utils

class StdOutListener(StreamListener):
    """
    listener, resposible for receiving data
    """
    def __init__(self, database):
        super(StdOutListener, self).__init__()
        self.database = database

    def on_status(self, status):
        """
        a twitter status has been recieved
        """

        tweet_url = (
            "http://twitter.com/" + status.user.screen_name + "/status/" + status.id_str
        )
        logging.info(f"TWEET: {tweet_url}\n{status.text}")

        status.link = tweet_url
        self.database.saveTweet(status)
        self.database.saveAuthor(status)

    def on_error(self, status):
        """
        error handler
        """
        logging.error(status)

def run():
    """
    main entry point
    """
    opts = c.parse_args([c.CONFIG_FILE, c.DEBUG, c.IDS, c.USERS, c.DBS, c.TERMS])

    database = opts.db
    config = opts.config[0]

    print (opts.ids)
    if opts.ids:
        ids = [str(i[1]) for i in opts.ids]
    else:
        ids = None
        
    stream_config = {
        "follow": ids,
        "track": opts.track or None
    }

    listener = StdOutListener(database)
    api = utils.twitter_login(config)

    def signal_handler(*argv, **argh):
        database.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    stream = tweepy.Stream(auth = api.auth, listener = listener)
    logging.info(f"STREAM: {stream_config}")
    while True:
        try:
            stream.filter(**stream_config)
        except ProtocolError:
            pass

if __name__ == "__main__":
    run()
