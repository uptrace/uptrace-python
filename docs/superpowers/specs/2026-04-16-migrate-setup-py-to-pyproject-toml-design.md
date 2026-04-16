# Migrate from setup.py to pyproject.toml (Hatchling)

## Goal

Replace `setup.py` + `setup.cfg` with a single `pyproject.toml` using **hatchling** as the build backend. This eliminates the deprecated `python setup.py` invocations and aligns with the opentelemetry-python upstream ecosystem.

## Scope

- Replace packaging configuration (`setup.py`, `setup.cfg` -> `pyproject.toml`)
- Update build/release commands (`python setup.py sdist bdist_wheel` -> `python -m build`)
- Update Makefile, noxfile.py, CI, and RELEASING.md to use the new tooling
- Preserve all existing behavior: version sourcing, entry points, namespace packages, src-layout

## Out of Scope

- Changing the version management strategy (keep `src/uptrace/version.py`)
- Migrating to uv workspace or any monorepo tool
- Changing the release/publish workflow beyond the build command
- Updating example projects

## Design

### 1. New pyproject.toml

The single source of packaging configuration. Mirrors the opentelemetry-python pattern.

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "uptrace"
description = "OpenTelemetry Python distribution for Uptrace"
readme = "README.md"
license = "BSD-3-Clause"
requires-python = ">=3.9"
authors = [
    { name = "Uptrace.dev", email = "support@uptrace.dev" },
]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Typing :: Typed",
]
dependencies = [
    "opentelemetry-api ~= 1.40.0",
    "opentelemetry-sdk ~= 1.40.0",
    "opentelemetry-exporter-otlp ~= 1.40.0",
    "opentelemetry-instrumentation ~= 0.61b0",
]
dynamic = ["version"]

[project.urls]
Homepage = "https://uptrace.dev"
Repository = "https://github.com/uptrace/uptrace-python"

[project.entry-points.opentelemetry_distro]
uptrace_distro = "uptrace.distro:UptraceDistro"

[tool.hatch.version]
path = "src/uptrace/version.py"

[tool.hatch.build.targets.sdist]
include = ["/src", "/tests"]

[tool.hatch.build.targets.wheel]
packages = ["src/uptrace"]
```

Key decisions:
- **`dynamic = ["version"]`** with `[tool.hatch.version]` reading `src/uptrace/version.py` preserves the existing single-source version pattern. Hatchling natively parses `__version__ = "X.Y.Z"` from the file.
- **`packages = ["src/uptrace"]`** tells hatchling where the package lives (src-layout).
- **Entry points** use the PEP 621 `[project.entry-points.*]` table format.
- **`requires-python = ">=3.9"`** updates from 3.8 (which is EOL) to match setup.cfg's classifiers which already list 3.9.
- **License** uses the PEP 639 SPDX identifier format (`"BSD-3-Clause"`).

### 2. Files to Delete

- `setup.py` - replaced entirely by pyproject.toml + hatchling
- `setup.cfg` - all metadata moved to pyproject.toml

### 3. dev-requirements.txt Changes

Replace `setuptools` with `build` (the PyPA standard build frontend):

```
wheel
mypy
black==26.3.1
pytest==9.0.2
pylint==4.0.5
nox
isort
twine
build
hatchling
```

### 4. Makefile Changes

Update the `release` target:

```makefile
release: test
	rm -rf build dist
	python -m build
	twine upload --skip-existing --verbose dist/*
```

The `deps` target stays the same (`pip install -r dev-requirements.txt && pip install .`) since `pip install .` works with any PEP 517 backend.

### 5. RELEASING.md Changes

Update the build instruction from `python setup.py sdist bdist_wheel` to `python -m build`. Update step references from `setup.cfg` to `pyproject.toml` for dependency version updates.

### 6. noxfile.py

No changes needed. `session.install(".")` uses pip, which already supports PEP 517 builds.

### 7. CI (.github/workflows/build.yml)

No changes needed. CI runs `make deps` which uses `pip install .`, already PEP 517 compatible.

### 8. Tool Configuration

Existing tool configs (`.isort.cfg`, `.pylintrc`) remain unchanged. These could optionally be moved into `pyproject.toml` in a future cleanup, but that is out of scope.

## Verification

1. `pip install -e .` succeeds (editable install)
2. `python -m build` produces sdist and wheel in `dist/`
3. `nox -s test-3.12` passes
4. `twine check dist/*` validates the built distributions
5. Entry point is registered: `pip show uptrace` shows correct metadata
6. Version is correct: `python -c "import uptrace; print(uptrace.__version__)"` outputs `1.40.0`

## Risk

Low. The project is pure Python with no C extensions, uses src-layout (well supported by hatchling), and the upstream ecosystem has already validated this exact pattern.
