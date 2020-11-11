.PHONY: all test

isort:
	isort .

lint: isort
	pylint src/uptrace/

test: lint
	PYTHONPATH=src pytest

release: test
	rm -r build dist
	python setup.py sdist bdist_wheel
	twine upload --skip-existing --verbose dist/*
