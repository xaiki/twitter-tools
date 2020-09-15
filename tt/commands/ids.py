import logging

import config as c
import utils

if __name__ == "__main__":
    DB_CONFIG = c.DBS
    DB_CONFIG["default"] = "sqlite"
    
    opts = c.parse_args([DB_CONFIG, c.DEBUG, c.CONFIG_FILE, c.CSV_FILE, c.USERS, ])
    config = utils.config.get_random(opts.config)
    ids = None
    try:
        ids = opts.ids
    except KeyError:
        ids = []

    if opts.csv:
        ids.extend(utils.twitter.fetch_users(config, opts.csv, opts.db))

    print("screen_name\tid\tcreated_at")
    for u in ids:
        print("\t".join([str(i) for i in u]))
