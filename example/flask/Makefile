all: build up

build:
	docker-compose build
up:
	docker-compose up --detach flask
down:
	docker-compose down
logs:
	docker-compose logs flask

deps:
	pip install -r requirements.txt

run:
	PYTHONPATH=../../src python app.py
