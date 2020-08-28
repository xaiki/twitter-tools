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

def fetch(config, users):
    logging.info(f"looking for: {users}")

    api = twitter_login(config)
    handles = []
    for screen_name in users:
        try:
            u = api.get_user(screen_name)
            logging.info(f"""{screen_name} -> {u._json["id"]}""")
            handles.append(str(u._json["id"]))
        except Exception as e:
            logging.error(f"{e}, {config}")
    return handles

if __name__ == "__main__":
    opts = c.parse_args([c.CONFIG_FILE, c.CSV_FILE, c.USERS])

    config = opts.config[0]
    users = None
    try:
        users = opts.users
    except KeyError:
        users = opts.csv

    handles = fetch(config, users)

    print("\n".join(handles) + "\n")
    
