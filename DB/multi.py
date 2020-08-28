from . import generic
import logging

class MultiDriver(generic.DB):
    def __init__(self, databases):
        self.name = "Multiple Dispatch DB Driver"
        self.dbs = databases

    def getTweets(self):
        return self.dbs[0].getTweets()

    def writeSuccess(self, path):
        return [d.writeSuccess(path) for d in self.dbs]

    def markDeleted(self, path):
        return [d.markDeleted(path) for d in self.dbs]

    def getLogs(self):
        return [d.getLogs() for d in self.dbs]

    def save(self, url, status):
        return [d.save(url, status) for d in self.dbs]
