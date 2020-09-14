#!/usr/bin/env python3
from types import SimpleNamespace
from datetime import datetime

def make_date(date):
    #"Sun Sep 13 14:21:23 +0000 2020"
    if date: return datetime.strptime(date, '%a %b %d %H:%M:%S +0000 %Y')
    return date

def make_user(username, id, date):
    return SimpleNamespace(screen_name = username, id = id, created_at = make_date(date))
    
def make_status(username, id, user_id, user_date=None,
                text=None, date=None, link=None, to=None,
                replies=0, retweets=0, favorites=0,
                geo=None, mentions=[], hashtags=[]):
    user = make_user(username, user_id, user_date)
    entities = SimpleNamespace(hashtags=hashtags, user_mentions=mentions)
    return SimpleNamespace(id=id, user=user, entities=entities,
                           geo=geo, text=text, created_at=make_date(date),
                           in_reply_to_screen_name=to, link=link,
                           replies_count=replies, favorite_count=favorites, retweet_count=retweets)

def extract_text(status):
    try:
        return status.extended_tweet.text
    except AttributeError:
        return status.text
