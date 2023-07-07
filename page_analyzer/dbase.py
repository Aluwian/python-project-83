import os
from psycopg2 import connect, sql, extras
from datetime import date
from dotenv import load_dotenv
from contextlib import suppress

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def create_db_connection(func):
    def wrapper(*arg):
        with connect(DATABASE_URL) as db_connection:
            with db_connection.cursor(cursor_factory=extras.DictCursor) \
                    as db_cursor:
                return func(*arg, db_cursor, db_connection)
    return wrapper


@create_db_connection
def add_url(url_text, db_cursor, db_connection):
    created_ad = date.today()
    db_cursor.execute("INSERT INTO urls (name, created_at)"
                      "VALUES (%s, %s) RETURNING id;", (url_text, created_ad))
    result = db_cursor.fetchone()
    db_connection.commit()
    return result[0]


@create_db_connection
def add_check(url_id, page_info, db_cursor, db_connection):
    created_at = date.today()
    db_cursor.execute("INSERT INTO url_checks ("
                      "url_id, status_code, h1, title,"
                      "description, created_at)"
                      "VALUES (%s, %s, %s, %s, %s, %s);",
                      (
                          url_id,
                          page_info.get('status_code'),
                          page_info.get('h1'),
                          page_info.get('title'),
                          page_info.get('description'),
                          created_at
                      )
                      )
    db_connection.commit()


@create_db_connection
def get_id_by_url(url, db_cursor, db_connection):
    query = sql.SQL("SELECT {find} FROM {table}"
                    "WHERE {key} = %s").format(
        find=sql.Identifier('id'),
        table=sql.Identifier('urls'),
        key=sql.Identifier('name')
    )
    db_cursor.execute(query, (url,))
    result = db_cursor.fetchone()
    if result is None:
        return None
    return result[0]


@create_db_connection
def get_url_by_id(url_id, db_cursor, db_connection):
    query = sql.SQL("SELECT * FROM {table} WHERE {key} = %s").format(
        table=sql.Identifier('urls'),
        key=sql.Identifier('id')
    )
    db_cursor.execute(query, (url_id,))
    result = db_cursor.fetchone()
    return result


@create_db_connection
def get_all_urls(db_cursor, db_connection):
    result = []
    db_cursor.execute("SELECT id, name FROM urls ORDER BY id DESC;")
    array = db_cursor.fetchall()
    for value in array:
        with suppress(FileNotFoundError):
            item = {'id': value[0],
                    'name': value[1],
                    'last_check': "",
                    'status_code': ""
                    }
            last_check = get_last(db_cursor, item.get('id'))
            item['last_check'] = last_check.get('created_at')
            item['status_code'] = last_check.get('status_code')
        result.append(item)
    return result


@create_db_connection
def get_all_checks(url_id, db_cursor, db_connection):
    result = []
    query = sql.SQL(
        "SELECT {id}, {stat}, {h1}, {t}, {desc}, {date} FROM {check}"
        "WHERE {value_3} = %s"
        "ORDER BY {id} DESC;"
    ).format(
        id=sql.Identifier('id'),
        stat=sql.Identifier('status_code'),
        h1=sql.Identifier('h1'),
        t=sql.Identifier('title'),
        desc=sql.Identifier('description'),
        date=sql.Identifier('created_at'),
        value_3=sql.Identifier('url_id'),
        check=sql.Identifier('url_checks')
    )
    db_cursor.execute(query, (url_id,))
    array = db_cursor.fetchall()
    for value in array:
        result.append(value)
    return result


def get_last(db_cursor, value_id):
    query = sql.SQL(
        "SELECT {create_at}, {status_code} FROM {table}"
        "WHERE {value_2} = %s "
        "ORDER BY {value_3} DESC LIMIT 1;").format(
        create_at=sql.Identifier('created_at'),
        status_code=sql.Identifier('status_code'),
        value_2=sql.Identifier('url_id'),
        value_3=sql.Identifier('id'),
        table=sql.Identifier('url_checks')
    )
    db_cursor.execute(query, (value_id,))
    result = db_cursor.fetchone()
    if result is None:
        raise FileNotFoundError
    return result
