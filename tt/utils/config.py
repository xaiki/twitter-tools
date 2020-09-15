#!/usr/bin/env python3
import logging
import os
import json
import random

CONFIG_PATH = "~/.config/twitter-tools/config.json"
ALL_NEEDS = ['access_token', 'access_token_secret', 'consumer_key', 'consumer_secret']
OAUTH_PROVIDER_NEEDS = ['access_token', 'access_token_secret', 'callback_url']

def try_load(j):
    try:
        with open(j) as data:
            return json.load(data)
    except FileNotFoundError:
        return None
    except Exception as e:
        logging.error(f"{e} is your config file well formated ?")
        raise e

def load(paths):
    for p in paths:
        c = try_load(os.path.expanduser(p))
        CONFIG_FILENAME = p
        if c: return c

    return []
    

def __add_config(config, new_config):
    name = new_config['name']

    for i, c in enumerate(config):
        if c['name'] == name:
            logging.info('old config found, updating with new keys')
            config[i] = new_config
            return config

    return config + [new_config]

def add(config, new_config, *args, **argskw):
    logging.debug(f"adding {new_config} to {config}")
    config = __add_config(config, new_config)
    write(config, *args, **argskw)

def write(config, path = CONFIG_PATH):
    dirname = os.path.dirname(os.path.expanduser(path))
    
    if not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok = True)

    with open(os.path.expanduser(path), "w") as f:
        f.write(json.dumps(config, indent=4))

def get_random(configs, needs=ALL_NEEDS):
    random.shuffle(configs)
    while len(configs):
        c = configs.pop()

        try:
            satisfied_needs = [c[n] for n in needs]
            return c
        except KeyError as e:
            pass

    raise KeyError(f"no config satisfies needs: {needs}")
    
    

    
