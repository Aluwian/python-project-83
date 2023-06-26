import pytest

from page_analyzer.app import app
from werkzeug.test import Client


@pytest.fixture()
def test_create_app():
    testing_app = app
    testing_app.config.update({
        'TESTING': True,
    })
    yield app


@pytest.fixture()
def client(test_create_app):
    return app.test_client()


def test_main_page(client):
    response = client.get('/')
    assert response.status_code == 200
