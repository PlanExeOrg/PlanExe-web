#!/usr/bin/env python3
"""
Process a PlanExe zip file for the planexe.org examples gallery.

Reads a single .zip from the input directory and performs these steps:
  1. Extracts the prompt from 001-2-plan.txt
  2. Injects Google Analytics into 030-report.html (replaces if already present)
  3. Extracts the title from the <title> tag of 030-report.html
  4. Creates a new zip in the output directory with the modified report

The extracted TITLE and PROMPT are printed to stdout in a parseable format.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

GA_SNIPPET = """\
<script async src="https://www.googletagmanager.com/gtag/js?id=G-2F6NE7JWTR"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-2F6NE7JWTR');
</script>"""

# Regex to match an existing GA block: the async loader script tag followed by
# the inline gtag config script tag.  Tolerates whitespace variations.
_GA_EXISTING_RE = re.compile(
    r'\s*<script[^>]*src=["\']https://www\.googletagmanager\.com/gtag/js\?id=[^"\']*["\'][^>]*>\s*</script>'
    r'\s*<script[^>]*>[\s\S]*?gtag\s*\(\s*[\'"]config[\'"][\s\S]*?</script>',
    re.IGNORECASE,
)

_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_TITLE_CLOSE_RE = re.compile(r"(</title>)", re.IGNORECASE)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Process a PlanExe zip: inject GA, extract prompt & title.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).resolve().parent / "input",
        help="Directory containing the source .zip (default: ./input)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "output",
        help="Directory to write the processed .zip (default: ./output)",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_zip(input_dir: Path) -> Path:
    """Return the single .zip file in *input_dir*, or raise."""
    zips = sorted(p for p in input_dir.iterdir() if p.suffix.lower() == ".zip")
    if not zips:
        raise FileNotFoundError(f"No .zip file found in {input_dir}")
    if len(zips) > 1:
        names = ", ".join(p.name for p in zips)
        raise RuntimeError(
            f"Expected exactly one .zip in {input_dir}, found {len(zips)}: {names}"
        )
    return zips[0]


def detect_prefix(zf: zipfile.ZipFile) -> str:
    """Detect whether the zip has a common wrapper directory.

    Returns the prefix string (e.g. ``"20260318_eurolens_platform/"``) or an
    empty string if the zip contains flat files.
    """
    names = [n for n in zf.namelist() if not n.startswith("__MACOSX")]
    if not names:
        return ""

    # Check if all entries start with the same top-level directory.
    first_parts = {n.split("/", 1)[0] for n in names if "/" in n}
    top_level_files = [n for n in names if "/" not in n and not n.endswith("/")]

    if len(first_parts) == 1 and not top_level_files:
        return first_parts.pop() + "/"
    return ""


def resolve_member(prefix: str, filename: str) -> str:
    """Build the full zip member path for a given filename."""
    return prefix + filename


def extract_prompt(plan_text: str) -> str:
    """Strip the ``Plan:`` prefix and ``Today's date:`` suffix from plan text."""
    # Remove leading "Plan:\n"
    text = plan_text
    if text.startswith("Plan:\n"):
        text = text[len("Plan:\n") :]
    elif text.startswith("Plan:\r\n"):
        text = text[len("Plan:\r\n") :]

    # Remove everything from "\nToday's date:" onward.
    marker = "\nToday's date:"
    idx = text.find(marker)
    if idx != -1:
        text = text[:idx]

    return text.strip()


def extract_title(html: str) -> str:
    """Return the content of the first ``<title>`` tag, or empty string."""
    m = _TITLE_RE.search(html)
    return m.group(1).strip() if m else ""


def inject_ga(html: str) -> str:
    """Ensure the canonical GA snippet is present after ``</title>``.

    If an existing GA block is detected, it is removed first so the canonical
    version replaces it rather than duplicating.
    """
    # Remove any pre-existing GA block.
    html = _GA_EXISTING_RE.sub("", html)

    # Inject the canonical snippet right after </title>.
    def _replacement(m: re.Match) -> str:  # type: ignore[type-arg]
        return m.group(1) + "\n" + GA_SNIPPET

    result, count = _TITLE_CLOSE_RE.subn(_replacement, html, count=1)
    if count == 0:
        print(
            "Warning: no </title> tag found — GA snippet was NOT injected.",
            file=sys.stderr,
        )
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    args = parse_args()
    input_dir: Path = args.input
    output_dir: Path = args.output

    if not input_dir.is_dir():
        print(f"Input directory not found: {input_dir}", file=sys.stderr)
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Locate the zip.
    try:
        zip_path = find_zip(input_dir)
    except (FileNotFoundError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Processing: {zip_path.name}", file=sys.stderr)

    # 2. Work inside a temporary directory.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        with zipfile.ZipFile(zip_path, "r") as zf:
            prefix = detect_prefix(zf)
            zf.extractall(tmp_dir)

        # Resolve key files.
        plan_path = tmp_dir / resolve_member(prefix, "001-2-plan.txt")
        report_path = tmp_dir / resolve_member(prefix, "030-report.html")

        # --- Extract the prompt ---
        if not plan_path.is_file():
            print(f"Missing {plan_path.name} in zip", file=sys.stderr)
            return 1

        prompt = extract_prompt(plan_path.read_text(encoding="utf-8"))

        # --- Process the report ---
        if not report_path.is_file():
            print(f"Missing {report_path.name} in zip", file=sys.stderr)
            return 1

        report_html = report_path.read_text(encoding="utf-8")
        title = extract_title(report_html)
        report_html = inject_ga(report_html)
        report_path.write_text(report_html, encoding="utf-8")

        # --- Create the output zip ---
        out_zip_path = output_dir / zip_path.name
        root_dir = tmp_dir / prefix.rstrip("/") if prefix else tmp_dir

        with zipfile.ZipFile(out_zip_path, "w", zipfile.ZIP_DEFLATED) as zf_out:
            for file_path in sorted(root_dir.rglob("*")):
                if file_path.is_file():
                    arcname = resolve_member(
                        prefix, str(file_path.relative_to(root_dir))
                    )
                    zf_out.write(file_path, arcname)

    # --- Print results ---
    print(f"Output zip: {out_zip_path}", file=sys.stderr)

    print(f"TITLE: {title}")
    print("PROMPT_START")
    print(prompt)
    print("PROMPT_END")

    return 0


if __name__ == "__main__":
    sys.exit(main())
