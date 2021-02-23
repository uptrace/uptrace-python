export PYTHONPATH=../../src
export OTEL_PYTHON_DJANGO_INSTRUMENT=True

all: build up

build:
	docker-compose build
up:
	docker-compose up --detach django
down:
	docker-compose down
logs:
	docker-compose logs django

deps:
	pip install -r requirements.txt

migrate:
	python manage.py migrate

run: migrate
	python manage.py runserver 0.0.0.0:8000
