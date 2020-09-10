from . import generic
import logging

class MultiDriver(generic.DB):
    def __init__(self, databases):
        self.name = "Multiple Dispatch DB Driver"
        self.dbs = databases

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            pass

        def wrapper(*args, **kwargs):
            for d in self.dbs:
                try:
                    getattr(d, name)(*args, **kwargs)
                except AttributeError:
                    logging.warn(f"{d} has no attribute {name}")

        return wrapper

    def getTweets(self):
        return self.dbs[0].getTweets()
