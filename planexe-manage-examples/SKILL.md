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

The repo includes `image_converter/convert_images.py` (requires Python 3.9+ and Pillow) which generates two JPEG variants from a source image:
- `*-big.jpg`: max dimension 1024px, ≤300KB
- `*-thumbnail.jpg`: fixed width 256px, proportional height

## Input staging directory

The user places files for processing in `upsert_plan/input/` inside the repo root. This is the drop zone for:
- The original PlanExe zip file
- The image file for the thumbnail

Check this directory first when the user says they have a new plan. The original zip is deleted from this directory after processing — only the modified zip (with GA) goes into the repo root.

## Workflow: Add a new plan

Ask the user for:
1. **Title** for the gallery card
2. **Description** (optional — ask if they want one, suggest omitting if the title speaks for itself)

Check `upsert_plan/input/` for the zip and image files. If they're not there, ask the user to place them there (or provide paths).

Then execute these steps:

### Step 1: Determine the plan name and extract

First, check the zip structure to see if it has a wrapper directory or flat files:

```bash
unzip -l <repo_root>/upsert_plan/input/<zip_file> | head -10
```

**If the zip has a wrapper directory** (first entry is `YYYYMMDD_name/`):
```bash
unzip -o <repo_root>/upsert_plan/input/<zip_file> -d <repo_root>/upsert_plan/input/
```
Confirm the directory name follows the `YYYYMMDD_descriptive_name` convention. Rename after extraction if needed.

**If the zip has flat files** (no wrapper directory — common when the zip filename is a UUID):
```bash
# Extract to a temporary directory first
unzip -o <repo_root>/upsert_plan/input/<zip_file> -d <repo_root>/upsert_plan/input/_extracted/
```
Then derive the canonical plan name:
1. Read `_extracted/001-1-start_time.json` to get the date → `YYYYMMDD`
2. Read the `<title>` tag from `_extracted/030-report.html` to get the descriptive name
3. Convert to lowercase_with_underscores (e.g. "EuroLens Platform" → `eurolens_platform`)
4. Combine: `YYYYMMDD_descriptive_name`
5. Rename: `mv _extracted/ YYYYMMDD_descriptive_name/`

Confirm the derived name with the user before proceeding.

### Step 2: Inject Google Analytics into the report

Read `upsert_plan/input/YYYYMMDD_descriptive_name/030-report.html` and insert the GA snippet immediately after the `</title>` closing tag. Use the Edit tool to find the closing `</title>` and insert the snippet right after it:

```html
</title>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-2F6NE7JWTR"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-2F6NE7JWTR');
</script>
```

### Step 3: Extract the prompt

Read `upsert_plan/input/YYYYMMDD_descriptive_name/001-2-plan.txt`, strip the `Plan:\n` prefix and the `\nToday's date:\n...` suffix (and any trailing date/metadata lines). The remaining text is the prompt for the YAML entry.

### Step 4: Create the modified zip

Re-zip the directory (now containing the GA-injected report) and place it in the repo root. Then copy the modified report to the repo root as well.

```bash
cd <repo_root>/upsert_plan/input/
zip -r <repo_root>/YYYYMMDD_descriptive_name.zip YYYYMMDD_descriptive_name/
cp YYYYMMDD_descriptive_name/030-report.html <repo_root>/YYYYMMDD_descriptive_name_report.html
```

### Step 5: Clean up working files

Delete the original zip (without GA), the extracted directory, and any other temp files from `upsert_plan/input/`. Keep the `.gitkeep`.

```bash
rm <repo_root>/upsert_plan/input/<original_zip_file>
rm -rf <repo_root>/upsert_plan/input/YYYYMMDD_descriptive_name/
# Also remove the image after processing (step 6)
```

### Step 6: Process the image

```bash
# Clear the image_converter input directory and copy the new image
rm -f <repo_root>/image_converter/input/*
cp <repo_root>/upsert_plan/input/<image_file> <repo_root>/image_converter/input/YYYYMMDD_descriptive_name.jpg

# Run the converter (ensure venv + pillow are available)
cd <repo_root>/image_converter
python3 -m venv .venv 2>/dev/null
source .venv/bin/activate
pip install pillow -q
python3 convert_images.py

# Move outputs to repo root
cp output/YYYYMMDD_descriptive_name-big.jpg <repo_root>/
cp output/YYYYMMDD_descriptive_name-thumbnail.jpg <repo_root>/

# Clean up the image from upsert_plan/input/
rm <repo_root>/upsert_plan/input/<image_file>
```

If the image is not a JPEG, the converter handles conversion automatically.

### Step 7: Add the YAML entry

Prepend a new entry to the top of `_data/examples.yml`. Use the Edit tool to insert before the first `- title:` line.

The prompt text goes under `prompt: |` with 4-space indentation. Preserve the original paragraph breaks. Make sure there's proper YAML escaping — the `|` block scalar handles most special characters, but double-check for trailing whitespace issues.

### Step 8: Verify locally

After all files are in place, suggest the user run `bundle exec jekyll serve` to preview. The new plan should appear as the first card in the examples gallery.

## Workflow: Replace/improve an existing plan

Ask the user for:
1. **Which plan to update** (by title or filename prefix)
2. Whether the **prompt has changed** (it often gets more detailed in regenerated plans)
3. Whether a **new image** is needed (usually not — the existing images stay)

Check `upsert_plan/input/` for the new zip file. If it's not there, ask the user to place it there (or provide a path).

Then execute:

### Step 1: Unzip and inject Google Analytics

Same as "add new plan" steps 2–3: unzip inside `upsert_plan/input/` and inject the GA snippet into `030-report.html` after the `</title>` tag.

### Step 2: Re-zip and replace files

Create the modified zip (with GA) and overwrite the existing zip in the repo root. Copy the modified `030-report.html` to overwrite the existing `_report.html` file.

### Step 3: Clean up

Delete the original zip and extracted directory from `upsert_plan/input/`. Keep the `.gitkeep`.

### Step 4: Update the prompt (if changed)

Extract `001-2-plan.txt` from the new zip. Compare with the existing prompt in `_data/examples.yml`. If different, update the YAML entry using the Edit tool. Show the user the diff before applying.

### Step 5: Update images (if provided)

If the user provides a new image, process it through `image_converter/` and replace the existing `-big.jpg` and `-thumbnail.jpg` files.

## Important conventions

- **Commit messages**: Use "Example plan added" for new plans, "improved plan" for updates. These are the established patterns in the repo history.
- **YAML ordering**: Newest plans go at the top of `examples.yml`.
- **Report HTML modification**: The only modification to `030-report.html` is injecting the Google Analytics snippet after `</title>`. Never make other content changes to report files.
- **Date prefix is stable**: When improving a plan, the `YYYYMMDD` prefix stays the same even if the report was regenerated months later. The date reflects when the plan was originally created.
- **Clean up temp files**: Remove all files from `upsert_plan/input/` (except `.gitkeep`) and `image_converter/input/` + `image_converter/output/` after processing.
- **description field**: Some entries have it, some don't. It's used for extra context like linking to the inspiration source. If the user doesn't specify one, omit it.
