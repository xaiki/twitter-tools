#!/usr/bin/env python3

import pytest
import sys
import os

if sys.version_info[0] < 3:
    raise Exception("Python 2.x is not supported. Please upgrade to 3.x")

basedir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(os.path.join(basedir, 'tt'))

def pytest_addoption(parser):
    parser.addoption(
        "--dbblacklist", nargs="+", default=[], help="modules to ignore"
    )

@pytest.fixture
def db_blacklist(request):
    return request.config.getoption("--dbblacklist")
