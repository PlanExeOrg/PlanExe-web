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
YYYYMMDD_descriptive_name.zip              # Modified PlanExe output (with GA injected)
YYYYMMDD_descriptive_name_report.html      # The HTML report (extracted from zip, with GA)
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

The PlanExe zip may have two different structures:
- **With wrapper directory**: Files inside a `YYYYMMDD_descriptive_name/` folder — the folder name is the canonical plan name.
- **Flat (no wrapper directory)**: Files at the zip root with a UUID-style filename (e.g. `9a202a96-240d-4465-b6bd-218414e09c10.zip`). In this case, the plan name must be derived from the content (see Step 1 below).

Key files inside the zip:
- `001-2-plan.txt` — The original prompt. Starts with `Plan:\n` and ends with `\nToday's date:\n...`. Strip these wrapper lines to get the clean prompt.
- `001-1-start_time.json` — Contains `server_iso_utc` with the plan generation timestamp. Use this to derive the `YYYYMMDD` date prefix.
- `030-report.html` — The rendered HTML report. Its `<title>` tag contains the plan title, useful for deriving the descriptive name portion.
- Various JSON files (analysis artifacts, not needed for the website).

### Google Analytics injection

The original zip from PlanExe does **not** include Google Analytics. Before the zip is stored in the repo, the GA snippet must be injected into `030-report.html`. Insert this snippet immediately after the `<title>...</title>` tag:

```html
<script async src="https://www.googletagmanager.com/gtag/js?id=G-2F6NE7JWTR"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-2F6NE7JWTR');
</script>
```

The zip stored in the repo is always the **modified** version with GA included — the original zip without GA is deleted after processing.

### Image processing

The `upsert_plan/` directory contains `convert_images.py` (requires Python 3.9+ and Pillow) which generates two JPEG variants from a source image placed in `upsert_plan/input/`:
- `*-big.jpg`: max dimension 1024px, ≤300KB → written to `upsert_plan/output/`
- `*-thumbnail.jpg`: fixed width 256px, proportional height → written to `upsert_plan/output/`

## The upsert_plan/ directory

This directory is the central workspace for all plan processing. It contains:
- `input/` — Drop zone for the original PlanExe zip file and image file for the thumbnail
- `output/` — Where processed files are written (modified zip, converted images)
- `process_plan_zip.py` — **Zip processing script** (stdlib only, no dependencies). Handles unzip, GA injection, prompt/title extraction, and re-zip in one step.
- `convert_images.py` — Image conversion script (requires Pillow)

### Using process_plan_zip.py

Place a PlanExe zip in `upsert_plan/input/` and run:
```bash
cd <repo_root>/upsert_plan
python3 process_plan_zip.py
```

The script:
1. Finds the single `.zip` in `input/`
2. Extracts the prompt from `001-2-plan.txt` (strips wrapper lines)
3. Injects Google Analytics into `030-report.html` after `</title>` (replaces existing GA if present)
4. Extracts the title from the `<title>` tag
5. Writes a modified zip to `output/` (preserves original zip structure)

Output to stdout (parseable):
```
TITLE: EuroLens Platform
PROMPT_START
Build and launch an open-source...
PROMPT_END
```

Status messages go to stderr, so `TITLE`/`PROMPT` can be captured cleanly.

Check `upsert_plan/input/` first when the user says they have a new plan. The original zip stays in `input/` — the modified zip goes to `output/`.

## Workflow: Add a new plan

Ask the user for:
1. **Title** for the gallery card
2. **Description** (optional — ask if they want one, suggest omitting if the title speaks for itself)

Check `upsert_plan/input/` for the zip and image files. If they're not there, ask the user to place them there (or provide paths).

Then execute these steps:

### Step 1: Run process_plan_zip.py

```bash
cd <repo_root>/upsert_plan
python3 process_plan_zip.py
```

This handles unzip, GA injection, prompt extraction, and re-zip in one step. Capture the stdout output — it contains the TITLE and PROMPT.

The modified zip is written to `upsert_plan/output/`.

### Step 2: Determine the plan name

Use the TITLE from step 1 and the date from inside the zip (`001-1-start_time.json`) to derive `YYYYMMDD_descriptive_name`:
1. Convert the title to lowercase_with_underscores (e.g. "EuroLens Platform" → `eurolens_platform`)
2. Combine with the date prefix: `YYYYMMDD_descriptive_name`
3. Confirm the name with the user.

### Step 3: Move output files to repo root

Rename the output zip and extract the report:

```bash
mv <repo_root>/upsert_plan/output/<zip_name>.zip <repo_root>/YYYYMMDD_descriptive_name.zip
# Extract just the report from the new zip
unzip -o -j <repo_root>/YYYYMMDD_descriptive_name.zip "*/030-report.html" -d /tmp/
mv /tmp/030-report.html <repo_root>/YYYYMMDD_descriptive_name_report.html
```

### Step 4: Clean up

Delete the original zip from `upsert_plan/input/` and any remaining files from `upsert_plan/output/`. Keep the `.gitkeep` files.

```bash
rm <repo_root>/upsert_plan/input/<original_zip_file>
rm -f <repo_root>/upsert_plan/output/*
```

### Step 5: Process the image

The image file should already be in `upsert_plan/input/`. Rename it to match the plan name before running the converter.

```bash
# Rename the image to match the plan name
mv <repo_root>/upsert_plan/input/<image_file> <repo_root>/upsert_plan/input/YYYYMMDD_descriptive_name.jpg

# Run the converter (ensure venv + pillow are available)
cd <repo_root>/upsert_plan
python3 -m venv .venv 2>/dev/null
source .venv/bin/activate
pip install pillow -q
python3 convert_images.py

# Move outputs to repo root
cp output/YYYYMMDD_descriptive_name-big.jpg <repo_root>/
cp output/YYYYMMDD_descriptive_name-thumbnail.jpg <repo_root>/

# Clean up input and output
rm <repo_root>/upsert_plan/input/YYYYMMDD_descriptive_name.jpg
rm <repo_root>/upsert_plan/output/*
```

If the image is not a JPEG, the converter handles conversion automatically.

### Step 6: Add the YAML entry

Prepend a new entry to the top of `_data/examples.yml`. Use the Edit tool to insert before the first `- title:` line.

Use the PROMPT captured from step 1 stdout. The prompt text goes under `prompt: |` with 4-space indentation. Preserve the original paragraph breaks. Make sure there's proper YAML escaping — the `|` block scalar handles most special characters, but double-check for trailing whitespace issues.

### Step 7: Verify locally

After all files are in place, suggest the user run `bundle exec jekyll serve` to preview. The new plan should appear as the first card in the examples gallery.

## Workflow: Replace/improve an existing plan

Ask the user for:
1. **Which plan to update** (by title or filename prefix)
2. Whether the **prompt has changed** (it often gets more detailed in regenerated plans)
3. Whether a **new image** is needed (usually not — the existing images stay)

Check `upsert_plan/input/` for the new zip file. If it's not there, ask the user to place it there (or provide a path).

Then execute:

### Step 1: Run process_plan_zip.py

Same as "add new plan" step 1. This handles GA injection, prompt/title extraction, and creates the modified zip in `upsert_plan/output/`.

### Step 2: Replace files in repo root

Move the output zip to overwrite the existing zip in the repo root. Extract and replace the `_report.html` file.

### Step 3: Clean up

Delete the original zip from `upsert_plan/input/` and clear `upsert_plan/output/`. Keep the `.gitkeep` files.

### Step 4: Update the prompt (if changed)

Extract `001-2-plan.txt` from the new zip. Compare with the existing prompt in `_data/examples.yml`. If different, update the YAML entry using the Edit tool. Show the user the diff before applying.

### Step 5: Update images (if provided)

If the user provides a new image, place it in `upsert_plan/input/`, process it through `convert_images.py`, and replace the existing `-big.jpg` and `-thumbnail.jpg` files in the repo root.

## Important conventions

- **Commit messages**: Use "Example plan added" for new plans, "improved plan" for updates. These are the established patterns in the repo history.
- **YAML ordering**: Newest plans go at the top of `examples.yml`.
- **Report HTML modification**: The only modification to `030-report.html` is injecting the Google Analytics snippet after `</title>`. Never make other content changes to report files.
- **Date prefix is stable**: When improving a plan, the `YYYYMMDD` prefix stays the same even if the report was regenerated months later. The date reflects when the plan was originally created.
- **Clean up temp files**: Remove all files from `upsert_plan/input/` and `upsert_plan/output/` (except `.gitkeep` in each) after processing.
- **description field**: Some entries have it, some don't. It's used for extra context like linking to the inspiration source. If the user doesn't specify one, omit it.
