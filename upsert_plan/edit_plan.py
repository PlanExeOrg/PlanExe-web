#!/usr/bin/env python3
"""
Edit metadata fields of an existing plan in ``_data/examples.yml``.

Supports setting the title, description, and prompt fields.
At least one field must be specified.

Usage::

    cd <repo_root>/upsert_plan
    python3 edit_plan.py 20260318_eurolens_platform --title "New Title"
    python3 edit_plan.py 20260318_eurolens_platform.zip --description "A short description."
    python3 edit_plan.py 20260318_eurolens_platform --prompt "The new prompt text."
    python3 edit_plan.py 20260318_eurolens_platform --title "New" --description "Desc." --prompt "Prompt."
    python3 edit_plan.py 20260318_eurolens_platform --description ""   # removes description
    python3 edit_plan.py 20260318_eurolens_platform --title "New" --dry-run
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
        description="Edit metadata fields of a plan in _data/examples.yml.",
    )
    parser.add_argument(
        "plan",
        help=(
            "Plan identifier: a zip filename (e.g. 20260318_eurolens_platform.zip) "
            "or just the YYYYMMDD_name portion."
        ),
    )
    parser.add_argument(
        "--title",
        help="Set the title.",
    )
    parser.add_argument(
        "--description",
        help='Set the description. Use "" to remove it.',
    )
    parser.add_argument(
        "--prompt",
        help="Set the prompt.",
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
    args = parser.parse_args()

    if args.title is None and args.description is None and args.prompt is None:
        parser.error("At least one of --title, --description, or --prompt is required.")

    return args


def plan_name_from_arg(arg: str) -> str:
    """Normalize a plan argument to the YYYYMMDD_name form."""
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


def set_title(entry: str, new_title: str) -> str:
    """Replace the title line in an entry."""
    return _TITLE_RE.sub(f"- title: {new_title}", entry, count=1)


def _find_block_field(entry: str, field_name: str) -> tuple[int, int] | None:
    """Find the start and end offsets of a YAML block scalar field.

    Returns (start, end) where entry[start:end] is the full field including
    its value lines. Returns None if the field is not present.
    """
    pattern = re.compile(
        rf"^  {field_name}:\s*\|?\s*\n", re.MULTILINE
    )
    m = pattern.search(entry)
    if not m:
        return None
    field_start = m.start()
    # Find where the field's indented content ends.
    pos = m.end()
    while pos < len(entry):
        line_end = entry.find("\n", pos)
        if line_end == -1:
            line_end = len(entry)
        line = entry[pos:line_end]
        # Empty lines are part of the block.
        if line.strip() == "":
            pos = line_end + 1
            continue
        # Lines with 4+ spaces of indentation are continuation.
        if line.startswith("    "):
            pos = line_end + 1
            continue
        # Anything else ends the block.
        break
    return (field_start, pos)


def set_block_field(entry: str, field_name: str, value: str, after_field: str) -> str:
    """Set a YAML block scalar field. If value is empty, remove the field.

    If the field doesn't exist and value is non-empty, insert it after
    ``after_field``.
    """
    existing = _find_block_field(entry, field_name)

    if not value:
        # Remove the field if it exists.
        if existing:
            start, end = existing
            return entry[:start] + entry[end:]
        return entry

    # Format the new field as a YAML block scalar.
    indented_lines = "\n".join(f"    {line}" for line in value.splitlines())
    new_block = f"  {field_name}: |\n{indented_lines}\n"

    if existing:
        start, end = existing
        return entry[:start] + new_block + entry[end:]

    # Insert after the specified field.
    after = _find_block_field(entry, after_field)
    if after:
        _, insert_pos = after
        return entry[:insert_pos] + new_block + entry[insert_pos:]

    # Fallback: insert after the title line.
    m = _TITLE_RE.search(entry)
    if m:
        insert_pos = m.end() + 1  # after the newline
        return entry[:insert_pos] + new_block + entry[insert_pos:]

    return entry


def main() -> int:
    args = parse_args()
    target_plan = plan_name_from_arg(args.plan)
    examples_path: Path = args.examples

    if not examples_path.is_file():
        print(f"Missing {examples_path}", file=sys.stderr)
        return 1

    existing_text = examples_path.read_text(encoding="utf-8")
    entries = split_entries(existing_text)

    # Find the matching entry.
    match_index: int | None = None
    for i, entry in enumerate(entries):
        if extract_plan_name(entry) == target_plan:
            match_index = i
            break

    if match_index is None:
        print(f"No entry found for plan: {target_plan}", file=sys.stderr)
        return 1

    entry = entries[match_index]
    changes: list[str] = []

    if args.title is not None:
        old_title = extract_title(entry)
        entry = set_title(entry, args.title)
        changes.append(f'title: "{old_title}" -> "{args.title}"')

    if args.description is not None:
        entry = set_block_field(entry, "description", args.description, after_field="title")
        if args.description:
            changes.append("description: set")
        else:
            changes.append("description: removed")

    if args.prompt is not None:
        entry = set_block_field(entry, "prompt", args.prompt, after_field="description")
        if args.prompt:
            changes.append("prompt: set")
        else:
            changes.append("prompt: removed")

    entries[match_index] = entry
    result = "".join(entries).rstrip("\n") + "\n"

    if args.dry_run:
        for change in changes:
            print(f"DRY RUN: {change}")
        print(f"Plan: {target_plan}")
        return 0

    examples_path.write_text(result, encoding="utf-8")
    for change in changes:
        print(f"Changed {change}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
