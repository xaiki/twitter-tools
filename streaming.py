import signal
import sys
import re
from getopt import getopt, GetoptError

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from config import get_config

r = re.compile("\s+")
db_driver = "mysql"
ids = []
track = []
argv = sys.argv
config_file = 0

if ((sys.argv[0]).find(".py") != -1):
    argv = sys.argv[1:]

def usage():
    print "usage: [-c|--config config.json] [-f|--file id.csv] [-i|--ids id1,id2,id3...] [-t|--track hash1,hash2,hash3...] [-d|--db]"

try:
    opts, args = getopt(argv, "c:f:i:t:D:", ["config", "file", "ids", "track"])
except GetoptError:
    usage()
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-c", "--config"):
        config_file = arg
    if opt in ("-D", "--db"):
        db_driver = arg
    if opt in ("-i", "--ids"):
        ids += r.sub(",", arg).split(',')
    if opt in ("-t", "--track"):
        track += r.sub(",", arg).split(',')

    if opt in ("-f", "--file"):
        with open(arg) as f:
            for row in f:
                ids.append(row)

config = get_config(config_file)
ids += args

if db_driver == "mysql":
    from DB.mysql import Driver
    filename = filename or "mysql://"
elif db_driver == "sqlite":
    from DB.sqlite import Driver
    filename = filename or "twitter.sqlite"
elif db_driver == "elasticsearch":
    from DB.elasticsearch import Driver
    filename = filename or "ec://"
elif db_driver == "pynx":
    from DB.pynx import Driver
    filename = filename or "graph.gexf"
else:
    print "ERROR could not find db driver for ", db_driver
    sys.exit(-2)
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
    l = StdOutListener()
    auth = OAuthHandler(config['consumer_key'], config['consumer_secret'])
    auth.set_access_token(config['access_token'], config['access_token_secret'])

    db = Driver(filename)
    def signal_handler(sig, frame):
        db.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    stream = Stream(auth, l)
    stream.filter(follow=ids, track=track)
