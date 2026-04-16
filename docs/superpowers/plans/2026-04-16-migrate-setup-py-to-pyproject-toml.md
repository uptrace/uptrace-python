# Migrate setup.py to pyproject.toml (Hatchling) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `setup.py` + `setup.cfg` with a single `pyproject.toml` using hatchling, eliminating deprecated `python setup.py` invocations.

**Architecture:** Single `pyproject.toml` with hatchling build backend replaces both `setup.py` and `setup.cfg`. All metadata follows PEP 621. Dynamic versioning reads from existing `src/uptrace/version.py`. Build commands switch from `python setup.py sdist bdist_wheel` to `python -m build`.

**Tech Stack:** hatchling (build backend), build (build frontend), twine (upload), nox (test runner)

**Spec:** `docs/superpowers/specs/2026-04-16-migrate-setup-py-to-pyproject-toml-design.md`

---

### Task 1: Create pyproject.toml

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: Create pyproject.toml with full configuration**

Create `pyproject.toml` in the project root with this exact content:

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

- [ ] **Step 2: Verify hatchling can read the version**

Run: `pip install hatchling && python -c "from hatchling.metadata.core import ProjectMetadata; from hatchling.plugin.manager import PluginManager; import pathlib; m = ProjectMetadata(str(pathlib.Path('.')), PluginManager()); print(m.version)"`

Expected output: `1.40.0`

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "feat: add pyproject.toml with hatchling build backend"
```

---

### Task 2: Remove setup.py and setup.cfg

**Files:**
- Delete: `setup.py`
- Delete: `setup.cfg`

- [ ] **Step 1: Delete setup.py**

```bash
rm setup.py
```

- [ ] **Step 2: Delete setup.cfg**

```bash
rm setup.cfg
```

- [ ] **Step 3: Clean up stale egg-info**

```bash
rm -rf src/uptrace.egg-info
```

- [ ] **Step 4: Verify pip install still works with pyproject.toml only**

```bash
pip install -e .
```

Expected: installs successfully using hatchling backend. No warnings about setup.py.

- [ ] **Step 5: Verify the package metadata is correct**

```bash
pip show uptrace
```

Expected output should include:
- `Name: uptrace`
- `Version: 1.40.0`
- `Author: Uptrace.dev`
- `License: BSD-3-Clause`
- `Requires: opentelemetry-api, opentelemetry-sdk, opentelemetry-exporter-otlp, opentelemetry-instrumentation`

- [ ] **Step 6: Verify the entry point is registered**

```bash
python -c "from importlib.metadata import entry_points; eps = entry_points(group='opentelemetry_distro'); print([(e.name, e.value) for e in eps])"
```

Expected: contains `('uptrace_distro', 'uptrace.distro:UptraceDistro')`

- [ ] **Step 7: Verify the version is importable**

```bash
python -c "import uptrace; print(uptrace.__version__)"
```

Expected: `1.40.0`

- [ ] **Step 8: Commit**

```bash
git rm setup.py setup.cfg
git commit -m "chore: remove setup.py and setup.cfg (replaced by pyproject.toml)"
```

---

### Task 3: Update dev-requirements.txt

**Files:**
- Modify: `dev-requirements.txt`

- [ ] **Step 1: Replace setuptools with build and hatchling**

Replace the full contents of `dev-requirements.txt` with:

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

Changes: removed `setuptools`, added `build` (PyPA build frontend) and `hatchling` (build backend).

- [ ] **Step 2: Verify install works**

```bash
pip install -r dev-requirements.txt
```

Expected: installs without errors.

- [ ] **Step 3: Commit**

```bash
git add dev-requirements.txt
git commit -m "chore: replace setuptools with build and hatchling in dev deps"
```

---

### Task 4: Update Makefile

**Files:**
- Modify: `Makefile`

- [ ] **Step 1: Update the release target**

Replace the full contents of `Makefile` with:

```makefile
.PHONY: all test

deps:
	pip install -r dev-requirements.txt
	pip install .

lint:
	nox -s lint

test:
	nox -s test-3.12

release: test
	rm -rf build dist
	python -m build
	twine upload --skip-existing --verbose dist/*
```

The only change is in the `release` target: `python setup.py sdist bdist_wheel` becomes `python -m build`.

- [ ] **Step 2: Verify build works**

```bash
rm -rf build dist && python -m build
```

Expected: creates `dist/uptrace-1.40.0.tar.gz` and `dist/uptrace-1.40.0-py3-none-any.whl`.

- [ ] **Step 3: Verify the built distributions are valid**

```bash
twine check dist/*
```

Expected: `PASSED` for both sdist and wheel.

- [ ] **Step 4: Commit**

```bash
git add Makefile
git commit -m "chore: update Makefile to use python -m build"
```

---

### Task 5: Update RELEASING.md

**Files:**
- Modify: `RELEASING.md`

- [ ] **Step 1: Update RELEASING.md to reference pyproject.toml**

Replace the full contents of `RELEASING.md` with:

```markdown
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
```

Changes from the original:
- Removed `pip install twine` from prerequisites (already in dev-requirements.txt)
- Step 3: changed `setup.cfg` to `pyproject.toml`

- [ ] **Step 2: Commit**

```bash
git add RELEASING.md
git commit -m "docs: update RELEASING.md for pyproject.toml migration"
```

---

### Task 6: Run full test suite

**Files:** None (verification only)

- [ ] **Step 1: Run nox test suite**

```bash
nox -s test-3.12
```

Expected: all tests pass. This verifies the package installs and imports correctly under the new build system.

- [ ] **Step 2: Run nox lint suite**

```bash
nox -s lint-3.12
```

Expected: linting passes (black, isort, pylint).

- [ ] **Step 3: Verify editable install works in a clean venv**

```bash
python -m venv /tmp/uptrace-test-venv && /tmp/uptrace-test-venv/bin/pip install -e . && /tmp/uptrace-test-venv/bin/python -c "import uptrace; print(uptrace.__version__)" && rm -rf /tmp/uptrace-test-venv
```

Expected: prints `1.40.0`.

- [ ] **Step 4: Verify non-editable install works**

```bash
python -m venv /tmp/uptrace-test-venv2 && /tmp/uptrace-test-venv2/bin/pip install . && /tmp/uptrace-test-venv2/bin/python -c "import uptrace; print(uptrace.__version__)" && rm -rf /tmp/uptrace-test-venv2
```

Expected: prints `1.40.0`.
