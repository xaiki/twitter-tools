"""
stream tweets to database driver and stdout
"""

import signal
import sys

from urllib3.exceptions import ProtocolError
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import config as c

class StdOutListener(StreamListener):
    """
    listener, resposible for receiving data
    """
    def __init__(self, database):
        super(self)
        self.database = database

    def on_status(self, status):
        """
        a twitter status has been recieved
        """
        tweet_url = (
            "http://twitter.com/" + status.user.screen_name + "/status/" + status.id_str
        )
        print("TWEET", status.text)
        print("URL", tweet_url)
        self.database.save(tweet_url, status)

    def on_error(self, status):
        """
        error handler
        """
        print(status)

def run():
    """
    main entry point
    """
    opts = c.parse_args([c.CONFIG_FILE, c.IDS, c.TERMS, c.DBS])

    database = opts.db
    config = opts.config[0]
    ids = opts.ids or []
    track = opts.track or []

    stdout = StdOutListener(database)
    auth = OAuthHandler(config["consumer_key"], config["consumer_secret"])
    auth.set_access_token(config["access_token"], config["access_token_secret"])

    def signal_handler():
        database.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    stream = Stream(auth, stdout)
    print("STREAM", ids, track)
    while True:
        try:
            stream.filter(follow=ids, track=track)
        except ProtocolError:
            pass

if __name__ == "__main__":
    run()
