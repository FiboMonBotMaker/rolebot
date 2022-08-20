from lib.dbutil import get
import os

d = get()

c.excute(f"""SHOW CREATE DATABASE {os.getenv("MARIADB_DATABASE")}""")
