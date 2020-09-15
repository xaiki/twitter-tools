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
import utils
import config as c
        
def should_overwrite(config):
    answers = prompt([
        {
            'type': 'confirm',
            'name': 'confirm',
            'message': f"""a config file has already been found with the following configs:
            {[c["name"] for c in config]},
            continue ?"""
            }         
        ])

    return answers["confirm"]

def validate_length(n):
    def validate(l):
        if len(l) == n: return True
        if len(l) < n: return f"your input too short, (it's {len(l)}, i expect {n})"
        if len(l) > n: return f"your input too long, (it's {len(l)}, i expect {n})"

    return validate

def ask_config_entry():
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

    return prompt(questions)


def run():
    opts = c.parse_args([c.DEBUG, c.CONFIG_FILE])
    config = opts.config

    if config:
        if not should_overwrite(config):
            sys.exit(-2)
    else:
        config = []

        
    config.append(ask_config_entry())
    utils.write_config(config)


if __name__ == '__main__':
    run()
