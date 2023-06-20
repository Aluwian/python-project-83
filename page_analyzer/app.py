from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    get_flashed_messages
)
from page_analyzer.controller import UrlsTable
from page_analyzer.validator import validate_url
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def get_main():
    return render_template('index.html')


@app.get('/urls')
def get_page():
    repo = UrlsTable()
    array = repo.get_all_urls()
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
    repo = UrlsTable()
    values = repo.has_name(data)
    id, result = values
    flash(result[1], result[0])
    return redirect(url_for('get_url', id=id))


@app.get('/urls/<int:id>')
def get_url(id):
    repo = UrlsTable()
    data = repo.get_url_info(id)
    messages = get_flashed_messages(with_categories=True)
    return render_template('urls/new.html',
                           id=id,
                           name=data[1],
                           created_at=data[2],
                           messages=messages)
