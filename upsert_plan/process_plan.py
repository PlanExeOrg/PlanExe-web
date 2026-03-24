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
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
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


def extract_date_prefix(start_time_json: str) -> str:
    """Parse ``001-1-start_time.json`` and return a ``YYYYMMDD`` date string."""
    data = json.loads(start_time_json)
    # Prefer server_iso_utc, fall back to server_iso_local.
    iso_str = data.get("server_iso_utc") or data.get("server_iso_local", "")
    # Extract just the date portion (first 10 chars: "2026-03-18").
    date_part = iso_str[:10]
    return date_part.replace("-", "")


def title_to_slug(title: str) -> str:
    """Convert a title like ``"EuroLens Platform"`` to ``eurolens_platform``."""
    # Normalize unicode, strip accents.
    nfkd = unicodedata.normalize("NFKD", title)
    ascii_text = nfkd.encode("ascii", "ignore").decode("ascii")
    # Lowercase, replace non-alphanumeric runs with underscore, strip edges.
    slug = re.sub(r"[^a-z0-9]+", "_", ascii_text.lower()).strip("_")
    return slug


def derive_canonical_name(date_prefix: str, title: str) -> str:
    """Combine a ``YYYYMMDD`` date prefix with a title slug."""
    slug = title_to_slug(title)
    if not date_prefix or not slug:
        raise ValueError(
            f"Cannot derive canonical name: date={date_prefix!r}, title={title!r}"
        )
    return f"{date_prefix}_{slug}"


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


_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}

_CONVERT_IMAGES_SCRIPT = Path(__file__).resolve().parent / "convert_images.py"


def find_image(input_dir: Path) -> Path | None:
    """Return the first image file in *input_dir*, or ``None``."""
    for p in sorted(input_dir.iterdir()):
        if p.is_file() and p.suffix.lower() in _IMAGE_EXTENSIONS:
            return p
    return None


def process_image(
    image_path: Path, canonical_name: str, output_dir: Path
) -> list[Path]:
    """Run ``convert_images.py`` on *image_path* and return output paths.

    The image is copied into a temporary directory with the canonical name so
    that ``convert_images.py`` produces ``<canonical_name>-big.jpg`` and
    ``<canonical_name>-thumbnail.jpg``.  The originals in ``input/`` are never
    modified.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_input = Path(tmp) / "input"
        tmp_output = Path(tmp) / "output"
        tmp_input.mkdir()
        tmp_output.mkdir()

        # Copy with canonical name, preserving the original extension.
        renamed = tmp_input / f"{canonical_name}{image_path.suffix}"
        shutil.copy2(image_path, renamed)

        result = subprocess.run(
            [
                sys.executable,
                str(_CONVERT_IMAGES_SCRIPT),
                "--input", str(tmp_input),
                "--output", str(tmp_output),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(
                f"convert_images.py failed:\n{result.stderr}",
                file=sys.stderr,
            )
            return []

        if result.stdout:
            print(result.stdout, end="", file=sys.stderr)

        # Copy results to the real output directory.
        created: list[Path] = []
        for out_file in sorted(tmp_output.iterdir()):
            dest = output_dir / out_file.name
            shutil.copy2(out_file, dest)
            created.append(dest)

        return created


def yaml_quote_title(title: str) -> str:
    """Quote a title for safe YAML output if it contains special characters.

    Titles containing ``: `` (colon-space) or `` #`` (space-hash) or that
    start with YAML indicator characters need double-quoting so that
    parsers treat them as plain strings rather than nested mappings or
    other YAML constructs.
    """
    needs_quoting = (
        ": " in title
        or " #" in title
        or title.startswith(tuple("[]{}'\"|>&*!%@`"))
    )
    if needs_quoting:
        # Escape existing double-quotes and backslashes inside the title.
        escaped = title.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return title


def generate_example_yml(title: str, prompt: str, canonical_name: str) -> str:
    """Generate a YAML snippet for ``_data/examples.yml``."""
    # Indent every line of the prompt by 4 spaces for the YAML block scalar.
    indented_prompt = "\n".join(
        f"    {line}" if line.strip() else "" for line in prompt.splitlines()
    )
    safe_title = yaml_quote_title(title)
    return (
        f"- title: {safe_title}\n"
        f"  description: |\n"
        f"    PLACEHOLDER_DESCRIPTION\n"
        f"  prompt: |\n"
        f"{indented_prompt}\n"
        f"  report_link: {canonical_name}_report.html\n"
        f"  thumbnail: {canonical_name}-thumbnail.jpg\n"
    )


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

def check_git_branch() -> str | None:
    """Check that we're on the 'main' branch. Return error message or None."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return None  # Not a git repo or git not available — skip check.
        branch = result.stdout.strip()
        if branch != "main":
            return (
                f"ERROR: Current branch is '{branch}', expected 'main'.\n"
                f"Input files are placed on the 'main' branch. "
                f"If you're in a worktree, exit it first."
            )
    except FileNotFoundError:
        pass  # git not installed — skip check.
    return None


def main() -> int:
    args = parse_args()
    input_dir: Path = args.input
    output_dir: Path = args.output

    # --- Check git branch ---
    branch_error = check_git_branch()
    if branch_error:
        print(branch_error, file=sys.stderr)
        return 1

    if not input_dir.is_dir():
        print(f"Input directory not found: {input_dir}", file=sys.stderr)
        return 1

    # --- Check prerequisites ---
    try:
        zip_path = find_zip(input_dir)
    except (FileNotFoundError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    image_path = find_image(input_dir)
    if image_path is None:
        exts = ", ".join(sorted(_IMAGE_EXTENSIONS))
        print(
            f"No image file found in {input_dir}\n"
            f"Please place an image ({exts}) alongside the zip.",
            file=sys.stderr,
        )
        return 1

    print(f"Found zip:   {zip_path.name}", file=sys.stderr)
    print(f"Found image: {image_path.name}", file=sys.stderr)

    output_dir.mkdir(parents=True, exist_ok=True)

    # 2. Work inside a temporary directory.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        with zipfile.ZipFile(zip_path, "r") as zf:
            prefix = detect_prefix(zf)
            zf.extractall(tmp_dir)

        # Resolve key files.
        plan_path = tmp_dir / resolve_member(prefix, "001-2-plan.txt")
        report_path = tmp_dir / resolve_member(prefix, "030-report.html")
        start_time_path = tmp_dir / resolve_member(prefix, "001-1-start_time.json")

        # --- Extract the prompt ---
        if not plan_path.is_file():
            print(f"Missing 001-2-plan.txt in zip", file=sys.stderr)
            return 1

        prompt = extract_prompt(plan_path.read_text(encoding="utf-8"))

        # --- Process the report ---
        if not report_path.is_file():
            print(f"Missing 030-report.html in zip", file=sys.stderr)
            return 1

        report_html = report_path.read_text(encoding="utf-8")
        title = extract_title(report_html)
        report_html = inject_ga(report_html)
        report_path.write_text(report_html, encoding="utf-8")

        # --- Derive the canonical name ---
        if not start_time_path.is_file():
            print(f"Missing 001-1-start_time.json in zip", file=sys.stderr)
            return 1

        date_prefix = extract_date_prefix(
            start_time_path.read_text(encoding="utf-8")
        )

        try:
            canonical_name = derive_canonical_name(date_prefix, title)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1

        # --- Create the output zip ---
        # The output zip is always named YYYYMMDD_slug.zip and uses that
        # same name as the wrapper directory inside the zip.
        out_zip_path = output_dir / f"{canonical_name}.zip"
        out_prefix = canonical_name + "/"

        root_dir = tmp_dir / prefix.rstrip("/") if prefix else tmp_dir

        with zipfile.ZipFile(out_zip_path, "w", zipfile.ZIP_DEFLATED) as zf_out:
            for file_path in sorted(root_dir.rglob("*")):
                if file_path.is_file():
                    arcname = out_prefix + str(file_path.relative_to(root_dir))
                    zf_out.write(file_path, arcname)

        # --- Copy the GA-injected report to the output directory ---
        out_report_path = output_dir / f"{canonical_name}_report.html"
        out_report_path.write_text(report_html, encoding="utf-8")

    # --- Process image ---
    print(f"Processing image: {image_path.name}", file=sys.stderr)
    created_images = process_image(image_path, canonical_name, output_dir)
    for img in created_images:
        print(f"Output image: {img}", file=sys.stderr)

    # --- Generate example_item.yml ---
    out_yml_path = output_dir / "example_item.yml"
    yml_content = generate_example_yml(title, prompt, canonical_name)
    out_yml_path.write_text(yml_content, encoding="utf-8")

    # --- Print results ---
    print(f"Output zip:    {out_zip_path}", file=sys.stderr)
    print(f"Output report: {out_report_path}", file=sys.stderr)
    print(f"Output yml:    {out_yml_path}", file=sys.stderr)

    print(f"TITLE: {title}")
    print(f"PLAN_NAME: {canonical_name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
