import tweepy
import time
import csv
import sys
import logging

from types import SimpleNamespace

import config as c

def twitter_login(config):
    auth = tweepy.OAuthHandler(config["consumer_key"], config["consumer_secret"])
    auth.set_access_token(config["access_token"], config["access_token_secret"])

    return tweepy.API(auth)

def make_status(name, id):
    return SimpleNamespace(user=SimpleNamespace(screen_name = name, id = id))

def fetch(config, users, db):
    if not (hasattr(db, 'getAuthor') and hasattr(db, 'saveAuthor')):
        db = c.load_db_driver('sqlite')

    logging.info(f"looking for: {users} in {db}")

    api = None
    handles = []
    for screen_name in users:
        try:
            u = db.getAuthor(screen_name)

        except (KeyError, AttributeError) as e:
            logging.warn(f"{screen_name} not found in DB {db} ({e})")
            try:
                if not api: api = twitter_login(config)
                u = api.get_user(screen_name)._json['id']
                db.saveAuthor(make_status(screen_name, u))
            except Exception as e:
                logging.error(f"{e}, {config}")
                break
            
        handles.append(str(u))
        logging.info(f"{screen_name} -> {u}")
    return handles

if __name__ == "__main__":
    DB_CONFIG = c.DBS
    DB_CONFIG["default"] = "sqlite"
    
    opts = c.parse_args([DB_CONFIG, c.DEBUG, c.CONFIG_FILE, c.CSV_FILE, c.USERS, ])
    config = opts.config[0]
    ids = None
    try:
        ids = opts.ids
    except KeyError:
        ids = fetch(config, opts.csv, opts.db)

    print("\n".join(ids) + "\n")
    
