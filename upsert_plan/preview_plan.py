#!/usr/bin/env python3
"""
Preview a processed plan on the local Jekyll site.

Temporarily copies output files into the repo, prepends the YAML entry to
``_data/examples.yml``, starts ``bundle exec jekyll serve``, opens the
examples page in the browser, and reverts everything on exit.

Usage::

    cd <repo_root>/upsert_plan
    python3 preview_plan.py          # uses ./output by default
    python3 preview_plan.py --output /path/to/output
"""

from __future__ import annotations

import argparse
import atexit
import shutil
import signal
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "_data"
EXAMPLES_YML = DATA_DIR / "examples.yml"
JEKYLL_PORT = 4000
EXAMPLES_URL = f"http://localhost:{JEKYLL_PORT}/examples/"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview a processed plan on the local Jekyll site.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "output",
        help="Directory containing process_plan.py output (default: ./output)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=JEKYLL_PORT,
        help=f"Jekyll serve port (default: {JEKYLL_PORT})",
    )
    parser.add_argument(
        "--skip-images",
        action="store_true",
        default=False,
        help="Skip checking for image files in output (use when replacing a plan and keeping existing images).",
    )
    return parser.parse_args()


def find_output_files(output_dir: Path, *, skip_images: bool = False) -> dict[str, Path]:
    """Locate the expected output files and return a name->path mapping."""
    files: dict[str, Path] = {}

    yml = output_dir / "example_item.yml"
    if not yml.is_file():
        raise FileNotFoundError(f"Missing {yml}")
    files["yml"] = yml

    for p in sorted(output_dir.iterdir()):
        if p.suffix == ".zip":
            files["zip"] = p
        elif p.name.endswith("_report.html"):
            files["report"] = p
        elif p.name.endswith("-big.jpg"):
            files["big"] = p
        elif p.name.endswith("-thumbnail.jpg"):
            files["thumbnail"] = p

    required = {"zip", "report"}
    if not skip_images:
        required |= {"big", "thumbnail"}
    missing = required - files.keys()
    if missing:
        raise FileNotFoundError(
            f"Missing output files in {output_dir}: {', '.join(sorted(missing))}"
        )

    return files


def main() -> int:
    args = parse_args()
    output_dir: Path = args.output
    port: int = args.port

    if not output_dir.is_dir():
        print(f"Output directory not found: {output_dir}", file=sys.stderr)
        return 1

    # --- Locate output files ---
    try:
        files = find_output_files(output_dir, skip_images=args.skip_images)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    # --- Back up examples.yml ---
    original_yml = EXAMPLES_YML.read_text(encoding="utf-8")

    # Track files we copy so we can clean up.
    copied: list[Path] = []

    def cleanup() -> None:
        """Revert examples.yml and remove copied files."""
        print("\nCleaning up preview files...", file=sys.stderr)
        EXAMPLES_YML.write_text(original_yml, encoding="utf-8")
        for p in copied:
            if p.exists():
                p.unlink()
        print("Reverted all preview changes.", file=sys.stderr)

    atexit.register(cleanup)

    # --- Copy asset files to repo root ---
    for key in ("zip", "report", "big", "thumbnail"):
        if key not in files:
            continue
        src = files[key]
        dest = REPO_ROOT / src.name
        shutil.copy2(src, dest)
        copied.append(dest)
        print(f"Copied {src.name} -> repo root", file=sys.stderr)

    # --- Prepend YAML entry ---
    new_entry = files["yml"].read_text(encoding="utf-8")
    EXAMPLES_YML.write_text(new_entry + "\n" + original_yml, encoding="utf-8")
    print("Prepended example_item.yml to _data/examples.yml", file=sys.stderr)

    # --- Start Jekyll ---
    # Ruby 3.3 is required (GitHub Pages doesn't support Ruby 4.x yet).
    # Homebrew installs it at /opt/homebrew/opt/ruby@3.3/bin.
    env = dict(__import__("os").environ)
    ruby33_bin = "/opt/homebrew/opt/ruby@3.3/bin"
    env["PATH"] = ruby33_bin + ":" + env.get("PATH", "")

    print(f"\nStarting Jekyll on port {port}...", file=sys.stderr)
    jekyll = subprocess.Popen(
        ["bundle", "exec", "jekyll", "serve", "--port", str(port)],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    # Forward SIGINT/SIGTERM to the Jekyll process.
    def _signal_handler(sig: int, frame: object) -> None:
        jekyll.terminate()

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    # Wait for Jekyll to be ready, then open the browser.
    url = f"http://localhost:{port}/examples/"
    opened = False

    try:
        for line in iter(jekyll.stdout.readline, ""):
            sys.stderr.write(line)
            if not opened and "Server running" in line:
                print(f"\nOpening {url}", file=sys.stderr)
                webbrowser.open(url)
                opened = True

        jekyll.wait()
    except Exception:
        jekyll.terminate()
        jekyll.wait()

    return jekyll.returncode or 0


if __name__ == "__main__":
    sys.exit(main())
