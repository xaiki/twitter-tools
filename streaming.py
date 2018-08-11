import sys
import re
from getopt import getopt, GetoptError

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from config import get_config

r = re.compile("\s+")
db = "mysql"
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
        db = arg
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

if db == "mysql":
    from db_mysql import save_to_db
elif db == "sqlite":
    from db_sqlite import save_to_db
elif db == "elasticsearch":
    from db_elasticsearch import save_to_db
else:
    print "ERROR could not find db driver for ", db
    sys.exit(-2)
# This is the listener, resposible for receiving data
class StdOutListener(StreamListener):

    def on_status(self, status):
        tweet_url = "http://twitter.com/" + status.user.screen_name + "/status/" + status.id_str
        print "TWEET", status.text
        print "URL", tweet_url
        save_to_db(status.user.screen_name, status.text, tweet_url, status.id_str)

    def on_error(self, status):
        print status

if __name__ == "__main__":
    l = StdOutListener()
    auth = OAuthHandler(config['consumer_key'], config['consumer_secret'])
    auth.set_access_token(config['access_token'], config['access_token_secret'])

    stream = Stream(auth, l)
    stream.filter(follow=ids, track=track)
