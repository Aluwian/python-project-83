import requests
from bs4 import BeautifulSoup


def get_h1(page):
    text = page.find_all('h1', limit=1)
    if not text or page.h1.string is None:
        return ""
    return page.h1.string


def get_description(page):
    meta = page.css.select('meta[name="description"]')
    if not meta:
        return ""
    attributes = meta[0].attrs
    content = attributes.get('content')
    if not content:
        return ""
    return content


def get_title(page):
    title = page.find_all('title')
    if not title or page.title.string is None:
        return ""
    return page.title.string


def get_analyze_info(page, code):
    return {
        "status_code": code,
        "title": get_title(page),
        "h1": get_h1(page),
        "description": get_description(page)
    }


def analyze_page(link):
    r = requests.get(link)
    r.raise_for_status()
    status_code = r.status_code
    html_code = BeautifulSoup(r.text, 'html.parser')
    return get_analyze_info(html_code, status_code)
