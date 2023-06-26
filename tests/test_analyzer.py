import pytest
from bs4 import BeautifulSoup
from page_analyzer.analyzer import (
    get_h1,
    get_title,
    get_description,
    get_analyze_info
)

code_1 = """<meta name="description" content="Third project for Hexlet.io">"
<title>Анализатор страниц</title>
<h1>Сайт: https://python-page-analyzer-ru.hexlet.app</h1>"""
code_2 = """<meta name="description" content="">
<title></title>
<h1></h1>"""
code_3 = """<html>
<body>
<p class="story">Once upon a time there were three little sisters;
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>
<p class="story">...</p>"""


page_1 = BeautifulSoup(code_1, 'html.parser')
page_2 = BeautifulSoup(code_2, 'html.parser')
page_3 = BeautifulSoup(code_3, 'html.parser')


@pytest.mark.parametrize(
    "page, result",
    [
        (page_1, "Сайт: https://python-page-analyzer-ru.hexlet.app"),
        (page_2, ""),
        (page_3, ""),
    ],
)
def test_get_h1(page, result):
    assert get_h1(page) == result


@pytest.mark.parametrize(
    "page, result",
    [
        (page_1, "Анализатор страниц"),
        (page_2, ""),
        (page_3, ""),
    ],
)
def test_get_title(page, result):
    assert get_title(page) == result


@pytest.mark.parametrize(
    "page, result",
    [
        (page_1, "Third project for Hexlet.io"),
        (page_2, ""),
        (page_3, ""),
    ],
)
def test_get_description(page, result):
    assert get_description(page) == result


@pytest.mark.parametrize(
    "page, code, result",
    [
        (
            page_1,
            200,
            {
                "status_code": 200,
                "title": "Анализатор страниц",
                "h1": "Сайт: https://python-page-analyzer-ru.hexlet.app",
                "description": "Third project for Hexlet.io"
            }
        ),
        (
            page_2,
            200,
            {
                "status_code": 200,
                "title": "",
                "h1": "",
                "description": ""
            }
        ),
        (
            page_3,
            200,
            {
                "status_code": 200,
                "title": "",
                "h1": "",
                "description": ""
            }
        ),
    ],
)
def test_get_analyze_info(page, code, result):
    assert get_analyze_info(page, code) == result
