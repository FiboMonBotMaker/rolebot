import os
import MySQLdb

__HOST = "db"
__PORT = 3306
__DB = os.getenv("MARIADB_DATABASE")
__USER = os.getenv("MARIADB_USER")
__PASSWORD = os.getenv("MARIADB_PASSWORD")


connection = MySQLdb.connect(
    host=__HOST,
    port=__PORT,
    user=__USER,
    passwd=__PASSWORD,
    db=__DB,
    charset="utf8")


def get():
    return connection.cursor()
