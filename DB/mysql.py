import MySQLdb
import logging

from . import generic


class MySQLDriver(generic.DB):
    def __init__(self):
        super(self)
        self.name = "MySQL DB Driver"
        self.db = MySQLdb.connect(host="", user="", passwd="", db="", charset="utf8")

    def getTweets():
        self.db.cursor()
        return cur.execute(
            """SELECT * \
                    FROM Tweets \
                    WHERE Deleted=0"""
        )

    def writeSuccess(path):
        cur = self.db.cursor()
        try:
            cur.execute(
                """UPDATE Tweets \
                      SET Screenshot=1 \
                      WHERE Tweet_Id=%s""",
                [path],
            )
            self.db.commit()
            logging.info(f"Screenshot OK. Tweet id {path}")
        except MySQLdb.Error as e:
            try:
                logging.error(("MySQL Error [%d]: %s" % (e.args[0], e.args[1])))
            except IndexError:
                logging.error(("MySQL Error: %s" % str(e)))

            logging.error(("Error", e.args[0], e.args[1]))
            logging.warning(("Warning:", path, "not saved to database"))
        return True

    def markDeleted(path):
        cur = self.db.cursor()
        try:
            cur.execute(
                """UPDATE Tweets \
                      SET Deleted=1 \
                      WHERE Tweet_Id=%s""",
                [path],
            )
            self.db.commit()
            logging.info(("Tweet marked as deleted ", path))
        except MySQLdb.Error as e:
            try:
                logging.error(("MySQL Error [%d]: %s" % (e.args[0], e.args[1])))
            except IndexError:
                logging.error(("MySQL Error: %s" % str(e)))

            logging.error(("Error", e.args[0], e.args[1]))
            logging.warning(("Warning:", path, "not saved to database"))
        return True

    def getLogs():
        cur = self.db.cursor()
        return cur.execute(
            "SELECT Url, Tweet_Id FROM Tweets WHERE Screenshot=0 AND Deleted=0 "
        )

    def saveTweet(url, status):
        (author, text, id_str) = (status.user.screen_name, status.text, status.id_str)
        cur = db.cursor()

        cur.execute(
            "CREATE TABLE IF NOT EXISTS Tweets(Id INT PRIMARY KEY AUTO_INCREMENT, \
                    Author VARCHAR(255), \
                    Text VARCHAR(255), \
                    Url VARCHAR(255), \
                    Tweet_Id VARCHAR(255), \
                    Screenshot INT, \
                    Deleted INT)"
        )

        try:
            cur.execute(
                """INSERT INTO Tweets(Author, Text, Url, Tweet_Id, Screenshot, Deleted)
                        VALUES (%s, %s, %s, %s, %s, %s)""",
                (author, text, url, id_str, 0, 0),
            )
            self.db.commit()
            logging.info(("Wrote to database:", author, id_str))
        except MySQLdb.Error as e:
            logging.error(("Error", e.args[0], e.args[1]))
            self.db.rollback()
            logging.error("ERROR writing database")
