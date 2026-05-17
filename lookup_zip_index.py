#!/usr/bin/env python3
"""
Look up a single entry in zip_index.json by plan name.

The plan name may be given with or without the trailing ``.zip``. Prints the
matching JSON snippet to stdout, suitable for piping into a ``meta.json`` file.

Usage::

    python3 lookup_zip_index.py 20250101_india_census
    python3 lookup_zip_index.py 20250101_india_census.zip
    python3 lookup_zip_index.py 20250101_india_census > meta.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
INDEX_PATH = REPO_ROOT / "zip_index.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="Plan name (with or without .zip suffix)")
    args = parser.parse_args()

    filename = args.name if args.name.endswith(".zip") else f"{args.name}.zip"

    try:
        data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"Index not found: {INDEX_PATH}", file=sys.stderr)
        return 1

    for item in data.get("items", []):
        if item.get("filename") == filename:
            print(json.dumps(item, indent=2))
            return 0

    print(f"No entry for {filename} in {INDEX_PATH.name}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
