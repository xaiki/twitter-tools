#!/usr/bin/env python3

import logging
import config as c
import utils

def run():
    """
    main entry point
    """

    UNBLOCK = {
        "flags": "-U, --unblock",
        "dest": "unblock",
        "help": "unblock operation",
        "action": "count",
        "default": 0
    }
    
    opts = c.parse_args([c.CONFIG_FILE, c.DEBUG, UNBLOCK, c.CSV_FILE, c.IDS, c.USERS])
    config = utils.config.get_random(opts.config)

    if not len(opts.ids):
        return logging.error("need to provide at least one id")
    
    api = utils.twitter.login(config)

    print(opts.unblock)
    if opts.unblock:
        op = api.destroy_block
        action = "unblocked"
    else:
        op = api.create_block
        action = "blocked"

    for u, i in opts.ids:
        try:
            op(user_id=i)
        except Exception as e:
            logging.error(f"{op}({i}) -> [{u}] failed with error {e}")

    logging.info(f"all done, {action} {len(opts.ids)}")

if __name__ == "__main__":
    run()
