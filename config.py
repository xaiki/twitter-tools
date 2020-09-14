import re
import os
import sys
import json
import csv
import importlib

import argparse
import coloredlogs, logging

from get_user_ids import fetch

from DB.multi import Driver as MultiDriver

LOGGING_FORMAT = '%(asctime)s - %(pathname)s:%(lineno)s:%(funcName)s()\n - %(levelname)s - %(message)s'
coloredlogs.install(fmt=LOGGING_FORMAT)

def flatten(lists):
    return [i for l in lists for i in l]

class LoadJSONAction(argparse.Action):
    """
    load a json file and put it in an opt
    """

    def __call__(self, parser, namespace, filename, option_string=None):
        with open(filename) as data:
            setattr(namespace, self.dest, json.load(data))


class LoadRowFileAction(argparse.Action):
    """
    load a file line by line into an opt
    """

    def __call__(self, parser, namespace, filename, option_string=None):
        ret = []
        logging.debug(f"opening {filename} as CSV")
        with open(filename) as f:
            for row in f:
                s = row.rstrip()
                if len(s): ret.append(s)
        setattr(namespace, self.dest, ret)


class LoadCSVAction(argparse.Action):
    """
    load a csv file and put it in an opt
    """

    def __call__(self, parser, namespace, filename, option_string=None):
        ret = []
        logging.debug(f"opening {filename} as CSV")
        with open(filename, "rb") as csvfile:
            reader = csv.reader(csvfile, delimiter=",", quotechar="|")
            for row in reader:
                for elem in row:
                    ret.extend(elem.strip().split(","))
        setattr(namespace, self.dest, ret)


def load_db_driver(arg):
    db_driver, filename = None, None
    try:
        db_driver, filename = arg.split(":")
    except:
        db_driver = arg
        filename = None
    finally:
        try:
            M = importlib.import_module(f"DB.{db_driver}")
        except:
            logging.error(f"ERROR could not find db driver for {db_driver}")
            sys.exit(-2)

        if filename:
            return M.Driver(filename)

        return M.Driver()

class LoadDBDriverAction(argparse.Action):
    """
    load a db driver by name
    """

    def __call__(self, parser, namespace, values, option_string=None):
        old_dbs = getattr(namespace, self.dest)
        if not isinstance(old_dbs, list):
            old_dbs = ()

        dbs = [load_db_driver(v) for v in values]

        dbs.extend(old_dbs)
        setattr(namespace, self.dest, dbs)

class ParseComasAction(argparse.Action):
    """
    Parse a coma separated arg into an array
    """

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, flatten([v.split(",") for v in values]))

class FetchUsersAction(argparse.Action):
    """
    Parse a coma separated usernames into an array of user ids
    """

    def __call__(self, parser, namespace, values, option_string=None):
        try:
            db = namespace.db
        except AttributeError:
            db = None
            
        old_ids = getattr(namespace, self.dest) or ()
        ids = fetch(namespace.config[0], flatten([v.split(',') for v in values]), db)
        ids.extend(old_ids)
        setattr(namespace, 'ids', ids)

class IncreaseVerbosityAction(argparse.Action):
    """
    up debug level
    """

    def __call__(self, parser, namespace, values, option_string=None):
        coloredlogs.increase_verbosity()
        
def load_config(paths):
    def try_load_json(j):
        try:
            with open(j) as data:
                return json.load(data)
        except FileNotFoundError:
            return None
        except Exception as e:
            logging.error(f"{e} is your config file well formated ?")
            raise e

    for p in paths:
        c = try_load_json(os.path.expanduser(p))
        if c: return c

    return []

CONFIG_FILE = {
    "flags": "-c, --config",
    "dest": "config",
    "help": "config file",
    "action": LoadJSONAction,
    "default": load_config(["./config.json", "../config.json", "~/.config/twitter-tools/config.json"])
}

IDS = {
    "flags": "-i, --ids",
    "dest": "ids",
    "nargs": "*",
    "help": "twitter user ids, as a comma-separated list",
    "action": ParseComasAction,
}
USERS = {
    "flags": "-u, --users",
    "dest": "users",
    "nargs": "*",
    "help": "twitter usernames, as a comma-separated list",
    "action": FetchUsersAction,
}
USERS_NOFETCH= {
    "flags": "-u, --users",
    "dest": "ids",
    "nargs": "*",
    "help": "twitter usernames, as a comma-separated list",
    "action": ParseComasAction,
}
TERMS = {
    "flags": "-t, --track",
    "dest": "track",
    "nargs": "*",
    "default": [],
    "help": "terms to track, as a comma-separated list",
    "action": ParseComasAction,
}
DBS = {
    "flags": "-D, --database",
    "dest": "db",
    "help": "database system to use (mysql, sqlite, elasticsearch)",
    "nargs": "*",
    "default": "tsv",
    "action": LoadDBDriverAction,
}
CSV_FILE = {
    "flags": "-f, --csv",
    "dest": "csv",
    "help": "load data from a csv file",
    "action": LoadRowFileAction,
}
DEBUG = {
    "flags": "-v",
    "help": "increase verbosity",
    "action": IncreaseVerbosityAction,
    "default": 0
}

options = [CONFIG_FILE, IDS, USERS, TERMS, DBS]

r = re.compile(r"\s+")


def parse_args(options):
    parser = argparse.ArgumentParser(
        description="Twitter Tools: query twitter from the commandline",
        allow_abbrev=False
    )

    if DBS in options:
        DBS["default"] = load_db_driver(DBS["default"])

    def add_argument(o):
        flags = o.pop("flags")
        parser.add_argument(flags, **o)

    last = options.pop()
    [add_argument(o) for o in options]

    last["flags"] = last["dest"]
    del last["dest"]

    add_argument(last)

    opts = parser.parse_args()
    if DBS in options:
        opts.db = MultiDriver(opts.db)

    return opts

if __name__ == "__main__":
    parse_args(options)
