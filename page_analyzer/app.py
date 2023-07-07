from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    get_flashed_messages
)
from page_analyzer import dbase
from page_analyzer.validator import validate_url, normalize_url
from page_analyzer.analyzer import analyze_page
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def get_main():
    return render_template('pages/index.html')


@app.errorhandler(404)
def get_404(error):
    return render_template('pages/404.html'), 404


@app.get('/urls')
def get_urls_page():
    array = dbase.get_all_urls()
    return render_template('pages/urls/index.html',
                           urls=array
                           )


@app.post('/urls')
def create_new_url():
    data = request.form.to_dict()
    errors = validate_url(data)
    if errors:
        return render_template('pages/index.html',
                               url=data,
                               messages=errors,
                               ), 422
    url = normalize_url(data.get('url'))
    url_id = dbase.get_id_by_url(url)
    if url_id is not None:
        flash('Страница уже существует', 'info')
        return redirect(url_for('get_url', id=url_id))
    new_id = dbase.add_url(url)
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('get_url', id=new_id))


@app.get('/urls/<int:id>')
def get_url(id):
    data = dbase.get_url_by_id(id)
    messages = get_flashed_messages(with_categories=True)
    checks = dbase.get_all_checks(id)
    return render_template('pages/urls/new.html',
                           id=id,
                           name=data[1],
                           created_at=data[2],
                           messages=messages,
                           checks=checks)


@app.post("/urls/<int:id>/checks")
def get_check(id):
    link = dbase.get_url_by_id(id)[1]
    try:
        check_result = analyze_page(link)
        dbase.add_check(id, check_result)
        flash('Страница успешно проверена', 'success')
        return redirect(url_for('get_url',
                                id=id))
    except Exception:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('get_url',
                                id=id))
