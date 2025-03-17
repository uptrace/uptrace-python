.PHONY: all test

deps:
	pip install -r dev-requirements.txt
	pip install .

lint:
	nox -s lint

test:
	nox -s test-3.10

release: test
	rm -rf build dist
	python setup.py sdist bdist_wheel
	twine upload --skip-existing --verbose dist/*
