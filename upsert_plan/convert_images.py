#!/usr/bin/env python3
"""
Batch image converter for PlanExe.

Reads every image from the local input directory and emits two JPEGs per source
file in the output directory:
  * <original>-big.jpg      : max dimension capped at 1024px and <= 300 KB
  * <original>-thumbnail.jpg: fixed width of 256px with proportional height
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path
from typing import Iterable, Optional

try:
    from PIL import Image, ImageOps, UnidentifiedImageError
except ModuleNotFoundError as exc:  # pragma: no cover - dependency guard
    sys.stderr.write(
        "Pillow is required to run this script. Install it with 'pip install pillow'.\n"
    )
    raise SystemExit(1) from exc


MAX_BIG_DIMENSION = 1024
MAX_BIG_BYTES = 300 * 1024  # 300 KB
THUMBNAIL_WIDTH = 256
MIN_JPEG_QUALITY = 30
QUALITY_STEP = 5


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate resized JPEG variants.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).resolve().parent / "input",
        help="Directory that contains source images (default: ./input)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "output",
        help="Directory to write converted images (default: ./output)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_dir: Path = args.input
    output_dir: Path = args.output

    if not input_dir.is_dir():
        print(f"Input directory not found: {input_dir}", file=sys.stderr)
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    images = sorted(path for path in input_dir.iterdir() if path.is_file())
    if not images:
        print(f"No files found in {input_dir}, nothing to do.")
        return 0

    for image_path in images:
        try:
            process_image(image_path, output_dir)
        except UnidentifiedImageError:
            print(f"Skipping non-image file: {image_path.name}", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001 - we want context on failures
            print(f"Failed to convert {image_path.name}: {exc}", file=sys.stderr)

    return 0


def process_image(image_path: Path, output_dir: Path) -> None:
    base_name = image_path.stem
    big_path = output_dir / f"{base_name}-big.jpg"
    thumb_path = output_dir / f"{base_name}-thumbnail.jpg"

    with Image.open(image_path) as raw_img:
        # Respect EXIF orientation and convert to RGB for consistent JPEG output.
        prepared = ImageOps.exif_transpose(raw_img).convert("RGB")

        big_img = prepared.copy()
        big_img.thumbnail((MAX_BIG_DIMENSION, MAX_BIG_DIMENSION), Image.LANCZOS)
        save_constrained_jpeg(big_img, big_path, MAX_BIG_BYTES)

        thumb_ratio = THUMBNAIL_WIDTH / prepared.width
        thumb_height = max(1, int(round(prepared.height * thumb_ratio)))
        thumb_img = prepared.resize((THUMBNAIL_WIDTH, thumb_height), Image.LANCZOS)
        thumb_img.save(thumb_path, format="JPEG", optimize=True, quality=85)

        print(f"Created {big_path.name} and {thumb_path.name}")


def save_constrained_jpeg(image: Image.Image, path: Path, max_bytes: int) -> None:
    """
    Encode the provided image as JPEG, decreasing quality and size until it
    satisfies the byte budget. Raises ValueError if the constraint cannot be met.
    """
    candidate = image.copy()

    while candidate.width > 0 and candidate.height > 0:
        encoded = try_quality_levels(candidate, max_bytes)
        if encoded is not None:
            path.write_bytes(encoded)
            return

        # Reduce both dimensions by 10% and retry to stay under the size limit.
        new_width = int(candidate.width * 0.9)
        new_height = int(candidate.height * 0.9)
        if new_width == candidate.width or new_height == candidate.height:
            break

        candidate = candidate.resize((new_width, new_height), Image.LANCZOS)

    raise ValueError(
        f"Unable to save {path.name} under {max_bytes} bytes after resizing attempts."
    )


def try_quality_levels(image: Image.Image, max_bytes: int) -> Optional[bytes]:
    for quality in generate_quality_series():
        encoded = encode_jpeg(image, quality)
        if len(encoded) <= max_bytes:
            return encoded
    return None


def generate_quality_series() -> Iterable[int]:
    return range(95, MIN_JPEG_QUALITY - 1, -QUALITY_STEP)


def encode_jpeg(image: Image.Image, quality: int) -> bytes:
    with io.BytesIO() as buffer:
        image.save(
            buffer,
            format="JPEG",
            quality=quality,
            optimize=True,
            progressive=True,
        )
        return buffer.getvalue()


if __name__ == "__main__":
    sys.exit(main())
