.PHONY: all test

deps:
	pip install nox

lint:
	nox -s lint

test:
	nox -s test-3.8

release: test
	rm -r build dist
	python setup.py sdist bdist_wheel
	twine upload --skip-existing --verbose dist/*
