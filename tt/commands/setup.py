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

from PyInquirer import prompt, print_json, Separator
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
            'type': 'checkbox',
            'message': 'is this an user or app account ?',
            'name': 'type',
            'choices': [
                Separator('if you have access token and password'),
                { 'name': 'user', 'checked': True},
                Separator('if you have a callback URL'),
                { 'name': 'app' }
            ]
        }
    ]

    answers = prompt(questions)
    print(answers)
    answers.update(ask_consumer_tokens())

    for t in answers['type']:
        if t == 'user': answers.update(ask_access_tokens())
        if t == 'app': answers.update(ask_callback_url())

    del (answers['type'])
    return answers

def ask_consumer_tokens():
    questions = [
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
    ]

    return prompt(questions)

def ask_access_tokens():
    questions = [
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

def ask_callback_url():
    questions = [
        {
            'type': 'input',
            'message': 'what is your callback URL',
            'name': 'callback_url',
            'default': 'http://localhost:4290/oauth-authorized'
        },
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
    utils.config.write(config)


if __name__ == '__main__':
    run()
