.PHONY: all test

install:
	pip install -r dev-requirements.txt
	pip install .

lint:
	nox -s lint

test:
	nox -s test-3.12

publish: test
	rm -rf build dist
	python -m build
	twine upload --skip-existing --verbose dist/*
