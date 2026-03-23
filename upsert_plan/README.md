# Image Converter

This helper script resizes every image in the local `input/` directory and
writes two JPEG versions per source file into `output/`:

- `<name>-big.jpg` — longest edge at most 1024 px, with the file capped at
  300 KB (quality is reduced or the image slightly downscales until it fits).
- `<name>-thumbnail.jpg` — width fixed at 256 px while keeping the original
  aspect ratio.

## Prerequisites

- Python 3.9+ (standard library only, apart from Pillow).
- Pillow imaging library (install inside a virtual environment, see below).

### Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install pillow
```

When you are done, leave the virtual environment with:

```bash
deactivate
```

## Usage

```bash
python3 convert_images.py
```

Optional flags:

- `--input DIR` – override the source directory (default: `./input`).
- `--output DIR` – override the destination directory (default: `./output`).

Each run keeps any previously generated files; delete the `output/` contents if
you need a clean slate.

## Notes

- Non-image files inside `input/` are skipped with a warning.
- Source files remain untouched; only JPEGs are written to `output/`.
