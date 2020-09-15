#!/usr/bin/env python3

import logging
import GetOldTweets3 as got
import config as c
import utils

def run():
    """
    main entry point
    """

    GEO = {
        "flags": "-g, --geo",
        "dest": "geo",
        "nargs": "*",
        "help": "lookup for tweets near term",
    }

    WITHIN = {
        "flags": "-w, --within",
        "dest": "within",
        "nargs": "*",
        "help": "radius of the geo query",
    }
    
    opts = c.parse_args([c.CONFIG_FILE, c.DEBUG, GEO, WITHIN, c.USERS_NOFETCH, c.DBS, c.TERMS])

    database = opts.db
    config = utils.config.get_random(opts.config)

    criteria = got.manager.TweetCriteria()

    if opts.ids and len(opts.ids): criteria.setUsername(opts.ids)
    if opts.track and len(opts.track): criteria.setQuerySearch(" ".join(opts.track))
    if opts.geo: criteria.setNear(opts.geo)
    if opts.within: criteria.setNear(opts.within)

    logging.info(criteria)
    def handler(tweets):
        for t in tweets:
            print(t)
            
    got.manager.TweetManager.getTweets(criteria, handler)
    

if __name__ == "__main__":
    run()
