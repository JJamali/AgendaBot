import MySQLdb
import os


def init_database(user, password):
    db = MySQLdb.connect(user=user, password=password, host='localhost')
    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS deadlinedb")

    db.select_db('deadlinedb')
    cursor = db.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS deadlines ("
                   "    guild_id BIGINT,"
                   "    department VARCHAR(20),"
                   "    course_num VARCHAR(20),"
                   "    name VARCHAR(20),"
                   "    due_date DATETIME"
                   ")")
    
    cursor.execute("CREATE TABLE IF NOT EXISTS events ("
                   "    name VARCHAR(30),"
                   "    Description VARCHAR(60),"
                   "    start_date DATETIME"
                   ")")
    db.close()


if __name__ == '__main__':
    USER = os.getenv('db_user')
    PASSWORD = os.getenv('db_password')
    init_database(USER, PASSWORD)
