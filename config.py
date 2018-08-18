import re
import sys
import json

from getopt import getopt, GetoptError
from random import randint

r = re.compile("\s+")
filename = None

def get_config(filename):
    d = load_json(filename)
    return d[randint(0, d.__len__() - 1)]

def o2u(option):
    args = "-%s|--%s" % (option['short'].replace(':', ''), option['long'])
    usage = option['usage'] % args
    return "\t[%s]\t%s\n" % (usage, option['doc'])

def usage(name, options):
    print "usage: %s" %name
    return reduce(lambda acc, cur: acc + o2u(cur), options, "")

def identity(a):
    return a

def load_json(filename):
    with open(filename) as data:
        return json.load(data)

def load_row_file(filename):
    ret = []
    with open(filename) as f:
        for row in f:
            ret.append(row)
    return ret

def parse_db(arg):
    try: 
        db_driver, filename = arg.split(':')
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
            print "ERROR could not find db driver for ", db_driver
            sys.exit(-2)
        return Driver(filename)

def parse_comas(arg):
    return r.sub(",", arg).split(',')

def make_short(o):
    if o.has_key('parse'): return o['short'] + ':'
    return o['short']

def make_long(o):
    if o.has_key('parse'): return o['long'] + '='
    return o['long']

def parse_args(options):
    argv = sys.argv

    if ((sys.argv[0]).find(".py") != -1):
        argv = sys.argv[1:]

    shorts = "".join(map(make_short, options))
    longs = map(make_long, options)
    sopthash = dict(map(lambda o: (o['short'], o), options))
    lopthash = dict(map(lambda o: (o['long'], o), options))
    parsed = {}

    def usage():
        print "usage: %s" % "\n".join(map(o2u, options))

    def get_key(opt):
        try:
            return sopthash[opt[1:]]
        except KeyError:
            return lopthash[opt[2:]]

    try:
        opts, args = getopt(argv, shorts, longs)
    except GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        try:
            k = get_key(opt)
            parsed.update({k['long']: k['parse'](arg)})
        except KeyError:
            print "couldn't parse arg: %s, %s" % (opt, arg)

    print "parsed: %s" % (parsed)
    return parsed

CONFIG_FILE = {'long': 'config', 'short': 'c', 'usage': '%s config.json', 'doc': 'config file', 'parse': load_json}
IDS = {'long': 'ids', 'short': 'i', 'usage': '%s "id1,id2,id3"', 'doc': 'twitter user ids', 'parse': parse_comas}
USERS = {'long': 'user', 'short': 'u', 'usage': '%s "user1,user2,usr3"', 'doc': 'twitter usernames', 'parse': parse_comas}
TERMS = {'long': 'track', 'short': 't', 'usage': '%s "term1,term2,term3"', 'doc': 'terms to track', 'parse': parse_comas}
DBS =  {'long': 'database', 'short': 'D', 'usage': '%s [mysql|sqlite|elasticsearch]', 'doc': 'database system to use', 'parse': parse_db}
options = [CONFIG_FILE, IDS, USERS, TERMS, DBS]

if __name__ == '__main__':
    parse_args(options)
