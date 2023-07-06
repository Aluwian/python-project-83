import os
from psycopg2 import connect, sql, extras
from datetime import date
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def add_url(url_text):
    with connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            created_ad = date.today()
            cur.execute("INSERT INTO urls (name, created_at)"
                        "VALUES (%s, %s) RETURNING id;", (url_text, created_ad))
            result = cur.fetchone()
    conn.commit()
    return result[0]


def add_check(url_id, page_info):
    with connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            created_at = date.today()
            cur.execute("INSERT INTO url_checks ("
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
    conn.commit()


def get_id_by_url(url):
    with connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            query = sql.SQL("SELECT {find} FROM {table}"
                            "WHERE {key} = %s").format(
                find=sql.Identifier('id'),
                table=sql.Identifier('urls'),
                key=sql.Identifier('name')
            )
            cur.execute(query, (url,))
            result = cur.fetchone()
    if result is None:
        return None
    return result[0]


def get_url_by_id(url_id):
    with connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            query = sql.SQL("SELECT * FROM {table} WHERE {key} = %s").format(
                table=sql.Identifier('urls'),
                key=sql.Identifier('id')
            )
            cur.execute(query, (url_id,))
            result = cur.fetchone()
    return result


def get_all_urls():
    with connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            result = []
            cur.execute("SELECT id, name FROM urls ORDER BY id DESC;")
            array = cur.fetchall()
            for value in array:
                item = {'id': value[0],
                        'name': value[1],
                        'last_check': "",
                        'status_code': ""
                        }
                try:
                    last_check = get_last(item.get('id'))
                    item['last_check'] = last_check.get('created_at')
                    item['status_code'] = last_check.get('status_code')
                except Exception:
                    pass
                result.append(item)
    return result


def get_all_checks(url_id):
    with connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=extras.DictCursor) as cur:
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
            cur.execute(query, (url_id,))
            array = cur.fetchall()
            for value in array:
                result.append(value)
    return result


def get_last(value_id):
    with connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=extras.DictCursor) as cur:
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
            cur.execute(query, (value_id,))
            result = cur.fetchone()
    if result is None:
        raise Exception
    return result
