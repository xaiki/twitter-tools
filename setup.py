#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
* ask the user for it's twitter credentials
"""
from __future__ import print_function, unicode_literals

import os
import sys
import json
import pathlib

from PyInquirer import prompt, print_json
from config import load_config

CONFIG_PATH = "~/.config/twitter-tools/config.json"
config = load_config([CONFIG_PATH])

if config:
    answers = prompt([
        {
            'type': 'confirm',
            'name': 'confirm',
            'message': f"""a config file has already been found at {CONFIG_PATH}, 
with the following configs: {[c["name"] for c in config]},
continue ?"""
        }         
    ])
    
    if not answers["confirm"]:
        sys.exit(-2)
else:
    config = []

def validate_length(n):
    def validate(l):
        if len(l) == n: return True
        if len(l) < n: return f"your input too short, (it's {len(l)}, i expect {n})"
        if len(l) > n: return f"your input too long, (it's {len(l)}, i expect {n})"
        
    return validate
    
questions = [
    {
        'type': 'input',
        'message': 'creds name',
        'name': 'name',
        'default': 'twitter-tools'
    },
    {
        'type': 'password',
        'message': 'Enter your consumer key',
        'name': 'consumer_key',
        'validate': validate_length(25)
    },
    {
        'type': 'password',
        'message': 'Enter your consumer key secret',
        'name': 'consumer_secret',
        'validate': validate_length(45)
    },
    {
        'type': 'password',
        'message': 'Enter your access token',
        'name': 'access_token_key',
        'validate': validate_length(50)
    },
    {
        'type': 'password',
        'message': 'Enter your access token secret',
        'name': 'access_token_secret',
        'validate': validate_length(45)
    }
]

answers = prompt(questions)
config.append(answers)

dirname = os.path.dirname(os.path.expanduser(CONFIG_PATH))
if not os.path.exists(dirname):
    os.mkdirs(dirname, parents = True, exist_ok = True)
    
with open(os.path.expanduser(CONFIG_PATH), "w") as f:
    f.write(json.dumps(config, indent=4))
