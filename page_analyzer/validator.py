from urllib.parse import urlparse
from validators import url


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
