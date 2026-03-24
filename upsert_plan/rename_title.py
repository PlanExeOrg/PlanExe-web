#!/usr/bin/env python3
"""
Replace the title of an existing plan in ``_data/examples.yml``.

Matches the plan by its ``report_link`` prefix derived from the zip
filename, then overwrites the ``- title:`` line with the new title.

Usage::

    cd <repo_root>/upsert_plan
    python3 rename_title.py 20260318_eurolens_platform.zip "New Title Here"
    python3 rename_title.py 20260318_eurolens_platform "New Title Here"
    python3 rename_title.py 20260318_eurolens_platform.zip "New Title" --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_YML = REPO_ROOT / "_data" / "examples.yml"

# Each YAML entry starts with "- title:" at column 0.
_ENTRY_START_RE = re.compile(r"^- title:", re.MULTILINE)
_REPORT_LINK_RE = re.compile(r"^\s*report_link:\s*(\S+)", re.MULTILINE)
_TITLE_RE = re.compile(r"^- title:\s*(.+)$", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Replace the title of a plan in _data/examples.yml.",
    )
    parser.add_argument(
        "plan",
        help=(
            "Plan identifier: a zip filename (e.g. 20260318_eurolens_platform.zip) "
            "or just the YYYYMMDD_name portion."
        ),
    )
    parser.add_argument(
        "title",
        help="The new title to set.",
    )
    parser.add_argument(
        "--examples",
        type=Path,
        default=EXAMPLES_YML,
        help=f"Path to examples.yml (default: {EXAMPLES_YML})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without writing.",
    )
    return parser.parse_args()


def plan_name_from_arg(arg: str) -> str:
    """Normalize a plan argument to the YYYYMMDD_name form.

    Accepts:
      - 20260318_eurolens_platform.zip
      - 20260318_eurolens_platform
    """
    name = arg
    if name.endswith(".zip"):
        name = name[: -len(".zip")]
    return name


def extract_plan_name(entry_text: str) -> str | None:
    """Extract the YYYYMMDD_name portion from a report_link field."""
    m = _REPORT_LINK_RE.search(entry_text)
    if not m:
        return None
    link = m.group(1)
    if link.endswith("_report.html"):
        return link[: -len("_report.html")]
    return link


def extract_title(entry_text: str) -> str | None:
    """Extract the current title from an entry."""
    m = _TITLE_RE.search(entry_text)
    if not m:
        return None
    return m.group(1).strip()


def split_entries(yml_text: str) -> list[str]:
    """Split examples.yml into individual entry strings."""
    starts = [m.start() for m in _ENTRY_START_RE.finditer(yml_text)]
    if not starts:
        return []

    entries: list[str] = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(yml_text)
        entries.append(yml_text[start:end])

    return entries


def main() -> int:
    args = parse_args()
    target_plan = plan_name_from_arg(args.plan)
    new_title = args.title
    examples_path: Path = args.examples

    # --- Read examples.yml ---
    if not examples_path.is_file():
        print(f"Missing {examples_path}", file=sys.stderr)
        return 1

    existing_text = examples_path.read_text(encoding="utf-8")
    entries = split_entries(existing_text)

    # --- Find the matching entry ---
    match_index: int | None = None
    for i, entry in enumerate(entries):
        if extract_plan_name(entry) == target_plan:
            match_index = i
            break

    if match_index is None:
        print(f"No entry found for plan: {target_plan}", file=sys.stderr)
        return 1

    old_title = extract_title(entries[match_index])

    # --- Replace the title line ---
    updated_entry = _TITLE_RE.sub(f"- title: {new_title}", entries[match_index], count=1)
    entries[match_index] = updated_entry

    result = "".join(entries).rstrip("\n") + "\n"

    # --- Write or dry-run ---
    if args.dry_run:
        print(f"DRY RUN: would rename \"{old_title}\" -> \"{new_title}\"")
        print(f"Plan: {target_plan}")
        return 0

    examples_path.write_text(result, encoding="utf-8")
    print(f"Renamed \"{old_title}\" -> \"{new_title}\"", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
