# Releasing a new version

## Prerequisites

Make sure you have the required tools installed:

```shell
source .venv/bin/activate
make deps
```

## Steps

### 1. Run tests

Ensure all tests pass before proceeding:

```shell
make test
```

### 2. Update the version

Bump the version in `src/uptrace/version.py`:

```python
__version__ = "X.Y.Z"
```

The version should match the OpenTelemetry SDK version (e.g. `1.40.0`).

### 3. Update dependencies

Update OpenTelemetry dependency versions in `pyproject.toml` to match the new version.

Update `requirements.txt` in each `example/` directory to use the new dependency versions.

### 4. Build and publish to PyPI

```shell
make release
```

This runs tests, builds the sdist and wheel, and uploads them to PyPI via `twine`.

### 5. Update go-uptrace

After publishing, update the uptrace version reference in the
[go-uptrace](https://github.com/uptrace/uptrace) repository.

### 6. Create a git tag

```shell
git add -A
git commit -m "chore: bump version to X.Y.Z"
git tag vX.Y.Z
git push origin master --tags
```
