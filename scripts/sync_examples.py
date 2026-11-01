#!/usr/bin/env python3
"""Sync uptrace/OpenTelemetry pins in example/*/requirements.txt.

Versions are taken from src/uptrace/version.py and pyproject.toml.

Usage:
    python scripts/sync_examples.py          # rewrite requirements.txt files
    python scripts/sync_examples.py --check  # exit 1 if anything is out of sync
"""

import difflib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_versions():
    version_py = (ROOT / "src/uptrace/version.py").read_text()
    uptrace = re.search(r'__version__\s*=\s*"([^"]+)"', version_py).group(1)

    pyproject = (ROOT / "pyproject.toml").read_text()
    sdk = re.search(r'"opentelemetry-sdk\s*~=\s*([^"]+)"', pyproject).group(1)
    contrib = re.search(
        r'"opentelemetry-instrumentation\s*~=\s*([^"]+)"', pyproject
    ).group(1)

    return uptrace, sdk.strip(), contrib.strip()


def rules(uptrace, sdk, contrib):
    return [
        (re.compile(r"^(uptrace)==\S+", re.M), uptrace),
        (re.compile(r"^(opentelemetry-sdk)==\S+", re.M), sdk),
        (re.compile(r"^(opentelemetry-exporter-otlp)==\S+", re.M), sdk),
        (
            re.compile(r"^(opentelemetry-instrumentation(?:-[\w-]+)?)==\S+", re.M),
            contrib,
        ),
    ]


def main():
    check = "--check" in sys.argv[1:]
    uptrace, sdk, contrib = read_versions()
    print(f"uptrace={uptrace} opentelemetry={sdk} contrib={contrib}")

    out_of_sync = []
    for path in sorted(ROOT.glob("example/*/requirements.txt")):
        old = path.read_text()
        new = old
        for pattern, version in rules(uptrace, sdk, contrib):
            new = pattern.sub(lambda m, v=version: f"{m.group(1)}=={v}", new)
        if new == old:
            continue

        rel = str(path.relative_to(ROOT))
        out_of_sync.append(rel)
        if check:
            sys.stdout.writelines(
                difflib.unified_diff(
                    old.splitlines(keepends=True),
                    new.splitlines(keepends=True),
                    fromfile=rel,
                    tofile=rel,
                )
            )
        else:
            path.write_text(new)
            print(f"updated {rel}")

    if check and out_of_sync:
        print("\nexamples are out of sync; run: python scripts/sync_examples.py")
        sys.exit(1)
    if not out_of_sync:
        print("examples are in sync")


if __name__ == "__main__":
    main()
