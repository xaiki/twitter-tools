#!/usr/bin/env python3

import pytest
import importlib
import sys
import os
import re

if sys.version_info[0] < 3:
    raise Exception("Python 2.x is not supported. Please upgrade to 3.x")

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

BLACKLIST = ['__init__.py', '__pycache__', 'utils.py', 'generic.py', 'multi.py']
drivers = [d.replace('.py', '') for d in os.listdir('DB') if not d in BLACKLIST]

from DB import utils

TEST_DATE = "Sun Sep 13 14:21:23 +0000 2020"
TEST_USER_DESCRIPTOR = {
    'username': 'test',
    'id': 1,
    'date': TEST_DATE,
}
TEST_STATUS_DESCRIPTOR = {
    'id': 0,
    'username': 'test',
    'user_id': 42,
    'user_date': TEST_DATE,
    'text': 'test tweet',
    'date': TEST_DATE,
    'link': 'http://twitter.com/test/id',
    'to': 'me',
    'replies': 42,
    'retweets': 0,
    'favorites': 23,
    'geo': 'Buenos Aires, Argentina',
    'mentions': ['me', 'anarchy', 'freedom'],
    'hashtags': ['#fun', '#test', '#twitter-tools']
}
TEST_USER = utils.make_user(**TEST_USER_DESCRIPTOR)
TEST_STATUS = utils.make_status(**TEST_STATUS_DESCRIPTOR)

class TestUtils():
    def test_make_date(self):
        d = utils.make_date(TEST_DATE)
        
        print(d, dir(d))
        assert(d.year == 2020)

    def test_make_user(self):
        u = utils.make_user('test', 0, TEST_DATE)

        print(u, dir(u))
        assert(hasattr(u, 'screen_name'))
        assert(hasattr(u, 'id'))
        assert(hasattr(u, 'created_at'))
        
        assert(u.created_at.year == 2020)

    def test_make_status(self):
        s = utils.make_status(**TEST_STATUS_DESCRIPTOR)

        print(s, dir(s))
        assert(hasattr(s, 'user'))
        assert(hasattr(s, 'entities'))
        assert(hasattr(s, 'geo'))
        assert(hasattr(s, 'text'))
        assert(hasattr(s, 'created_at'))
        assert(hasattr(s, 'in_reply_to_screen_name'))
        assert(hasattr(s, 'link'))
        assert(hasattr(s, 'replies_count'))
        assert(hasattr(s, 'favorite_count'))
        assert(hasattr(s, 'retweet_count'))

        assert(s.created_at.year == 2020)
        
        assert(hasattr(s.user, 'screen_name'))
        assert(hasattr(s.user, 'id'))
        assert(hasattr(s.user, 'created_at'))
        
        assert(s.user.created_at.year == 2020)

        assert(hasattr(s.entities, 'hashtags'))
        assert('#fun' in s.entities.hashtags )
        
        assert(hasattr(s.entities, 'user_mentions'))
        assert('anarchy' in s.entities.user_mentions )

@pytest.mark.parametrize(
    'driver', drivers
)
class TestDrivers():
    def test_import_driver(self, driver, db_blacklist):
        if driver in db_blacklist: pytest.skip("blacklisted")
        return importlib.import_module(f"DB.{driver}")

    def test_load_driver(self, driver, db_blacklist):
        M = self.test_import_driver(driver, db_blacklist)
        return M.Driver(f"test_run.{driver}")

    def test__WIPE(self, driver, db_blacklist):
        D = self.test_load_driver(driver, db_blacklist)

        D._WIPE()

    def test_saveTweet(self, driver, db_blacklist):
        D = self.test_load_driver(driver, db_blacklist)

        D.saveTweet(TEST_STATUS)

    def test_saveAuthor(self, driver, db_blacklist):
        D = self.test_load_driver(driver, db_blacklist)
        if not hasattr(D, 'saveAuthor'):
            pytest.skip("Driver does not implement optional feature: saveAuthor")
        
        D.saveAuthor(TEST_USER)

    def test_getAuthor(self, driver, db_blacklist):
        D = self.test_load_driver(driver, db_blacklist)
        if not hasattr(D, 'getAuthor'):
            pytest.skip("Driver does not implement optional feature: getAuthor")

        a = D.getAuthor(TEST_USER.screen_name)
        assert(a[0] == TEST_USER.screen_name)

    def test_getTweets(self, driver, db_blacklist):
        D = self.test_load_driver(driver, db_blacklist)
        if not hasattr(D, 'getTweets'):
            pytest.skip("Driver does not implement optional feature: getTweets")
        
        D.getTweets()

    def test_writeSuccess(self, driver, db_blacklist):
        D = self.test_load_driver(driver, db_blacklist)
        if not hasattr(D, 'writeSuccess'):
            pytest.skip("Driver does not implement optional feature: writeSuccess")

        D.writeSuccess(0)
        
    def test_markDeleted(self, driver, db_blacklist):
        D = self.test_load_driver(driver, db_blacklist)
        if not hasattr(D, 'markDeleted'):
            pytest.skip("Driver does not implement optional feature: markDeleted")

        D.markDeleted(0)

    def test_getLogs(self, driver, db_blacklist):
        D = self.test_load_driver(driver, db_blacklist)
        if not hasattr(D, 'getLogs'):
            pytest.skip("Driver does not implement optional feature: getLogs")
        
        D.getLogs()
        
    def test__WIPE_again(self, driver, db_blacklist):
        D = self.test_load_driver(driver, db_blacklist)

        D._WIPE()

