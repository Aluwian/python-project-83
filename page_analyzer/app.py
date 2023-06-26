from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    get_flashed_messages
)
from page_analyzer.dbase import UrlsTable, Url_Checks
from page_analyzer.validator import validate_url
from page_analyzer.analyzer import analyze_page
import os
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def get_main():
    return render_template('index.html')


@app.get('/urls')
def get_urls_page():
    table = UrlsTable()
    array = table.get_all_info()
    return render_template('urls/index.html',
                           urls=array
                           )


@app.post('/urls')
def create_new_url():
    data = request.form.to_dict()
    errors = validate_url(data)
    if errors:
        return render_template('index.html',
                               url=data,
                               messages=errors,
                               ), 422
    url_base = UrlsTable()
    values = url_base.has_name(data)
    id, result = values
    flash(result[1], result[0])
    return redirect(url_for('get_url', id=id))


@app.get('/urls/<int:id>')
def get_url(id):
    urt_table = UrlsTable()
    checks_base = Url_Checks()
    data = urt_table.get_url_info(id)
    messages = get_flashed_messages(with_categories=True)
    checks = checks_base.get_all_checks(id)
    return render_template('urls/new.html',
                           id=id,
                           name=data[1],
                           created_at=data[2],
                           messages=messages,
                           checks=checks)


@app.post("/urls/<int:id>/checks")
def get_check(id):
    urls = UrlsTable()
    link = urls.get_url_info(id)[1]
    try:
        checks_base = Url_Checks()
        check_result = analyze_page(link)
        result = checks_base.create_new(id, check_result)
        flash(result[1], result[0])
        return redirect(url_for('get_url',
                                id=id))
    except requests.ConnectionError:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('get_url',
                                id=id))
