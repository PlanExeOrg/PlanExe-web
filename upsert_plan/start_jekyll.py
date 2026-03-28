#!/usr/bin/env python3
"""
Start the local Jekyll server and open the browser.

Kills any existing Jekyll process first, then starts a new one.
Waits for the server to be ready before opening browser tabs.

Usage::

    cd <repo_root>/upsert_plan
    python3 start_jekyll.py                              # opens /examples/
    python3 start_jekyll.py --plan 20250427_555project   # also opens the report page
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import webbrowser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
JEKYLL_PORT = 4000
RUBY_BIN = "/opt/homebrew/opt/ruby@3.3/bin"


def kill_existing_jekyll() -> None:
    """Kill any running Jekyll serve process."""
    result = subprocess.run(
        ["pkill", "-f", "jekyll serve"],
        capture_output=True,
    )
    if result.returncode == 0:
        print("Killed existing Jekyll process.", file=sys.stderr)


def start_jekyll() -> subprocess.Popen:
    """Start Jekyll serve as a subprocess and return the Popen object."""
    env = dict(os.environ)
    env["PATH"] = RUBY_BIN + ":" + env.get("PATH", "")
    env["LANG"] = "en_US.UTF-8"
    env["LC_ALL"] = "en_US.UTF-8"

    proc = subprocess.Popen(
        ["bundle", "exec", "jekyll", "serve", "--port", str(JEKYLL_PORT)],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return proc


def wait_for_ready(proc: subprocess.Popen) -> bool:
    """Read Jekyll stdout until 'Server running' appears. Returns True if ready."""
    assert proc.stdout is not None
    for line in iter(proc.stdout.readline, ""):
        sys.stderr.write(line)
        if "Server running" in line:
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Start Jekyll and open the browser.",
    )
    parser.add_argument(
        "--plan",
        type=str,
        default=None,
        help="Plan name (e.g. 20250427_555project) to also open the report page.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=JEKYLL_PORT,
        help=f"Jekyll serve port (default: {JEKYLL_PORT})",
    )
    args = parser.parse_args()
    port = args.port

    kill_existing_jekyll()

    print(f"Starting Jekyll on port {port}...", file=sys.stderr)
    proc = start_jekyll()

    if not wait_for_ready(proc):
        print("Jekyll failed to start.", file=sys.stderr)
        return 1

    # Open browser tabs.
    examples_url = f"http://localhost:{port}/examples/"
    print(f"Opening {examples_url}", file=sys.stderr)
    webbrowser.open(examples_url)

    if args.plan:
        report_url = f"http://localhost:{port}/{args.plan}_report.html"
        print(f"Opening {report_url}", file=sys.stderr)
        webbrowser.open(report_url)

    print(f"Jekyll running (PID {proc.pid}). Stop with: python3 stop_jekyll.py", file=sys.stderr)

    # Detach from Jekyll stdout so the script can exit while Jekyll keeps running.
    # Close our end of the pipe — Jekyll continues writing to /dev/null effectively.
    proc.stdout.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
