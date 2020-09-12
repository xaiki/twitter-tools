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

TWITTER_BATCH_LIMIT = 100
    
def fetch(config, users, db):
    if not (hasattr(db, 'getAuthor') and hasattr(db, 'saveAuthor')):
        db = c.load_db_driver('sqlite')

    logging.info(f"looking for: {users} in {db}")

    api = None
    handles = []
    need_fetch = []

    def add_sn(screen_name, i):
        if i: handles.append((screen_name, i))
        db.saveAuthor(make_status(screen_name, i))
    
    for screen_name in users:
        try:
            i = db.getAuthor(screen_name)
            if i: add_sn(screen_name, i)
        except (KeyError, AttributeError) as e:
            logging.warn(f"{screen_name} not found in DB {db} ({e})")
            need_fetch.append(screen_name)

    while len(need_fetch):
        if not api: api = twitter_login(config)
        
        batch = need_fetch[:TWITTER_BATCH_LIMIT]
        need_fetch = need_fetch[TWITTER_BATCH_LIMIT:]

        try:
            lu = api.lookup_users(user_ids = None, screen_names = batch, include_entities = False)
        except Exception as e:
            lu = []
            
        for u in lu:
            add_sn(u._json['screen_name'], u._json['id'])
            batch.remove(u._json['screen_name'])

        for sn in batch:
            add_sn(sn, None)
                    
        logging.info(handles)
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
        ids = []

    if opts.csv:
        ids.extend(fetch(config, opts.csv, opts.db))

    print(ids)
