# Releasing a new version

## Prerequisites

Make sure you have the required tools installed:

```shell
source .venv/bin/activate
make install
```

## Steps

### 1. Update the version

Bump the version in `src/uptrace/version.py`:

```python
__version__ = "X.Y.Z"
```

The version should match the OpenTelemetry SDK version (e.g. `1.45.0`).

### 2. Update dependencies

Check the latest versions on PyPI:

```shell
curl -s https://pypi.org/pypi/opentelemetry-sdk/json | python3 -c "import json,sys; print(json.load(sys.stdin)['info']['version'])"
curl -s https://pypi.org/pypi/opentelemetry-instrumentation/json | python3 -c "import json,sys; print(json.load(sys.stdin)['info']['version'])"
```

Update the OpenTelemetry dependencies in `pyproject.toml`:

- `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-exporter-otlp`: `~= X.Y.0`
- `opentelemetry-instrumentation`, `opentelemetry-instrumentation-logging`: the matching
  contrib version `~= 0.Nb0` (e.g. 1.45.0 ↔ 0.66b0)

Dependabot may rewrite individual pins (e.g. `opentelemetry-api >= 1.41,< 1.45`); reset them
to `~=` so all packages move together.

Also check `requires-python` against the upstream packages (e.g. OpenTelemetry 1.45 requires
Python >= 3.10) and update the classifiers accordingly.

Update `requirements.txt` in each `example/` directory to use the new versions (`uptrace`,
`opentelemetry-sdk`, `opentelemetry-exporter-otlp`, and `opentelemetry-instrumentation-*`).

Then reinstall dependencies and check that nothing is left on the old versions:

```shell
make install
grep -rn "<old-sdk-version>\|<old-contrib-version>" --exclude-dir=.venv --exclude-dir=.git .
```

### 3. Run tests and commit

```shell
make test
git add -A
git commit -m "chore: bump version to X.Y.Z"
git push origin master
```

### 4. Build and publish to PyPI

```shell
make publish
```

This runs tests, builds the sdist and wheel, and uploads them to PyPI via `twine`.

If the upload fails with `'2.5' is not a valid metadata version`, your twine is too old; run
`make install` to upgrade it.

### 5. Create a git tag

Tag the commit that was published:

```shell
git tag vX.Y.Z
git push origin vX.Y.Z
```

### 6. Update go-uptrace

After publishing, update the uptrace version reference in the
[go-uptrace](https://github.com/uptrace/uptrace) repository.
