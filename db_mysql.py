import MySQLdb


db = MySQLdb.connect(host="",
                     user="",
                     passwd="",
                     db="",
                     charset="utf8")

def writeSuccess(path):
    cur = db.cursor()
    try:
        cur.execute("""UPDATE Tweets \
                  SET Screenshot=1 \
                  WHERE Tweet_Id=%s""", [path])
        db.commit()
        print "Screenshot OK. Tweet id ", path
    except MySQLdb.Error, e:
        try:
            print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
        except IndexError:
            print "MySQL Error: %s" % str(e)

        print "Error", e.args[0], e.args[1]
        print "Warning:", path, "not saved to database"
    return True

def markDeleted(path):
    cur = db.cursor()
    try:
        cur.execute("""UPDATE Tweets \
                  SET Deleted=1 \
                  WHERE Tweet_Id=%s""", [path])
        db.commit()
        print "Tweet marked as deleted ", path
    except MySQLdb.Error, e:
        try:
            print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
        except IndexError:
            print "MySQL Error: %s" % str(e)

        print "Error", e.args[0], e.args[1]
        print "Warning:", path, "not saved to database"
    return True

def getLogs():
    cur = db.cursor()
    return cur.execute("SELECT Url, Tweet_Id FROM Tweets WHERE Screenshot=0 AND Deleted=0 ")

def save_to_db(author, text, url, id_str):
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS Tweets(Id INT PRIMARY KEY AUTO_INCREMENT, \
                Author VARCHAR(255), \
                Text VARCHAR(255), \
                Url VARCHAR(255), \
                Tweet_Id VARCHAR(255), \
                Screenshot INT, \
                Deleted INT)")

    try:
        cur.execute("""INSERT INTO Tweets(Author, Text, Url, Tweet_Id, Screenshot, Deleted)
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (author, text, url, id_str, 0, 0))
        db.commit()
        print "Wrote to database:", author, id_str
    except MySQLdb.Error, e:
        print "Error", e.args[0], e.args[1]
        db.rollback()
        print "ERROR writing database"
