import time
import csv
import sys
import logging

from types import SimpleNamespace

import config as c
import utils

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
        sn = screen_name.lower()
        try:
            i = db.getAuthor(sn)
            if i: add_sn(sn, i)
        except (KeyError, AttributeError) as e:
            logging.warn(f"{sn} not found in DB {db} ({e})")
            need_fetch.append(sn)

    while len(need_fetch):
        if not api: api = utils.twitter_login(config)
        
        batch = need_fetch[:TWITTER_BATCH_LIMIT]
        need_fetch = need_fetch[TWITTER_BATCH_LIMIT:]

        logging.debug(f"this batch is {len(batch)}, still need to fetch {len(need_fetch)}")

        try:
            lu = api.lookup_users(user_ids = None, screen_names = batch, include_entities = False)
        except Exception as e:
            lu = []
            
        for u in lu:
            sn = u._json['screen_name'].lower()
            add_sn(sn, u._json['id'])
            batch.remove(sn)

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

    print("screen_name\tid")
    for u, i in ids:
        print(f"{u}\t{i}")
