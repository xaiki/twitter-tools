#!/usr/bin/env python3

import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--dbblacklist", nargs="+", default=[], help="modules to ignore"
    )

@pytest.fixture
def db_blacklist(request):
    return request.config.getoption("--dbblacklist")
