# Run me with 'nosetests screenshot.py --with-save-baseline --nocapture'

import logging

from needle.cases import NeedleTestCase
from needle.driver import NeedlePhantomJS

import config as c

opts = c.parse_args([c.DBS])
db = opts.db


class captureTweetScreenshots(NeedleTestCase):
    @classmethod
    def get_web_driver(cls):
        return NeedlePhantomJS()

    def test_masthead(self):
        self.list_to_screenshot()

    def writeSuccess(self, path):
        return db.writeSuccess(path)

    def markDeleted(self, path):
        return db.markDeleted(path)

    def list_to_screenshot(self):
        logFile = open("logfile.txt", "w")
        cur = db.getLogs()
        for (Url, Tweet_Id) in cur:
            try:
                self.driver.get(Url)
            except:
                logging(f"url does not exist: {Url}")
                logFile.write("Url doesnt exist \n")
                continue
            try:
                self.assertScreenshot(".tweet", Tweet_Id)

            except:
                logging(f"tweet deleted: {Url}")
                self.markDeleted(Tweet_Id)
                message = "Tweet deleted %s \n" % Url
                logFile.write(message)
                continue
            self.writeSuccess(Tweet_Id)
            message = "Tweet screenshotted %s \n" % Url
            logFile.write(message)
        logFile.close()


# if __name__ == '__main__':
#     list_to_screenshot(db)
