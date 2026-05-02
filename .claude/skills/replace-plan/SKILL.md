---
name: replace-plan
description: Replace or improve an existing example plan on the PlanExe-web Jekyll site (planexe.org) while preserving its name, images, title, and description. Use this skill whenever the user wants to replace, improve, or update an existing plan's zip and report. Trigger on mentions of "replace plan", "improve plan", "update plan", "plan needs updating", "replace the report", or any reference to updating an existing plan on the planexe.org examples gallery.
---

# Replacing an Existing Example Plan on PlanExe-web

Goal: under one minute, fully autonomous. The user drops a zip in `upsert_plan/input/` and names the existing plan to replace. You do everything: extract, inject GA, preserve old title + description, update the prompt from the new zip, copy files, upsert YAML, commit & push, clean up. **No preview step. No questions.**

## Invariants

- **Title and description**: always preserved from the existing `_data/examples.yml` entry.
- **Prompt**: replaced with whatever is in the new zip (`process_plan.py` extracts it).
- **Plan name**: preserved (e.g. `20260201_media_rescue`) so URLs keep working.
- **Images** (`-big.jpg`, `-thumbnail.jpg`): preserved.
- **Branch**: must be `main`. If in a worktree, ask the user to disable the worktree setting and start a new session.

## Files

Each plan lives at the repo root: `EXISTING_NAME.zip`, `EXISTING_NAME_report.html`, `EXISTING_NAME-big.jpg`, `EXISTING_NAME-thumbnail.jpg`. The gallery entry is in `_data/examples.yml`.

## Workflow

### Step 1: Identify the existing entry

User tells you the plan name (e.g. "replace 20260201_media_rescue"). Read its current entry in `_data/examples.yml`. Capture the **exact** `title:` line and the full `description:` block (or note that there is no description).

### Step 2: Process the new zip

```bash
cd <repo_root>/upsert_plan
.venv/bin/python3 process_plan.py --name EXISTING_NAME --skip-images
```

Produces in `output/`:
- `EXISTING_NAME.zip` — GA-injected
- `EXISTING_NAME_report.html` — GA-injected
- `example_item.yml` — has new title (from report), `PLACEHOLDER_DESCRIPTION`, new prompt (from zip), `report_link`, `thumbnail`

If the venv is broken: `rm -rf .venv && python3 -m venv .venv && .venv/bin/pip install pillow`.

### Step 3: Patch example_item.yml — restore old title + old description

Use the `Edit` tool on `upsert_plan/output/example_item.yml`:
1. Replace the new `- title: …` line with the old title line copied verbatim from `_data/examples.yml`.
2. Replace the placeholder description block with the old description block copied verbatim from `_data/examples.yml`. If the old entry had no `description:` field, delete the entire `description: |` block (the `description:` line plus the indented block underneath it) from `example_item.yml`.

Leave `prompt:`, `report_link:`, `thumbnail:` as generated.

### Step 4: Copy files into the repo root, upsert YAML

```bash
cd <repo_root>
cp upsert_plan/output/EXISTING_NAME.zip .
cp upsert_plan/output/EXISTING_NAME_report.html .
cd upsert_plan
python3 upsert_examples_yml.py
```

`upsert_examples_yml.py` matches by `report_link` and replaces the entry in place.

### Step 5: Commit & push

```bash
cd <repo_root>
git add EXISTING_NAME.zip EXISTING_NAME_report.html _data/examples.yml
git commit -m "improved plan EXISTING_NAME"
git push
```

If `process_plan.py` or other scripts in the repo also changed, make a separate descriptive commit for those first.

### Step 6: Clean up

```bash
cd <repo_root>/upsert_plan
python3 clean.py
```

## Conventions

- **Commit message**: always `improved plan EXISTING_NAME`.
- **No preview**: do not run `start_jekyll.py`.
- **No questions**: do not ask about title or description — always preserve.
