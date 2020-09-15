#!/usr/bin/env python3
import tweepy
import config as c

import logging
from types import SimpleNamespace
from DB import utils as db_utils
TWITTER_BATCH_LIMIT = 100

def login(config):
    auth = tweepy.OAuthHandler(config["consumer_key"], config["consumer_secret"])
    auth.set_access_token(config["access_token"], config["access_token_secret"])

    api = tweepy.API(auth)
    
    # test authentication
    try:
        api.verify_credentials()
        logging.info("authentification OK")
        return api
    except:
        logging.error("Error during authentication")
        return None
    
def fetch_users(config, users, db):
    if not (hasattr(db, 'getAuthor') and hasattr(db, 'saveAuthor')):
        db = c.load_db_driver('sqlite')

    logging.info(f"looking for: {users} in {db}")

    api = None
    handles = []
    need_fetch = []

    def add_sn(screen_name, i, date):
        if i: handles.append((screen_name, i))
        db.saveAuthor(db_utils.make_user(screen_name, i, date))
    
    for screen_name in users:
        sn = screen_name.lower()
        try:
            i = db.getAuthor(sn)
            if i: handles.append(i)
        except (KeyError, AttributeError) as e:
            logging.warn(f"{sn} not found in DB {db} ({e})")
            need_fetch.append(sn)

    while len(need_fetch):
        if not api: api = login(config)
        
        batch = need_fetch[:TWITTER_BATCH_LIMIT]
        need_fetch = need_fetch[TWITTER_BATCH_LIMIT:]

        logging.debug(f"this batch is {len(batch)}, still need to fetch {len(need_fetch)}")

        try:
            lu = api.lookup_users(user_ids = None, screen_names = batch, include_entities = False)
        except Exception as e:
            lu = []
            
        for u in lu:
            sn = u._json['screen_name'].lower()
            add_sn(sn, u._json['id'], u._json['created_at'])
            batch.remove(sn)

        for sn in batch:
            add_sn(sn, None)
                    
        logging.info(handles)
    return handles
