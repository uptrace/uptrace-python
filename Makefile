.PHONY: all test

lint:
	pylint src/uptrace/

test: lint
	PYTHONPATH=src pytest

release: test
	rm -r dist
	python setup.py sdist bdist_wheel
	twine upload dist/*
