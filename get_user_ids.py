import tweepy
import time
import csv
import sys
import config as c

opts = c.parse_args([c.CONFIG_FILE, c.CSV_FILE, c.USERS])

authdata = opts['config'][0]
users = None
try: 
    users = opts['users']
except KeyError:
    users = opts['csv']

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
