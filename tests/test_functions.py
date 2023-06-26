from page_analyzer.validator import normalize_url


url_1 = 'https://guides.hexlet.io/ru/deploy/'
url_2 = 'https://www.geeksforgeeks.org/python-os-getenv-method/'


def test_normalize_url():
    assert normalize_url(url_1) == 'https://guides.hexlet.io'
    assert normalize_url(url_2) == 'https://www.geeksforgeeks.org'
