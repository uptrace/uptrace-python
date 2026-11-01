.PHONY: all test examples

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

# Smoke-test all examples, each in its own virtualenv under .venv-examples/.
examples:
	python3 scripts/sync_examples.py --check
	for ex in $$(python3 scripts/run_example.py --list); do \
		python3 -m venv .venv-examples/$$ex \
		&& .venv-examples/$$ex/bin/python scripts/run_example.py --install $$ex \
		&& .venv-examples/$$ex/bin/python scripts/run_example.py $$ex || exit 1; \
	done
