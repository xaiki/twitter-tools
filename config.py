import re
import sys
import json
import csv

import argparse


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


class LoadDBDriverAction(argparse.Action):
    """
    load a db driver by name
    """

    def __call__(self, parser, namespace, arg, option_string=None):
        try:
            db_driver, filename = arg.split(":")
        except ValueError:
            db_driver = arg
            filename = None
        finally:
            if db_driver == "mysql":
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
                print("ERROR could not find db driver for ", db_driver)
                sys.exit(-2)
        setattr(namespace, self.dest, Driver(filename))


class ParseComasAction(argparse.Action):
    """
    Parse a coma separated arg into an array
    """

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, r.sub(",", values).split(","))


CONFIG_FILE = {
    "flags": "-c, --config",
    "dest": "config",
    "help": "config file",
    "action": LoadJSONAction,
}
IDS = {
    "flags": "-i, --ids",
    "dest": "ids",
    "help": "twitter user ids, as a comma-separated list",
    "action": ParseComasAction,
}
USERS = {
    "flags": "-u, --users",
    "dest": "users",
    "help": "twitter usernames, as a comma-separated list",
    "action": ParseComasAction,
}
TERMS = {
    "flags": "-t, --track",
    "dest": "track",
    "help": "terms to track, as a comma-separated list",
    "action": ParseComasAction,
}
DBS = {
    "flags": "-D, --database",
    "dest": "db",
    "help": "database system to use (mysql, sqlite, elasticsearch)",
    "default": "sqlite",
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

    map(add_argument, options)
    return parser.parse_args()


if __name__ == "__main__":
    parse_args(options)
