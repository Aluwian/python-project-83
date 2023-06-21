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
        cur.execute("SELECT id, name FROM urls ORDER BY created_at DESC;")
        array = cur.fetchall()
        for value in array:
            result.append(
                {
                    'id': value[0],
                    'name': value[1],
                    'last_check': checks.get_last_check(value[0])
                }
            )
        return result


class Url_Checks:
    def __init__(self):
        self.connect = connect_to_db()

    def create_new(self, url_id):
        cur = self.connect.cursor()
        created_ad = date.today()
        cur.execute("INSERT INTO url_checks (url_id, created_at)"
                    "VALUES (%s, %s);", (url_id, created_ad))
        self.connect.commit()
        return 'success', 'Страница успешно проверена'

    def get_all_checks(self, url_id):
        cur = self.connect.cursor()
        result = []
        query = sql.SQL(
            "SELECT {value_1}, {value_2} FROM {table} WHERE {value_3} = %s"
            "ORDER BY {value_1} DESC;"
        ).format(
            value_1=sql.Identifier('id'),
            value_2=sql.Identifier('created_at'),
            value_3=sql.Identifier('url_id'),
            table=sql.Identifier('url_checks')
        )
        cur.execute(query, (url_id,))
        array = cur.fetchall()
        for value in array:
            result.append({'id': value[0], 'created_at': value[1]})
        return result

    def get_last_check(self, value):
        cur = self.connect.cursor()
        query = sql.SQL(
            "SELECT {value_1} FROM {table} WHERE {value_2} = %s "
            "ORDER BY {value_3} DESC LIMIT 1;").format(
            value_1=sql.Identifier('created_at'),
            value_2=sql.Identifier('url_id'),
            value_3=sql.Identifier('id'),
            table=sql.Identifier('url_checks')
        )
        cur.execute(query, (value,))
        result = cur.fetchone()
        if result is None:
            return ""
        return result[0]
