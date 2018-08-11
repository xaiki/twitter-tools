from random import randint
import json

def get_config(filename):
    with open(filename) as data:
        d = json.load(data)
        return d[randint(0, d.__len__() - 1)]
