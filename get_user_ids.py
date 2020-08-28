import tweepy
import time
import csv
import sys
import config as c


def twitter_login():
    opts = c.parse_args([c.CONFIG_FILE, c.CSV_FILE, c.USERS])

    authdata = opts.config[0]
    users = None
    try:
        users = opts.users
    except KeyError:
        users = opts.csv

    sys.stderr.write(f"looking for: {users}")


    auth = tweepy.OAuthHandler(authdata["consumer_key"], authdata["consumer_secret"])
    auth.set_access_token(authdata["access_token"], authdata["access_token_secret"])

    return tweepy.API(auth), users


if __name__ == "__main__":
    api, users = twitter_login()
    handles = []
    for screen_name in users:
        try:
            u = api.get_user(screen_name)
            sys.stderr.write(f"""\n{screen_name} -> {u._json["id"]}""")
            handles.append(str(u._json["id"]))
        except Exception as e:
            sys.stderr.write(f"ERROR: {e}, {authdata}")

    print("\n".join(handles) + "\n")
    
