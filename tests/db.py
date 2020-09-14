#!/usr/bin/env python3

import pytest
import os

drivers = [d for d in os.listdir('/../DB') if not d.match('(__init__|pycache|utils)')]


class TestDrivers():
    @pytest.mark.parametrize(
        'driver', drivers
    )

    def print_driver(self, driver):
        print(driver)
