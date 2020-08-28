import sqlite3
from DB import generic

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


    def getTweets(self):
        cur = self.db.cursor()
        return cur.execute(
            """SELECT * \
                    FROM Tweets \
                    WHERE Deleted=0"""
        )

    def _commit(self, query):
        cur = self.db.cursor()
        try:
            cur.execute(query)
            self.db.commit()
        except sqlite3.Error as e:
            print("Error", e)
            return False
        return True

    def writeSuccess(self, path):
        if self._commit(
            """UPDATE Tweets \
                      SET Screenshot=1 \
                      WHERE Tweet_Id='%s'"""
        ):
            print("Screenshot OK. Tweet id ", path)
            return True
        print("Warning:", path, "not saved to database")
        return False

    def markDeleted(self, path):
        if self._commit(
            """UPDATE Tweets \
                      SET Deleted=1 \
                      WHERE Tweet_Id='%s'"""
            % [path]
        ):
            print("Tweet marked as deleted ", path)
            return True
        print("Warning:", path, "not saved to database")
        return False

    def getLogs(self,):
        cur = self.db.cursor()
        return cur.execute(
            "SELECT Url, Tweet_Id FROM Tweets WHERE Screenshot=0 AND Deleted=0 "
        )

    def save(self, url, status):
        (author, text, id_str) = (status.user.screen_name, status.text, status.id_str)
        cur = self.db.cursor()

        try:
            cur.execute(
                """
            INSERT INTO Tweets(Author, Text, Url, Tweet_Id, Screenshot, Deleted)
            VALUES ('%s', '%s', '%s', '%s', '%s', '%s')
            """
                % (author, text, url, id_str, 0, 0)
            )
            self.db.commit()
            # print "Wrote to database:", author, id_str
        except sqlite3.Error as e:
            print("Error", e, c)
            self.db.rollback()
            print("ERROR writing database")
