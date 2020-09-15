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

MOCK_CONFIG_ENTRY = {
        'name': 'test3',
        "consumer_key": "XxXxXxxXXxXxxxxxXXxXXXxxx",
        "consumer_secret": "XXxxXXXxxxXxxxxxxXxXXXxxxxxxxxxxxXXXxxxxxXxXXXXxXx",
        "access_token": "xXXxXxxxxXxxxxxXXxxxxxxxxxxXxxxxxXXXxxxxxXxXxxXxxX",
        "access_token_secret": "XxXxxXxxXXxXxXXxxxXxXXxxxxxxXxXXXxxxxXxXxXxxx"
}

class TestConfig():
    def assert_write_config(self, config, dest):
        utils.config.write(config, dest)
        assert(open(dest).read() == json.dumps(config, indent=4))
        return config

    def assert_load_config(self, src_config, src):
        self.assert_write_config(src_config, src)
        config = utils.config.load([src])
        assert(config == src_config)
        return config
        
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

    def test_remove_config(self,):
        os.remove(TEST_CONFIG_FILENAME)

    def test_add_config(self,):
        config = self.assert_write_config(MOCK_CONFIG, TEST_CONFIG_FILENAME)
        utils.config.add(config, MOCK_CONFIG_ENTRY, TEST_CONFIG_FILENAME)
        config = utils.config.load([TEST_CONFIG_FILENAME])
        assert(config[len(MOCK_CONFIG)] == MOCK_CONFIG_ENTRY)

    def test_random_config(self,):
        config = self.assert_write_config(MOCK_CONFIG, TEST_CONFIG_FILENAME)
        n = len(config)
        c = utils.config.get_random(config)
        assert(n == len(config))

    def test_remove_config_last(self,):
        os.remove(TEST_CONFIG_FILENAME)
