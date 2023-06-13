import pytest
from page_analyzer.app import app
from werkzeug.test import Client


def test_main():
    client = Client(app)
    response = client.get('/')
    assert response.status_code == 200
