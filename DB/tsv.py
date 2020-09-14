import os
import sys
import logging

from . import generic
from . import utils

class Driver(generic.DB):
    def __init__(self, filename=sys.stdout):
        generic.DB.__init__(self)

        self.name = "Simplest TSV driver"

        self.filename = filename
        self.open()
        
    def close(self):
        self.file.close()
        
    def open(self):
        if type(self.filename) is str:            
            exists = os.path.exists(self.filename)
            self.file = open(self.filename, 'a')
            if not exists:
                self.file.write("id\tauthor\ttext\turl")
        else:
            self.file = self.filename
            self.file.write("id\tauthor\ttext\turl")


    def saveTweet(self, status):
        text = utils.extract_text(status)

        self.file.write("\t".join((
            str(status.id),
            status.user.screen_name,
            text.replace("\n", "\\n").replace("\t", "\\t"),
            status.link
        )))
