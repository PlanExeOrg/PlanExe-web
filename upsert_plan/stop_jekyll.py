#!/usr/bin/env python3
"""
Stop the local Jekyll server without killing the browser.

Uses pkill to target only the Jekyll process, leaving Firefox and other
applications untouched.

Usage::

    cd <repo_root>/upsert_plan
    python3 stop_jekyll.py
"""

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    result = subprocess.run(
        ["pkill", "-f", "jekyll serve"],
        capture_output=True,
    )
    if result.returncode == 0:
        print("Jekyll server stopped.", file=sys.stderr)
    else:
        print("No Jekyll server running.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
