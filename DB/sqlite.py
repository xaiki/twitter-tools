import sqlite3
import logging

from . import generic

class Driver(generic.DB):
    def __init__(self, filename="twitter.db"):
        generic.DB.__init__(self)
        self.db = sqlite3.connect(filename)

        cur = self.db.cursor()

        cur.execute(
            "CREATE TABLE IF NOT EXISTS Tweets (Id INTEGER PRIMARY KEY, \
                    Author VARCHAR(255), \
                    Text VARCHAR(255), \
                    Url VARCHAR(255), \
                    Tweet_Id VARCHAR(255), \
                    Screenshot INTEGER, \
                    Deleted INTEGER)"
        )

        cur.execute(
            "CREATE TABLE IF NOT EXISTS Authors (Author VARCHAR(255) PRIMARY KEY, \
                    Id INTEGER NOT NULL UNIQUE)"
        )


    def getTweets(self):
        cur = self.db.cursor()
        return cur.execute(
            """SELECT * \
                    FROM Tweets \
                    WHERE Deleted=0"""
        )

    def getAuthor(self, author):
        cur = self.db.cursor()
        return cur.execute(
            """SELECT Id FROM Authors WHERE Author=?""", (author,)
        ).fetchone()[0]

    def _commit(self, query):
        cur = self.db.cursor()
        try:
            cur.execute(query)
            self.db.commit()
        except sqlite3.Error as e:
            logging.error(e)
            return False
        return True

    def writeSuccess(self, path):
        q = """UPDATE Tweets \
                      SET Screenshot=1 \
                      WHERE Tweet_Id='?'"""
        if self._commit(q, path):
            logging.info(f"Screenshot OK. Tweet id {path}")
            return True
        logging.warning(f"{path} not saved to database")
        return False

    def markDeleted(self, path):
        q =  """UPDATE Tweets \
                      SET Deleted=1 \
                      WHERE Tweet_Id='?'"""
        if self._commit(q, path):
            logging.info(f"Tweet marked as deleted {path}")
            return True
        logging.warning(f"{path} not saved to database")
        return False

    def getLogs(self,):
        cur = self.db.cursor()
        return cur.execute(
            "SELECT Url, Tweet_Id FROM Tweets WHERE Screenshot=0 AND Deleted=0 "
        )

    def execute(self, q, args):
        cur = self.db.cursor()
        try:
            cur.execute(q, args)
            self.db.commit()
        except sqlite3.Error as e:
            logging.error(e, q, args)
            self.db.rollback()
            logging.error("ERROR writing database")

        
    def saveTweet(self, url, status):
        (author, text, id_str) = (status.user.screen_name, status.text, status.id_str)
        self.execute("""
INSERT INTO Tweets(Author, Text, Url, Tweet_Id, Screenshot, Deleted) \
        VALUES (?, ?, ?, ?, ?, ?)
        """, (author, text, url, id_str, 0, 0))
        
    def saveAuthor(self, status):
        args = (status.user.screen_name, status.user.id)
        self.execute("""
            INSERT INTO Authors(Author, Id)
            VALUES(?, ?) ON CONFLICT(Author) DO NOTHING
            """, args)
