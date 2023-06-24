import os
from psycopg2 import connect, sql
from datetime import date
from page_analyzer.validator import normalize_url


def connect_to_db():
    DATABASE_URL = os.getenv("DATABASE_URL")
    return connect(DATABASE_URL)


class UrlsTable:
    def __init__(self):
        self.connect = connect_to_db()

    def fill_table(self, url_text):
        cur = self.connect.cursor()
        created_ad = date.today()
        cur.execute("INSERT INTO urls (name, created_at)"
                    "VALUES (%s, %s) RETURNING id;", (url_text, created_ad))
        result = cur.fetchone()
        self.connect.commit()
        return result[0]

    def has_name(self, dictionary):
        url_name = normalize_url(dictionary.get('url'))
        cur = self.connect.cursor()
        query = sql.SQL("SELECT {find} FROM {table} WHERE {key} = %s").format(
            find=sql.Identifier('id'),
            table=sql.Identifier('urls'),
            key=sql.Identifier('name')
        )
        cur.execute(query, (url_name,))
        result = cur.fetchone()
        if result is None:
            return self.fill_table(url_name),\
                ('success', 'Страница успешно добавлена')
        return result[0], ('info', 'Страница уже существует')

    def get_url_info(self, id):
        cur = self.connect.cursor()
        query = sql.SQL("SELECT * FROM {table} WHERE {key} = %s").format(
            table=sql.Identifier('urls'),
            key=sql.Identifier('id')
        )
        cur.execute(query, (id,))
        return cur.fetchone()

    def get_all_info(self):
        cur = self.connect.cursor()
        result = []
        checks = Url_Checks()
        cur.execute("SELECT id, name FROM urls ORDER BY id DESC;")
        array = cur.fetchall()
        for value in array:
            result.append(
                {
                    'id': value[0],
                    'name': value[1],
                    'last_check': checks.get_last(value[0]).get('created_at'),
                    'status_code': checks.get_last(value[0]).get('status_code')
                }
            )
        return result


class Url_Checks:
    def __init__(self):
        self.connect = connect_to_db()

    def create_new(self, url_id, page_info):
        cur = self.connect.cursor()
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
        self.connect.commit()
        return 'success', 'Страница успешно проверена'

    def get_all_checks(self, url_id):
        cur = self.connect.cursor()
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
        return result

    def get_last(self, value):
        cur = self.connect.cursor()
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
        cur.execute(query, (value,))
        result = cur.fetchone()
        if result is None:
            return ""
        return {"created_at": result[0],
                "status_code": result[1]
                }
