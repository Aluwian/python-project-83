import os
from psycopg2 import connect, sql
from datetime import date
from page_analyzer.validator import normalize_url
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
    conn.close()
    return result[0]


def add_check(url_id, page_info):
    with connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            created_at = date.today()
            cur.execute("INSERT INTO url_checks ("
                        "url_id, status_code, h1, title, description, created_at"
                        ")"
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
    conn.close()
    return 'success', 'Страница успешно проверена'


def has_url_name(url):
    with connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            url_name = normalize_url(url)
            query = sql.SQL("SELECT {find} FROM {table} WHERE {key} = %s").format(
                find=sql.Identifier('id'),
                table=sql.Identifier('urls'),
                key=sql.Identifier('name')
            )
            cur.execute(query, (url_name,))
            result = cur.fetchone()
    conn.close()
    if result is None:
        return add_url(url_name), \
            ('success', 'Страница успешно добавлена')
    return result[0], ('info', 'Страница уже существует')


def get_one_url(url_id):
    with connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            query = sql.SQL("SELECT * FROM {table} WHERE {key} = %s").format(
                table=sql.Identifier('urls'),
                key=sql.Identifier('id')
            )
            cur.execute(query, (url_id,))
            result = cur.fetchone()
    conn.close()
    return result


def get_all_urls():
    with connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            result = []
            cur.execute("SELECT id, name FROM urls ORDER BY id DESC;")
            array = cur.fetchall()
            for value in array:
                result.append(
                    {
                        'id': value[0],
                        'name': value[1],
                        'last_check': get_last_check(value[0]).get('created_at'),
                        'status_code': get_last_check(value[0]).get('status_code')
                    }
                )
    conn.close()
    return result


def get_all_checks(url_id):
    with connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            result = []
            query = sql.SQL(
                "SELECT {id}, {status}, {h1}, {title}, {desc}, {date} FROM {table}"
                "WHERE {value_3} = %s"
                "ORDER BY {id} DESC;"
            ).format(
                id=sql.Identifier('id'),
                status=sql.Identifier('status_code'),
                h1=sql.Identifier('h1'),
                title=sql.Identifier('title'),
                desc=sql.Identifier('description'),
                date=sql.Identifier('created_at'),
                value_3=sql.Identifier('url_id'),
                table=sql.Identifier('url_checks')
            )
            cur.execute(query, (url_id,))
            array = cur.fetchall()
            for value in array:
                result.append({
                    'id': value[0],
                    'status_code': value[1],
                    'h1': value[2],
                    'title': value[3],
                    'description': value[4],
                    'created_at': value[5]
                })
    conn.close()
    return result


def get_last_check(value_id):
    with connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
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
    conn.close()
    if result is None:
        return {"created_at": "",
                "status_code": ""
                }
    return {"created_at": result[0],
            "status_code": result[1]
            }
