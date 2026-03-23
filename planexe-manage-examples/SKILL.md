---
name: planexe-manage-examples
description: Manage example plans on the PlanExe-web Jekyll site (planexe.org). Use this skill whenever the user wants to add a new example plan, replace or improve an existing plan, update plan thumbnails or images, or modify entries in the examples gallery. Trigger on mentions of "add plan", "new example", "improve plan", "replace plan", "update plan", "examples.yml", "plan zip", "report HTML", or any reference to managing the planexe.org examples gallery — even if the user just says something like "I have a new plan to add" or "this plan needs updating".
---

# Managing Example Plans on PlanExe-web

This skill automates the workflow for adding and updating example plans on the PlanExe-web Jekyll site (planexe.org). The site showcases AI-generated project plans from the PlanExe tool, each displayed as a card in the examples gallery.

## What you need to know

### File structure per plan

Each plan consists of these files in the repo root:

```
YYYYMMDD_descriptive_name.zip              # The raw PlanExe output
YYYYMMDD_descriptive_name_report.html      # The HTML report (extracted from zip)
YYYYMMDD_descriptive_name-big.jpg          # Hero image (max 1024px, ≤300KB)
YYYYMMDD_descriptive_name-thumbnail.jpg    # Gallery thumbnail (256px wide)
```

The date prefix (`YYYYMMDD`) comes from when the plan was generated, not when it's added to the site.

### The examples gallery

All plans are listed in `_data/examples.yml`. Newest entries go at the top. Each entry looks like:

```yaml
- title: Hong Kong Game
  description: |
    Inspired by [The Game](https://www.imdb.com/title/tt0119174/) movie.
  prompt: |
    Produce a modern-day remake of the 1997 psychological thriller...
  report_link: 20260310_hong_kong_game_report.html
  thumbnail: 20260310_hong_kong_game-thumbnail.jpg
```

Fields:
- **title** (required): Short display name for the card
- **description** (optional): Brief context, can include markdown links. Omit if the title is self-explanatory.
- **prompt** (required): The original prompt fed to PlanExe. Use `|` for multiline YAML.
- **report_link** (required): Filename of the HTML report in the repo root
- **thumbnail** (required): Filename of the thumbnail image in the repo root

### Inside the zip file

The PlanExe zip contains a folder named `YYYYMMDD_descriptive_name/` with key files:
- `001-2-plan.txt` — The original prompt. Starts with `Plan:\n` and ends with `\nToday's date:\n...`. Strip these wrapper lines to get the clean prompt.
- `030-report.html` — The rendered HTML report to display on the site.
- Various JSON files (analysis artifacts, not needed for the website).

### Image processing

The repo includes `image_converter/convert_images.py` (requires Python 3.9+ and Pillow) which generates two JPEG variants from a source image:
- `*-big.jpg`: max dimension 1024px, ≤300KB
- `*-thumbnail.jpg`: fixed width 256px, proportional height

## Workflow: Add a new plan

Ask the user for:
1. **Path to the zip file** from PlanExe
2. **Path to an image file** for the thumbnail (user generates/screenshots this separately)
3. **Title** for the gallery card
4. **Description** (optional — ask if they want one, suggest omitting if the title speaks for itself)

Then execute these steps:

### Step 1: Determine the plan name

Extract the folder name from inside the zip. This is the canonical `YYYYMMDD_descriptive_name` used for all files.

```bash
# The first entry that's a directory tells you the name
unzip -l <zip_path> | head -5
```

### Step 2: Copy zip to repo root

```bash
cp <zip_path> <repo_root>/YYYYMMDD_descriptive_name.zip
```

### Step 3: Extract the HTML report

```bash
unzip -o -j <zip_path> "YYYYMMDD_descriptive_name/030-report.html" -d /tmp/
cp /tmp/030-report.html <repo_root>/YYYYMMDD_descriptive_name_report.html
```

### Step 4: Extract the prompt

```bash
unzip -o -j <zip_path> "YYYYMMDD_descriptive_name/001-2-plan.txt" -d /tmp/
```

Read `/tmp/001-2-plan.txt`, strip the `Plan:\n` prefix and the `\nToday's date:\n...` suffix (and any trailing date/metadata lines). The remaining text is the prompt for the YAML entry.

### Step 5: Process the image

```bash
# Clear the input directory and copy the new image
rm -f <repo_root>/image_converter/input/*
cp <image_path> <repo_root>/image_converter/input/YYYYMMDD_descriptive_name.jpg

# Run the converter (ensure venv + pillow are available)
cd <repo_root>/image_converter
python3 -m venv .venv 2>/dev/null
source .venv/bin/activate
pip install pillow -q
python3 convert_images.py

# Move outputs to repo root
cp output/YYYYMMDD_descriptive_name-big.jpg <repo_root>/
cp output/YYYYMMDD_descriptive_name-thumbnail.jpg <repo_root>/
```

If the image is not a JPEG, the converter handles conversion automatically.

### Step 6: Add the YAML entry

Prepend a new entry to the top of `_data/examples.yml`. Use the Edit tool to insert before the first `- title:` line.

The prompt text goes under `prompt: |` with 4-space indentation. Preserve the original paragraph breaks. Make sure there's proper YAML escaping — the `|` block scalar handles most special characters, but double-check for trailing whitespace issues.

### Step 7: Verify locally

After all files are in place, suggest the user run `bundle exec jekyll serve` to preview. The new plan should appear as the first card in the examples gallery.

## Workflow: Replace/improve an existing plan

Ask the user for:
1. **Which plan to update** (by title or filename prefix)
2. **Path to the new zip file**
3. Whether the **prompt has changed** (it often gets more detailed in regenerated plans)
4. Whether a **new image** is needed (usually not — the existing images stay)

Then execute:

### Step 1: Replace the zip

Overwrite the existing zip in the repo root.

### Step 2: Extract and replace the HTML report

Same extraction as "add new plan" step 3, overwriting the existing `_report.html` file.

### Step 3: Update the prompt (if changed)

Extract `001-2-plan.txt` from the new zip. Compare with the existing prompt in `_data/examples.yml`. If different, update the YAML entry using the Edit tool. Show the user the diff before applying.

### Step 4: Update images (if provided)

If the user provides a new image, process it through `image_converter/` and replace the existing `-big.jpg` and `-thumbnail.jpg` files.

## Important conventions

- **Commit messages**: Use "Example plan added" for new plans, "improved plan" for updates. These are the established patterns in the repo history.
- **YAML ordering**: Newest plans go at the top of `examples.yml`.
- **Don't modify report HTML**: The `_report.html` files are generated artifacts. Never edit their content — just replace them wholesale from the zip.
- **Date prefix is stable**: When improving a plan, the `YYYYMMDD` prefix stays the same even if the report was regenerated months later. The date reflects when the plan was originally created.
- **Clean up temp files**: Remove any files from `/tmp/` and `image_converter/input/` + `image_converter/output/` after processing.
- **description field**: Some entries have it, some don't. It's used for extra context like linking to the inspiration source. If the user doesn't specify one, omit it.
