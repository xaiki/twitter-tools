import signal
import sys
import re
from getopt import getopt, GetoptError

from urllib3.exceptions import ProtocolError
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import config as c

r = re.compile("\s+")

# This is the listener, resposible for receiving data
class StdOutListener(StreamListener):

    def on_status(self, status):
        tweet_url = "http://twitter.com/" + status.user.screen_name + "/status/" + status.id_str
        print "TWEET", status.text
        print "URL", tweet_url
        db.save(tweet_url, status)

    def on_error(self, status):
        print status

if __name__ == "__main__":
    opts = c.parse_args([c.CONFIG_FILE, c.IDS, c.TERMS, c.DBS])

    db = opts.db
    config = opts.config[0]
    ids = opts.ids or []
    track = opts.track or []

    l = StdOutListener()
    auth = OAuthHandler(config['consumer_key'], config['consumer_secret'])
    auth.set_access_token(config['access_token'], config['access_token_secret'])

    def signal_handler(sig, frame):
        db.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    stream = Stream(auth, l)
    print "STREAM",ids, track
    while True:
        try:
            stream.filter(follow=ids, track=track)
        except ProtocolError:
            pass
