import tweepy
import time
import csv
import sys
import logging

import config as c

def twitter_login(config):
    auth = tweepy.OAuthHandler(config["consumer_key"], config["consumer_secret"])
    auth.set_access_token(config["access_token"], config["access_token_secret"])

    return tweepy.API(auth)

class MiniUser():
    def __init__(self, author, id):
        self.screen_name = author
        self.id = id
        
class MiniStatus():
    def __init__(self, author, id):
        self.user = MiniUser(author, id)

def fetch(config, users, db):
    logging.info(f"looking for: {users}")

    api = None
    handles = []
    for screen_name in users:
        try:
            u = db.getAuthor(screen_name)

        except KeyError:
            logging.warn(f"{screen_name} not found in DB {db}")
            try:
                if not api: api = twitter_login(config)
                u = api.get_user(screen_name)._json['id']
                db.saveAuthor(MiniStatus(screen_name, u))
            except Exception as e:
                logging.error(f"{e}, {config}")
                break
            
        handles.append(str(u))
        logging.info(f"{screen_name} -> {u}")
    return handles

if __name__ == "__main__":
    DB_CONFIG = c.DBS
    DB_CONFIG["default"] = c.load_db_driver("sqlite")
    
    opts = c.parse_args([DB_CONFIG, c.DEBUG, c.CONFIG_FILE, c.CSV_FILE, c.USERS, ])
    config = opts.config[0]
    ids = None
    try:
        ids = opts.ids
    except KeyError:
        ids = fetch(config, opts.csv, opts.db)

    print("\n".join(ids) + "\n")
    
