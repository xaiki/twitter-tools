import requests
import logging
import config as c

opts = c.parse_args([c.DBS])
db = opts.db

list_of_tweets = []


def query(url):
    r = requests.get(url)
    if r.status_code != 200:
        return True
    else:
        logging.info("Tweet still exists")


def read_database(db):
    cur = db.getTweets()
    for tweet in cur:
        list_of_tweets.append(tweet)
        logging.info(tweet)
    return list_of_tweets


def check_tweet():
    for tweet in read_database(db):
        if query(tweet[3]) is True:
            db.markDeleted(tweet[4])

            logging.info(f"tweet deleted, id is {tweet[4]}") 
            logging.info(f"url is {tweet[3]}")


if __name__ == "__main__":
    check_tweet()
