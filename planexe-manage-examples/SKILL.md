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
- `output/` — Where all processed files are written
- `process_plan.py` — **Main processing script**. Orchestrates everything.
- `preview_plan.py` — **Local preview script**. Temporarily stages output into the repo, starts Jekyll, opens the browser, and reverts on exit.
- `upsert_examples_yml.py` — **YAML upsert script**. Updates or prepends `output/example_item.yml` into `_data/examples.yml`. Matches by `report_link` plan name — updates in place if the plan exists, prepends if new.
- `convert_images.py` — Image conversion script (requires Pillow). Called automatically by `process_plan.py`.
- `rename_title.py` — **Title rename script**. Updates the title of an existing plan in `_data/examples.yml`. Takes a plan name (or zip filename) and the new title as arguments.

### Using process_plan.py

**Prerequisites:** Place both a PlanExe `.zip` and an image file (`.jpg`, `.jpeg`, `.png`, `.webp`) in `upsert_plan/input/`. The script will refuse to run if either is missing.

**Requires:** Python 3.9+ with Pillow installed (for image conversion). Use the venv python directly (do NOT use `source .venv/bin/activate` — shell state does not persist between Bash calls in Claude Code):
```bash
cd <repo_root>/upsert_plan
.venv/bin/python3 process_plan.py
```

If the venv is broken or Pillow is missing, recreate it:
```bash
cd <repo_root>/upsert_plan
rm -rf .venv && python3 -m venv .venv && .venv/bin/pip install pillow
```

**What it does (in order):**
1. Validates that `input/` contains exactly one `.zip` and at least one image file
2. Extracts the prompt from `001-2-plan.txt` (strips `Plan:` prefix and `Today's date:` suffix)
3. Injects Google Analytics into `030-report.html` after `</title>` (replaces existing GA if present)
4. Extracts the title from the `<title>` tag
5. Derives the canonical name `YYYYMMDD_descriptive_name` from `001-1-start_time.json` (date) and the title (slug)
6. Creates a modified zip in `output/` named `YYYYMMDD_name.zip` with a matching wrapper directory
7. Copies the GA-injected report to `output/YYYYMMDD_name_report.html`
8. Invokes `convert_images.py` to produce `output/YYYYMMDD_name-big.jpg` and `output/YYYYMMDD_name-thumbnail.jpg`
9. Generates `output/example_item.yml` — a YAML snippet ready to prepend to `_data/examples.yml` (with `PLACEHOLDER_DESCRIPTION` for the user to fill in or remove)

**Output files in `output/`:**
```
YYYYMMDD_name.zip                  # Modified zip with GA injected
YYYYMMDD_name_report.html          # GA-injected report
YYYYMMDD_name-big.jpg              # Hero image (max 1024px, ≤300KB)
YYYYMMDD_name-thumbnail.jpg        # Gallery thumbnail (256px wide)
example_item.yml                   # YAML snippet for examples.yml
```

**Stdout output** (parseable — status goes to stderr):
```
TITLE: EuroLens Platform
PLAN_NAME: 20260318_eurolens_platform
```

**Important:** The script never modifies or deletes files in `input/`. If something goes wrong, the original files are still there for re-running.

### Using preview_plan.py

After running `process_plan.py`, preview the result locally before committing:

```bash
cd <repo_root>/upsert_plan
python3 preview_plan.py
```

**What it does:**
1. Copies output files (zip, report, images) into the repo root temporarily
2. Prepends `example_item.yml` into `_data/examples.yml`
3. Starts `bundle exec jekyll serve` (using Ruby 3.3 via Homebrew)
4. Opens `http://localhost:4000/examples/` in the browser
5. **On Ctrl-C** — reverts everything: removes copied files and restores `examples.yml`

**Note:** Requires Ruby 3.3 installed via Homebrew (`brew install ruby@3.3`) and `bundle install` completed in the repo root. The script sets the Ruby 3.3 PATH automatically.

Check `upsert_plan/input/` first when the user says they have a new plan.

## Important: Branch requirement

The user places input files on the **main** branch. `process_plan.py` will refuse to run if the current branch is not `main`. If you're in a worktree, **ask the user to disable the worktree setting** and start a new session — you cannot switch to `main` from inside a worktree.

## Workflow: Add a new plan

Check `upsert_plan/input/` for the zip and image files. If they're not there, ask the user to place them there.

### Step 1: Run process_plan.py

```bash
cd <repo_root>/upsert_plan
.venv/bin/python3 process_plan.py
```

This produces all files in `output/`: the modified zip, report HTML, both image variants, and `example_item.yml`.

### Step 2: Ask for a description

The script generates `output/example_item.yml` with `PLACEHOLDER_DESCRIPTION`. Present the user with description options (suggest 3 based on the plan content, plus "No description" to omit the field). Edit **only** `output/example_item.yml` to replace the placeholder — never touch `_data/examples.yml` directly at this stage.

### Step 3: Preview locally

Run `preview_plan.py` to preview. Since it starts a long-running Jekyll server, run it **in the background** (`run_in_background: true`):

```bash
cd <repo_root>/upsert_plan
.venv/bin/python3 preview_plan.py
```

If port 4000 is already in use, kill the existing process first:
```bash
lsof -ti:4000 | xargs kill 2>/dev/null
```

This temporarily stages output files into the repo and opens the examples page. It always prepends from a clean `_data/examples.yml` (backed up and restored on exit). The new plan should appear as the first card.

Wait a few seconds for the server to start, then verify it's running:
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:4000/examples/
```

### Step 4: User decides

The preview server (Jekyll) live-reloads when files change, so there is no need to restart it between edits.

Present the user with 4 choices:
1. **Change title** — run `rename_title.py` to update `_data/examples.yml` directly. Jekyll will live-reload the page. Loop back to this step.
   ```bash
   cd <repo_root>/upsert_plan
   python3 rename_title.py YYYYMMDD_name.zip "New Title Here"
   ```
2. **Change description** — edit the `description` field directly in `_data/examples.yml`. Jekyll will live-reload the page. Loop back to this step.
3. **Commit & push** — stop the background preview task, then proceed to step 5.
4. **Abort** — stop the background preview task, discard all changes, clean `output/`, done.

### Step 5: Commit & push

Move output files to the repo root and upsert the YAML entry:

```bash
cd <repo_root>/upsert_plan

# Move output files to repo root
mv output/YYYYMMDD_name.zip ../
mv output/YYYYMMDD_name_report.html ../
mv output/YYYYMMDD_name-big.jpg ../
mv output/YYYYMMDD_name-thumbnail.jpg ../

# Upsert the YAML entry (prepends if new, updates in place if existing)
python3 upsert_examples_yml.py
```

Then commit with the plan name as the message (e.g. `"20260318_eurolens_platform"`) and push.

### Step 6: Clean up

Remove processed files from `output/`. Input files stay untouched.

```bash
rm -f <repo_root>/upsert_plan/output/*
```

## Workflow: Replace/improve an existing plan

Ask the user for:
1. **Which plan to update** (by title or filename prefix)
2. Whether a **new image** is needed (usually not — the existing images stay)

Place the new zip (and image if needed) in `upsert_plan/input/`.

Follow the same steps as "Add a new plan" — the workflow is identical. `upsert_examples_yml.py` automatically detects whether the plan already exists and updates it in place instead of prepending a duplicate.

## Important conventions

- **Commit messages**: Use "Example plan added" for new plans, "improved plan" for updates. These are the established patterns in the repo history.
- **YAML ordering**: Newest plans go at the top of `examples.yml`.
- **Report HTML modification**: The only modification to `030-report.html` is injecting the Google Analytics snippet after `</title>`. Never make other content changes to report files.
- **Date prefix is stable**: When improving a plan, the `YYYYMMDD` prefix stays the same even if the report was regenerated months later. The date reflects when the plan was originally created.
- **Clean up temp files**: Remove all files from `upsert_plan/input/` and `upsert_plan/output/` (except `.gitkeep` in each) after processing.
- **description field**: Some entries have it, some don't. It's used for extra context like linking to the inspiration source. If the user doesn't specify one, omit it.
