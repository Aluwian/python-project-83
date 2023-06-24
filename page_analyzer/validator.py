from urllib.parse import urlparse
from validators import url
import requests
from bs4 import BeautifulSoup


def validate_url(value):
    errors = []
    if not value.get('url'):
        errors.append(('danger', 'URL обязателен'))
    if not url(value.get('url')):
        errors.append(('danger', 'Некорректный URL'))
    return errors


def normalize_url(value):
    result = (urlparse(value)[0], urlparse(value)[1])
    return '://'.join(result)


def check_page(link):
    r = requests.get(link)
    page = BeautifulSoup(r.text, 'html.parser')
    status_code = r.status_code
    if 200 > status_code > 299:
        raise RuntimeError
    title = page.title.string
    h_1 = find_h1(page)
    description = find_description(page)
    return {
        "status_code": status_code,
        "title": title,
        "h1": h_1,
        "description": description
    }


def find_h1(page):
    text = page.h1.string
    if not text:
        return None
    return text


def find_description(page):
    meta = page.css.select('meta[name="description"]')
    attributes = meta[0].attrs
    content = attributes.get('content')
    if not meta or not content:
        return None
    return content
