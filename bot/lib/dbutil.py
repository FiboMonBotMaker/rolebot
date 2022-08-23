import os
import MySQLdb

__HOST = "db"
__PORT = 3306
__DB = os.getenv("MARIADB_DATABASE")
__USER = os.getenv("MARIADB_USER")
__PASSWORD = os.getenv("MARIADB_PASSWORD")


def get_connection():
    connection = MySQLdb.connect(
        host=__HOST,
        user=__USER,
        passwd=__PASSWORD,
        db=__DB,
        port=__PORT,
        charset="utf8")
    return connection


def create_talbe(table_name: str, columns: list[str]):
    connection = get_connection()
    columns = ",".join(columns)
    sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
    print(sql)
    try:
        connection.cursor().execute(sql)
        connection.commit()
        connection.close()
    except MySQLdb.Error as e:
        raise e


def select(table_name: str, columns: str, join: str = "", where: str = ""):
    connection = get_connection()
    columns = ",".join(columns)
    if len(where) != 0:
        where = f" WHERE {where}"
    if len(join) != 0:
        join = f" LEFT OUTER JOIN {join} "
    sql = f"SELECT {columns} FROM {table_name}{join}{where}"
    print(sql)
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        connection.close()
        return rows
    except MySQLdb.Error as e:
        raise e


def delete(table_name: str, where):
    connection = get_connection()
    sql = f"DELETE FROM {table_name} WHERE {where}"
    print(sql)
    try:
        connection.cursor().execute(sql)
        connection.commit()
        connection.close()
    except MySQLdb.Error as e:
        raise e


def insert(table_name: str, columins: list[str] = [], values: list[list[str]] = []):
    connection = get_connection()
    _values = ""
    if len(values) != 0:
        value_list = []
        for v in values:
            tmp = ",".join(v)
            value_list.append(f"({tmp})")
        _values = ",".join(value_list)
    else:
        raise ValueError("values is Empty list")
    _columins = ""
    if len(columins) != 0:
        tmp = ",".join(columins)
        _columins = f"({tmp})"

    sql = f"INSERT INTO {table_name}{_columins} VALUES{_values}"
    print(sql)
    try:
        connection.cursor().execute(sql)
        connection.commit()
        connection.close()
    except MySQLdb.Error as e:
        raise e


def foreign_key(from_table: str, from_column: str, dest_table, dest_column: str):
    return f"FOREIGN KEY {from_column}({from_table}) REFERENCES {dest_column}({dest_table})"


def primary_key(keys: list[str]):
    _keys = ",".join(keys)
    return f"PRIMARY KEY({_keys})"
