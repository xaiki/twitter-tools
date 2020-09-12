#!/usr/bin/env python3
import tweepy
import logging

def twitter_login(config):
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
