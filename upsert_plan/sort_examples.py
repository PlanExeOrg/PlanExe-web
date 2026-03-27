#!/usr/bin/env python3
"""
List the YYYYMMDD_name_report.html files in the repo root,
sorted by the generation timestamp embedded inside each file,
then alphabetically by filename for same-timestamp ties.

Usage::

    cd <repo_root>/upsert_plan
    python3 sort_examples.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
_TIMESTAMP_RE = re.compile(r"Generated on:\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")


def extract_timestamp(path: Path) -> str:
    """Return 'YYYY-MM-DD HH:MM:SS' from inside the HTML, or '' if not found."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        m = _TIMESTAMP_RE.search(text)
        return m.group(1) if m else ""
    except OSError:
        return ""


def main() -> int:
    files = list(REPO_ROOT.glob("*_report.html"))
    if not files:
        print("No *_report.html files found.", file=sys.stderr)
        return 1

    annotated = [(extract_timestamp(f), f.name, f) for f in files]
    annotated.sort(key=lambda x: (x[0], x[1]))

    for timestamp, name, _ in annotated:
        print(json.dumps({"timestamp": timestamp, "filename": name}))

    return 0


if __name__ == "__main__":
    sys.exit(main())
