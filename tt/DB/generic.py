import logging
import os

class DB:
    def __init__(self):
        self.name = "Generic DB Driver"
        
    def _WIPE(self):
        self.close()
        os.remove(self.filename)
        self.open()
