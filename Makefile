.PHONY: all test

lint:
	pylint src/

test: lint
	PYTHONPATH=src pytest

release: test
	rm -r dist
	python setup.py sdist
	twine upload dist/*
