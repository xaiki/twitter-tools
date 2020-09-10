import logging

class DB:
    def __init__(self):
        self.name = "Generic DB Driver"

    def getAuthor(self, status):
        raise KeyError(f"{status} not found")
