#!/usr/bin/env python3
"""
Build an index of all *.zip files in the repo root.

For each zip:
- last commit id and commit date (ISO 8601) from git
- sha256 of the file contents

Output: zip_index.json in the repo root, with items sorted by filename
ascending and a top-level `generated_at` UTC timestamp.

Usage::

    cd <repo_root>
    python3 build_zip_index.py
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = REPO_ROOT / "zip_index.json"


def last_commit(path: Path) -> tuple[str, str]:
    """Return (commit_id, commit_date_iso) for the most recent commit touching ``path``.

    Returns ("", "") if the file has no commit history (e.g. untracked).
    """
    result = subprocess.run(
        ["git", "log", "-1", "--format=%H%x09%cI", "--", path.name],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    line = result.stdout.strip()
    if not line:
        return "", ""
    commit_id, _, commit_date = line.partition("\t")
    return commit_id, commit_date


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    zips = sorted(REPO_ROOT.glob("*.zip"), key=lambda p: p.name)
    if not zips:
        print("No *.zip files found in repo root.", file=sys.stderr)
        return 1

    items = []
    for zip_path in zips:
        commit_id, commit_date = last_commit(zip_path)
        items.append(
            {
                "filename": zip_path.name,
                "commit_id": commit_id,
                "commit_date": commit_date,
                "sha256": sha256_of(zip_path),
            }
        )
        print(f"  {zip_path.name}", file=sys.stderr)

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "items": items,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)} ({len(items)} items).", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
