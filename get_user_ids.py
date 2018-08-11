from getopt import getopt, GetoptError
import tweepy
import time
import csv
import sys

from config import get_config

config = "./config.json"

if ((sys.argv[0]).find(".py") != -1):
    argv = sys.argv[1:]

def usage():
    print "usage: [-c|--config config.json] [-f|--file users.csv] [user1 [user2 [user3] ...]]"

try:
    opts, args = getopt(argv, "c:f:", ["config", "file"])
except GetoptError:
    usage()
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-c", "--config"):
        config = arg
    if opt in ("-f", "--file"):
        with open(arg, "rb") as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                for elem in row:
                    users.extend(elem.strip().split(','))

users += args

authdata = get_config(config)
print "looking for", users

auth = tweepy.OAuthHandler(authdata['consumer_key'], authdata['consumer_secret'])
auth.set_access_token(authdata['access_token'], authdata['access_token_secret'])

api = tweepy.API(auth)

def get_user_ids():
    handles = []
    for screen_name in users:
        try:
            u = api.get_user(screen_name)
            print screen_name, u._json['id']
            handles.append(str(u._json['id']))
        except Exception, e:
            print 'ERROR', e, authdata

    sys.stderr.write(' '.join(handles) + "\n")
    return handles
if __name__ == '__main__':
    get_user_ids()
