import sys
import logging

from . import generic

class Driver(generic.DB):
    def __init__(self, filename=sys.stdout):
        generic.DB.__init__(self)

        self.name = "Simplest TSV driver"
        self.filename = filename

        print("id\tauthor\ttext\turl")

    def saveTweet(self, url, status):
        try:
            text = status.extended_tweet.text
        except AttributeError:
            text = status.text

        print("\t".join((
            status.id_str,
            status.user.screen_name,
            status.text.replace("\n", "\\n").replace("\t", "\\t"),
            url
        )))
