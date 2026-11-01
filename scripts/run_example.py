#!/usr/bin/env python3
"""Smoke-test an example from example/.

Usage:
    python scripts/run_example.py --list            # print example names
    python scripts/run_example.py --install NAME    # install NAME's dependencies
    python scripts/run_example.py NAME [NAME...]    # run examples

Dependencies are installed into the current Python environment. The local
uptrace source is installed instead of the `uptrace` pin from requirements.txt,
so examples are tested against the code in this repo.

UPTRACE_DSN is not required: without it uptrace is disabled and nothing is sent.
"""

import os
import re
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable

# kind:
#   script - must exit 0 within the timeout
#   daemon - runs forever; must still be alive after a few seconds
#   server - must answer HTTP 200 on every URL, then `client` (if any) must exit 0
EXAMPLES = {
    "basic": {"kind": "script", "cmd": [PY, "main.py"]},
    "otel-api": {"kind": "script", "cmd": [PY, "main.py"]},
    "metrics": {"kind": "daemon", "cmd": [PY, "main.py"]},
    "otlp-logs": {"kind": "script", "cmd": [PY, "main.py"]},
    "otlp-metrics": {"kind": "daemon", "cmd": [PY, "main.py"]},
    "otlp-traces": {"kind": "script", "cmd": [PY, "main.py"]},
    "otlp-traces-http": {"kind": "script", "cmd": [PY, "main.py"]},
    "flask": {
        "kind": "server",
        "cmd": [PY, "main.py"],
        "urls": ["http://127.0.0.1:8000/", "http://127.0.0.1:8000/hello/world"],
    },
    "flask-auto-instrumentation": {
        "kind": "server",
        "cmd": ["opentelemetry-instrument", PY, "main.py"],
        "urls": ["http://127.0.0.1:8000/", "http://127.0.0.1:8000/hello/world"],
    },
    "flask-gunicorn": {
        "kind": "server",
        "cmd": ["gunicorn", "main", "-c", "gunicorn.config.py"],
        "urls": ["http://127.0.0.1:8000/", "http://127.0.0.1:8000/hello/world"],
    },
    "flask-uwsgi": {
        "kind": "server",
        "cmd": [
            "uwsgi",
            "--http=127.0.0.1:8000",
            "--wsgi-file=main.py",
            "--callable=application",
            "--master",
            "--enable-threads",
            "--die-on-term",
        ],
        "urls": ["http://127.0.0.1:8000/", "http://127.0.0.1:8000/hello/world"],
    },
    "fastapi": {
        "kind": "server",
        "cmd": ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
        "urls": ["http://127.0.0.1:8000/", "http://127.0.0.1:8000/items/5?q=x"],
        "client": [PY, "client.py"],
    },
    "pyramid": {
        "kind": "server",
        "cmd": [PY, "main.py"],
        "urls": ["http://127.0.0.1:6543/", "http://127.0.0.1:6543/hello/world"],
    },
    "django": {
        "kind": "server",
        "setup": [PY, "manage.py", "migrate", "--noinput"],
        "cmd": [PY, "manage.py", "runserver", "127.0.0.1:8000", "--noreload"],
        "urls": ["http://127.0.0.1:8000/", "http://127.0.0.1:8000/hello/world"],
    },
    "django-postgresql": {
        "kind": "server",
        "setup": [PY, "manage.py", "migrate", "--noinput"],
        "cmd": [PY, "manage.py", "runserver", "127.0.0.1:8000", "--noreload"],
        "urls": ["http://127.0.0.1:8000/", "http://127.0.0.1:8000/hello/world"],
    },
}

SCRIPT_TIMEOUT = 60
DAEMON_ALIVE = 10
SERVER_READY_TIMEOUT = 60


class Failure(Exception):
    pass


def example_dir(name):
    return ROOT / "example" / name


def install(name):
    reqs = example_dir(name) / "requirements.txt"
    text = reqs.read_text() if reqs.exists() else ""
    lines = [l.strip() for l in text.splitlines() if l.strip()[:1] not in ("", "#")]
    other = [l for l in lines if not re.match(r"uptrace\b(?!-)", l)]
    # Examples without requirements.txt rely on uptrace alone.
    uses_uptrace = not reqs.exists() or len(other) < len(lines)

    args = [PY, "-m", "pip", "install"]
    if uses_uptrace:
        args.append(str(ROOT))
    if other:
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("\n".join(other) + "\n")
        args += ["-r", f.name]
    print("+", " ".join(args), flush=True)
    subprocess.run(args, check=True)


def start(cmd, cwd, log):
    print("+", " ".join(cmd), flush=True)
    # Find console scripts (gunicorn, uvicorn, ...) installed next to this Python
    # even when its virtualenv is not activated.
    env = dict(os.environ)
    env["PATH"] = os.pathsep.join([str(Path(PY).parent), env.get("PATH", "")])
    return subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdout=log,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )


def stop(proc):
    if proc.poll() is not None:
        return
    for sig, wait in ((signal.SIGINT, 10), (signal.SIGKILL, 5)):
        try:
            os.killpg(proc.pid, sig)
        except ProcessLookupError:
            return
        try:
            proc.wait(wait)
            return
        except subprocess.TimeoutExpired:
            pass


def run_to_completion(cmd, cwd, log, timeout=SCRIPT_TIMEOUT):
    proc = start(cmd, cwd, log)
    try:
        code = proc.wait(timeout)
    except subprocess.TimeoutExpired:
        stop(proc)
        raise Failure(f"{cmd[-1]} did not exit within {timeout}s")
    finally:
        stop(proc)
    if code != 0:
        raise Failure(f"{' '.join(cmd)} exited with code {code}")


def http_get(url):
    with urllib.request.urlopen(url, timeout=10) as resp:
        resp.read()
        return resp.status


def check_port_free(url):
    parts = urllib.parse.urlsplit(url)
    with socket.socket() as sock:
        if sock.connect_ex((parts.hostname, parts.port)) == 0:
            raise Failure(
                f"port {parts.port} is already in use; stop whatever is listening there"
            )


def wait_ready(proc, url):
    deadline = time.monotonic() + SERVER_READY_TIMEOUT
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise Failure(f"server exited with code {proc.returncode}")
        try:
            http_get(url)
            return
        except (urllib.error.URLError, ConnectionError, OSError):
            time.sleep(0.5)
    raise Failure(f"server is not ready after {SERVER_READY_TIMEOUT}s")


def run(name):
    spec = EXAMPLES[name]
    cwd = example_dir(name)
    env_note = "set" if os.getenv("UPTRACE_DSN") else "unset"
    print(f"=== {name} ({spec['kind']}, UPTRACE_DSN {env_note})", flush=True)

    with tempfile.TemporaryFile("w+") as log:
        try:
            if "setup" in spec:
                run_to_completion(spec["setup"], cwd, log)

            if spec["kind"] == "script":
                run_to_completion(spec["cmd"], cwd, log)

            elif spec["kind"] == "daemon":
                proc = start(spec["cmd"], cwd, log)
                try:
                    time.sleep(DAEMON_ALIVE)
                    if proc.poll() is not None:
                        raise Failure(f"exited early with code {proc.returncode}")
                finally:
                    stop(proc)

            elif spec["kind"] == "server":
                check_port_free(spec["urls"][0])
                proc = start(spec["cmd"], cwd, log)
                try:
                    wait_ready(proc, spec["urls"][0])
                    for url in spec["urls"]:
                        try:
                            status = http_get(url)
                        except urllib.error.HTTPError as exc:
                            status = exc.code
                        print(f"GET {url} -> {status}", flush=True)
                        if status != 200:
                            raise Failure(f"GET {url} returned {status}")
                    if "client" in spec:
                        run_to_completion(spec["client"], cwd, log)
                finally:
                    stop(proc)

        except Failure as exc:
            log.seek(0)
            print(f"--- output of {name} ---\n{log.read()}--- end ---")
            print(f"FAIL {name}: {exc}", flush=True)
            return False

    print(f"PASS {name}", flush=True)
    return True


def main():
    args = sys.argv[1:]
    if not args or args == ["--help"]:
        print(__doc__)
        sys.exit(2)
    if args == ["--list"]:
        print("\n".join(EXAMPLES))
        return

    do_install = "--install" in args
    names = [a for a in args if a != "--install"]
    unknown = [n for n in names if n not in EXAMPLES]
    if unknown:
        sys.exit(f"unknown example(s): {', '.join(unknown)}")

    on_disk = {p.name for p in (ROOT / "example").iterdir() if p.is_dir()}
    missing = sorted(on_disk - EXAMPLES.keys())
    if missing:
        sys.exit(f"examples without a smoke test in {__file__}: {', '.join(missing)}")

    if do_install:
        for name in names:
            install(name)
        return

    failed = [n for n in names if not run(n)]
    if failed:
        sys.exit(f"failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
