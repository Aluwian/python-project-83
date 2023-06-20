install:
	poetry install

package-install:
	python3 -m pip install --user dist/*.whl

build:
	poetry build

publish:
	poetry publish --dry-run

lint:
	poetry run flake8

test:
	poetry run pytest

test-coverage:
	poetry run pytest --cov=page_analyzer --cov-report xml tests

dev:
	poetry run flask --app page_analyzer:app run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

all:
	db-create database-load

database-load:
	psql python-project-83 < database.sql
