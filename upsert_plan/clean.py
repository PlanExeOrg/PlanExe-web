#!/usr/bin/env python3
"""
Remove all processed files from input/ and output/, preserving .gitkeep.
"""

from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
KEEP = {".gitkeep"}


def clean_dir(d: Path) -> None:
    if not d.is_dir():
        return
    for p in sorted(d.iterdir()):
        if p.name in KEEP:
            continue
        if p.is_file():
            p.unlink()
            print(f"  removed {p.name}")


def main() -> None:
    for name in ("input", "output"):
        d = SCRIPT_DIR / name
        print(f"{name}/")
        clean_dir(d)


if __name__ == "__main__":
    main()
