#!/usr/bin/env python3

import pytest
import utils.config
import os
import json

TEST_CONFIG_FILENAME = './test_config.json'

MOCK_CONFIG = [
    {
        'name': 'test0',
        "consumer_key": "xxxXxXxXxxXXxXxxxxxXXxXXX",
        "consumer_secret": "xxxXXXxxxxxXxXXXXxXxXXxxXXXxxxXxxxxxxXxXXXxxxxxxxx",
        "access_token": "xxxxxxxxxxXxxxxxXXXxxxxxXxXxxXxxXxXXxXxxxxXxxxxxXX",
        "access_token_secret": "XxXxXxxxXxXxxXxxXXxXxXXxxxXxXXxxxxxxXxXXXxxxx"
    },
    {
        'name': 'test1',
        "consumer_key": "XXxXxxxxxXXxXXXxxxXxXxXxx",
        "consumer_secret": "XXXxXxXXxxXXXxxxXxxxxxxXxXXXxxxxxxxxxxxXXXxxxxxXxX",
        "access_token": "xXxxXxxXxXXxXxxxxXxxxxxXXxxxxxxxxxxXxxxxxXXXxxxxxX",
        "access_token_secret": "xXxXXxxxXxXXxxxxxxXxXXXxxxxXxXxXxxxXxXxxXxxXX"
    },
]

class TestConfig():
    def assert_write_config(self, config, dest):
        utils.config.write(config, dest)
        assert(open(dest).read() == json.dumps(config, indent=4))

    def assert_load_config(self, src_config, src):
        self.assert_write_config(src_config, src)
        config = utils.config.load([src])
        assert(config == src_config)
        
    def test_write_empty_config(self,):
        self.assert_write_config([], TEST_CONFIG_FILENAME)

    def test_load_empty_config(self,):
        self.assert_load_config([], TEST_CONFIG_FILENAME)

    def test_remove_empty_config(self,):
        os.remove(TEST_CONFIG_FILENAME)

    def test_write_config(self,):
        self.assert_write_config(MOCK_CONFIG, TEST_CONFIG_FILENAME)

    def test_load_config(self,):
        self.assert_load_config(MOCK_CONFIG, TEST_CONFIG_FILENAME)
