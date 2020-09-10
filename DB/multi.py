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
                logging.debug(f"{d} -> {name}({args})")
                fn = None
                try:
                    fn = getattr(d, name)
                except AttributeError:
                    logging.warn(f"{d} has no attribute {name}")

                if fn: fn(*args, **kwargs)

        return wrapper

    def getTweets(self):
        return self.dbs[0].getTweets()
