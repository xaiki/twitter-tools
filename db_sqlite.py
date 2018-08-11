import sqlite3

db = sqlite3.connect('twitter.db')

def writeSuccess(path):
    cur = db.cursor()
    try:
        cur.execute("""UPDATE Tweets \
                  SET Screenshot=1 \
                  WHERE Tweet_Id='%s'""" % [path])
        db.commit()
        print "Screenshot OK. Tweet id ", path
    except sqlite3.Error, e:
        print "Error", e
        print "Warning:", path, "not saved to database"
    return True

def markDeleted(path):
    cur = db.cursor()
    try:
        cur.execute("""UPDATE Tweets \
                  SET Deleted=1 \
                  WHERE Tweet_Id='%s'""" % [path])
        db.commit()
        print "Tweet marked as deleted ", path
    except sqlite3.Error, e:
        print "Error", e
        print "Warning:", path, "not saved to database"
    return True

def getLogs():
    cur = db.cursor()
    return cur.execute("SELECT Url, Tweet_Id FROM Tweets WHERE Screenshot=0 AND Deleted=0 ")

def save_to_db(author, text, url, id_str):
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS Tweets (Id INTEGER PRIMARY KEY, \
                Author VARCHAR(255), \
                Text VARCHAR(255), \
                Url VARCHAR(255), \
                Tweet_Id VARCHAR(255), \
                Screenshot INTEGER, \
                Deleted INTEGER)")

    try:
        cur.execute("""INSERT INTO Tweets(Author, Text, Url, Tweet_Id, Screenshot, Deleted)
                    VALUES ('%s', '%s', '%s', '%s', '%s', '%s')""" % (author, text, url, id_str, 0, 0))
        db.commit()
        #print "Wrote to database:", author, id_str
    except sqlite3.Error, e:
        print "Error", e
        db.rollback()
        print "ERROR writing database"

if __name__ == '__main__':
    save_to_db('xaiki', 'blah blah', 'url', 'id')
