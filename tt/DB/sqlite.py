import sqlite3
import json
import logging
import sys
from datetime import datetime

from . import utils
from . import generic

VERSION = 1

def migrate_0_1(db):
    db.execute(
        """CREATE TABLE IF NOT EXISTS tweets (id INTEGER PRIMARY KEY, \
        screen_name VARCHAR(255), \
        text VARCHAR(1024), \
        date DATE, \
        link VARCHAR(255), \
        directed_to VARCHAR(255), \
        replies INTEGER, \
        retweets INTEGER, \
        favorites INTEGER, \
        geo VARCHAR(255), \
        mentions VARCHAR(1024), \
        hashtags VARCHAR(1024), \
        Screenshot BOOLEAN, \
        Deleted BOOLEAN)""")

    db.execute(
        """CREATE TABLE IF NOT EXISTS authors (screen_name VARCHAR(255) PRIMARY KEY, \
        id INTEGER UNIQUE, \
        date DATE)
        """)

    db.execute("PRAGMA user_version = 1")
    
MIGRATIONS = [
    migrate_0_1
]

class Driver(generic.DB):
    def __init__(self, filename="twitter.db"):
        generic.DB.__init__(self)
        self.filename = filename
        self.open()
        
    def open(self):
        self.db = sqlite3.connect(self.filename)

        self._migrate()

    def close(self):
        self.db.close()
        
    def _migrate(self):
        cur = self.db.cursor()
        user_version = cur.execute(
            """
            PRAGMA user_version
            """
        ).fetchone()
        version = user_version[0] if user_version else 0

        if version != VERSION:
            for i, m in enumerate(MIGRATIONS[version:VERSION]):
                logging.info(f"running migration {i} -> {i+1} ({m})")
                try:
                    m(self)
                except Exception as e:
                    logging.critical(f"error {e} in migration {m}")
                    sys.exit(-2)

    def getTweets(self):
        cur = self.db.cursor()
        return cur.execute(
            """SELECT * \
                    FROM tweets \
                    WHERE Deleted=0"""
        )

    def getAuthor(self, screen_name):
        cur = self.db.cursor()
        data = cur.execute(
            """SELECT * FROM authors WHERE screen_name=?""", (screen_name,)
        ).fetchone()
        if not data: raise KeyError(f"{screen_name} not found")

        return (data[0], data[1], datetime.strptime(data[2], '%Y-%m-%d %H:%M:%S'))

    def writeSuccess(self, id):
        q = """UPDATE tweets \
                      SET Screenshot=1 \
                      WHERE id=?"""
        if self.execute(q, (id,)):
            logging.info(f"Screenshot OK. Tweet id {id}")
            return True
        logging.warning(f"{id} not marked as success")
        return False

    def markDeleted(self, id):
        q =  """UPDATE tweets \
                      SET Deleted=1 \
                      WHERE id=?"""
        if self.execute(q, (id,)):
            logging.info(f"Tweet marked as deleted {id}")
            return True
        logging.warning(f"{id} not marked as deleted")
        return False

    def getLogs(self,):
        cur = self.db.cursor()
        return cur.execute(
            "SELECT link, id FROM tweets WHERE Screenshot=0 AND Deleted=0 "
        )

    def execute(self, q, args = []):
        cur = self.db.cursor()
        try:
            cur.execute(q, args)
            self.db.commit()
        except sqlite3.Error as e:
            logging.error(e, q, args)
            self.db.rollback()
            logging.error("ERROR writing database")
            return False
        return True

        
    def saveTweet(self, status):
        text = utils.extract_text(status)
        date = status.created_at
        if type(date) == str:
            date = utils.make_date(status.created_at)
            
        self.execute("""
        INSERT INTO tweets(id, screen_name, text, date, link, directed_to, replies, geo, mentions, hashtags, Screenshot, Deleted) \
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0)
        """, (status.id, status.user.screen_name, text, date, status.link,
              status.in_reply_to_screen_name, status.replies_count, status.geo,
              json.dumps(status.entities.user_mentions), json.dumps(status.entities.hashtags)))
        
    def saveAuthor(self, user):
        args = (user.screen_name, user.id, user.created_at)
        self.execute("""
        INSERT INTO authors(screen_name, id, date)
        VALUES(?, ?, ?) ON CONFLICT(screen_name) DO NOTHING
        """, args)
