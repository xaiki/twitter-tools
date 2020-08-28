import re
import os
import sys
import json
import csv

import argparse
import logging

from get_user_ids import fetch

from DB.multi import MultiDriver

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

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
        with open(filename) as f:
            for row in f:
                ret.append(row)
        setattr(namespace, self.dest, ret)


class LoadCSVAction(argparse.Action):
    """
    load a csv file and put it in an opt
    """

    def __call__(self, parser, namespace, filename, option_string=None):
        ret = []
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
    except ValueError:
        db_driver = arg
        filename = None
    finally:
        if db_driver == "tsv":
            from DB.tsv import Driver
            
        elif db_driver == "mysql":
            from DB.mysql import Driver

            filename = filename or "mysql://"
        elif db_driver == "sqlite":
            from DB.sqlite import Driver

            filename = filename or "twitter.sqlite"
        elif db_driver == "elasticsearch":
            from DB.elasticsearch import Driver

            filename = filename or "ec://"
        elif db_driver == "pynx":
            from DB.pynx import Driver

            filename = filename or "graph.gexf"
        else:
            logging.error(f"ERROR could not find db driver for {db_driver}")
            sys.exit(-2)

        return Driver(filename)

class LoadDBDriverAction(argparse.Action):
    """
    load a db driver by name
    """

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, [load_db_driver(v) for v in values])

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
        old_ids = getattr(namespace, self.dest) or ()
        ids = fetch(namespace.config[0], flatten([v.split(',') for v in values]))
        ids.extend(old_ids)
        setattr(namespace, self.dest, ids)
        
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
    "dest": "ids",
    "nargs": "*",
    "help": "twitter usernames, as a comma-separated list",
    "action": FetchUsersAction,
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

options = [CONFIG_FILE, IDS, USERS, TERMS, DBS]

r = re.compile(r"\s+")


def parse_args(options):
    parser = argparse.ArgumentParser(
        description="Twitter Tools: query twitter from the commandline"
    )

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
        if opts.db == DBS["default"]:
            opts.db = MultiDriver([load_db_driver(DBS["default"])])
        else:
            opts.db = MultiDriver(opts.db)
    
    return opts

if __name__ == "__main__":
    parse_args(options)
