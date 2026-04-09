---
name: replace-plan
description: Replace or improve an existing example plan on the PlanExe-web Jekyll site (planexe.org) while preserving its name and images. Use this skill whenever the user wants to replace, improve, or update an existing plan's zip and report. Trigger on mentions of "replace plan", "improve plan", "update plan", "plan needs updating", "replace the report", or any reference to updating an existing plan on the planexe.org examples gallery — even if the user just says something like "this plan needs updating" or "I have a better version of this plan".
---

# Replacing an Existing Example Plan on PlanExe-web

This skill handles replacing an existing plan's zip and report on the PlanExe-web Jekyll site (planexe.org), while preserving the plan's canonical name (so existing links keep working) and its images (thumbnail and hero).

## What you need to know

### File structure per plan

Each plan consists of these files in the repo root:

```
YYYYMMDD_descriptive_name.zip              # Modified PlanExe output (with GA injected)
YYYYMMDD_descriptive_name_report.html      # The HTML report (extracted from zip, with GA)
YYYYMMDD_descriptive_name-big.jpg          # Hero image (max 1024px, ≤300KB)
YYYYMMDD_descriptive_name-thumbnail.jpg    # Gallery thumbnail (256px wide)
```

When replacing a plan, typically only the `.zip` and `_report.html` change. The images stay the same.

### The examples gallery

All plans are listed in `_data/examples.yml`. Each entry has:
- **title** (required): Short display name for the card
- **description** (optional): Brief context, can include markdown links.
- **prompt** (required): The original prompt fed to PlanExe.
- **report_link** (required): Filename of the HTML report in the repo root
- **thumbnail** (required): Filename of the thumbnail image in the repo root

### Inside the zip file

Key files inside the PlanExe zip:
- `plan.txt` — The original prompt. Starts with `Plan:\n` and ends with `\nToday's date:\n...`.
- `start_time.json` — Contains `server_iso_utc` with the plan generation timestamp.
- `report.html` — The rendered HTML report. Its `<title>` tag contains the plan title.

## The upsert_plan/ directory

Key scripts:
- `process_plan.py` — Main processing script. Supports `--name` to override the canonical name and `--skip-images` to skip image processing.
- `preview_plan.py` — Local preview. Supports `--skip-images` to skip checking for image files in output.
- `upsert_examples_yml.py` — YAML upsert. Updates existing entries in place (matches by `report_link`).
- `edit_plan.py` — Metadata editor for title/description/prompt in `_data/examples.yml`.
- `clean.py` — Removes all files from `input/` and `output/` except `.gitkeep`.

**Python venv:** `process_plan.py` requires Pillow via the venv. Use `.venv/bin/python3` directly:
```bash
cd <repo_root>/upsert_plan
.venv/bin/python3 process_plan.py [args]
```

If the venv is broken:
```bash
cd <repo_root>/upsert_plan
rm -rf .venv && python3 -m venv .venv && .venv/bin/pip install pillow
```

## Important: Branch requirement

The user places input files on the **main** branch. `process_plan.py` will refuse to run if the current branch is not `main`. If you're in a worktree, **ask the user to disable the worktree setting** and start a new session.

## Workflow: Replace an existing plan

### Step 0: Identify the plan

Ask the user which plan to replace (by title or filename prefix like `20250627_delhi_water`). Look up its current entry in `_data/examples.yml` to confirm it exists and note the current title, description, and prompt.

The user places only the **new zip** in `upsert_plan/input/`. No image is needed since existing images are preserved.

### Step 1: Run process_plan.py with --name and --skip-images

```bash
cd <repo_root>/upsert_plan
.venv/bin/python3 process_plan.py --name EXISTING_NAME --skip-images
```

For example:
```bash
.venv/bin/python3 process_plan.py --name 20250627_delhi_water --skip-images
```

- `--name EXISTING_NAME` overrides the canonical name so it matches the existing plan (preserving links).
- `--skip-images` skips image processing and does not require an image file in `input/`.

This produces in `output/`:
```
EXISTING_NAME.zip                  # Modified zip with GA injected
EXISTING_NAME_report.html          # GA-injected report
example_item.yml                   # YAML snippet
```

### Step 2: Decide on title and description

Compare the new report's `<title>` with the old entry's title. Ask the user:
1. **Keep old title** (default — preserves gallery appearance)
2. **Use new title** (from the new report's `<title>` tag)
3. **Custom title**

Also ask about description (the old entry may or may not have one).

Edit `output/example_item.yml` to reflect the chosen title and description. Remove the `description:` field entirely if not wanted.

### Step 3: Preview locally

For replacement previews, use a manual approach since `preview_plan.py` prepends entries (which creates duplicates for existing plans):

```bash
cd <repo_root>

# Backup examples.yml
cp _data/examples.yml _data/examples.yml.bak

# Copy zip and report to repo root (overwrites existing files)
cp upsert_plan/output/EXISTING_NAME.zip .
cp upsert_plan/output/EXISTING_NAME_report.html .

# Update the YAML entry in place
cd upsert_plan
python3 upsert_examples_yml.py

# Start Jekyll and open browser (kills any existing Jekyll first)
cd <repo_root>/upsert_plan
python3 start_jekyll.py --plan EXISTING_NAME
```

Run this command **in the background** (`run_in_background: true`). The script waits for Jekyll to be ready, then opens both the examples gallery and the plan's report page.

**IMPORTANT:** Do NOT kill the Jekyll server after the user is done reviewing. Killing the process closes their browser tabs. Leave it running — the user will close tabs and stop the server themselves. If the user explicitly asks to stop Jekyll, use `python3 stop_jekyll.py` (never `lsof` port-based killing, which also kills the browser).

### Step 4: User decides

Present the user with choices:
1. **Change title** — use `edit_plan.py`, then also update `output/example_item.yml`. Jekyll live-reloads. Loop back.
   ```bash
   cd <repo_root>/upsert_plan
   python3 edit_plan.py EXISTING_NAME --title "New Title"
   ```
2. **Change description** — same approach with `--description`. Loop back.
3. **Commit & push** — proceed to step 5.
4. **Abort** — follow abort procedure below.

**Abort procedure:**
```bash
cd <repo_root>
cp _data/examples.yml.bak _data/examples.yml
rm -f _data/examples.yml.bak
git checkout -- EXISTING_NAME.zip EXISTING_NAME_report.html
cd upsert_plan
python3 clean.py
git status
```

### Step 5: Commit & push

Since the files are already in the repo root (copied during preview), just commit:

```bash
cd <repo_root>
rm -f _data/examples.yml.bak
```

If no preview was done, copy files first:
```bash
cp upsert_plan/output/EXISTING_NAME.zip .
cp upsert_plan/output/EXISTING_NAME_report.html .
cd upsert_plan
python3 upsert_examples_yml.py
```

Commit with two separate commits if script changes are also present:
1. Script changes: descriptive message
2. Plan replacement: `"improved plan EXISTING_NAME"`

Push to remote.

### Step 6: Clean up

```bash
cd <repo_root>/upsert_plan
python3 clean.py
```

## Important conventions

- **Commit messages**: Use `"improved plan EXISTING_NAME"` for replacements (e.g. `"improved plan 20250627_delhi_water"`).
- **Name is preserved**: The `YYYYMMDD_descriptive_name` prefix stays the same — this is critical so existing URLs keep working.
- **Images are preserved**: Unless the user explicitly wants new images, the existing `-big.jpg` and `-thumbnail.jpg` stay.
- **Clean up temp files**: Run `clean.py` after processing.
