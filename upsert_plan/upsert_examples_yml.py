#!/usr/bin/env python3
"""
Upsert an example entry into ``_data/examples.yml``.

Reads ``output/example_item.yml`` and either:
  - **Updates** the matching entry in ``_data/examples.yml`` if a plan with
    the same ``report_link`` prefix (``YYYYMMDD_name``) already exists.
  - **Prepends** the entry to the top of the file if it's new.

Usage::

    cd <repo_root>/upsert_plan
    python3 upsert_examples_yml.py
    python3 upsert_examples_yml.py --output /path/to/output
    python3 upsert_examples_yml.py --dry-run   # show what would happen
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upsert an example entry into _data/examples.yml.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "output",
        help="Directory containing example_item.yml (default: ./output)",
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


def extract_plan_name(entry_text: str) -> str | None:
    """Extract the YYYYMMDD_name portion from a report_link field."""
    m = _REPORT_LINK_RE.search(entry_text)
    if not m:
        return None
    # report_link: 20260318_eurolens_platform_report.html
    # Strip _report.html suffix to get the plan name.
    link = m.group(1)
    if link.endswith("_report.html"):
        return link[: -len("_report.html")]
    return link


def split_entries(yml_text: str) -> list[str]:
    """Split examples.yml into individual entry strings.

    Each entry starts with ``- title:`` and ends just before the next
    ``- title:`` or at EOF.
    """
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
    output_dir: Path = args.output
    examples_path: Path = args.examples

    # --- Read the new entry ---
    item_path = output_dir / "example_item.yml"
    if not item_path.is_file():
        print(f"Missing {item_path}", file=sys.stderr)
        return 1

    new_entry = item_path.read_text(encoding="utf-8")
    new_plan_name = extract_plan_name(new_entry)

    if not new_plan_name:
        print("Could not extract plan name from example_item.yml", file=sys.stderr)
        return 1

    # --- Read the existing examples.yml ---
    if not examples_path.is_file():
        print(f"Missing {examples_path}", file=sys.stderr)
        return 1

    existing_text = examples_path.read_text(encoding="utf-8")
    entries = split_entries(existing_text)

    # --- Check for an existing entry with the same plan name ---
    match_index: int | None = None
    for i, entry in enumerate(entries):
        entry_plan_name = extract_plan_name(entry)
        if entry_plan_name == new_plan_name:
            match_index = i
            break

    if match_index is not None:
        action = "UPDATE"
        entries[match_index] = new_entry.rstrip("\n") + "\n\n"
    else:
        action = "PREPEND"
        # Ensure new entry ends with a blank line separator.
        entries.insert(0, new_entry.rstrip("\n") + "\n\n")

    result = "".join(entries).rstrip("\n") + "\n"

    # --- Write or dry-run ---
    if args.dry_run:
        print(f"DRY RUN: would {action} entry for {new_plan_name}")
        print(f"Plan name: {new_plan_name}")
        if match_index is not None:
            print(f"Replacing entry at position {match_index}")
        else:
            print("Adding as first entry")
        return 0

    examples_path.write_text(result, encoding="utf-8")
    print(f"{action}: {new_plan_name}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
