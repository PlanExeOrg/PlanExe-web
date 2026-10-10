---
name: replace-plan
description: Replace or improve an existing example plan on the PlanExe-web Jekyll site (planexe.org) while preserving its name, images, title, and description. Use this skill whenever the user wants to replace, improve, or update an existing plan's zip and report. Trigger on mentions of "replace plan", "improve plan", "update plan", "plan needs updating", "replace the report", or any reference to updating an existing plan on the planexe.org examples gallery.
---

# Replacing an Existing Example Plan on PlanExe-web

This skill handles replacing an existing plan's zip and report on the PlanExe-web Jekyll site (planexe.org), while preserving the plan's canonical name (so existing links keep working) and its images (thumbnail and hero).

## Invariants

- **Title and description**: always preserved from the existing `_data/examples.yml` entry.
- **Prompt**: replaced with whatever is in the new zip (`process_plan.py` extracts it).
- **Plan name**: preserved (e.g. `20260201_media_rescue`) so URLs keep working.
- **Images** (`-big.jpg`, `-thumbnail.jpg`): preserved.
- **Curation flags** (`featured: true`, and any other field `process_plan.py` does not generate): preserved from the old entry. `upsert_examples_yml.py` replaces the whole entry, so any such field missing from `example_item.yml` is silently dropped (dropping `featured: true` removes the plan from the homepage).
- **PlanExe version** (`planexe_version`): taken from the **new** zip, never from the old entry. `process_plan.py` detects it (`generator.name: PlanExe2` in `planexe_metadata.json` → `planexe_version: 2`; otherwise the field is omitted = version 1). Replacing a v1 plan with a PlanExe 2 run therefore upgrades the card from `v1 · legacy` to `v2 · current`.
- **Branch**: all commits land on `main` in the main worktree. Even if invoked from a feature worktree, run every command against the main worktree path — do not switch branches in the current worktree, do not ask the user to start a new session.

## Files

Each plan lives at the repo root: `EXISTING_NAME.zip`, `EXISTING_NAME_report.html`, `EXISTING_NAME-big.jpg`, `EXISTING_NAME-thumbnail.jpg`. The gallery entry is in `_data/examples.yml`.

## Workflow

### Step 0: Locate the main worktree and verify it is clean on `main`

```bash
MAIN_REPO=$(git worktree list | awk 'NR==1 {print $1}')
git -C "$MAIN_REPO" rev-parse --abbrev-ref HEAD   # must print: main
git -C "$MAIN_REPO" status --short                # must be empty
```

Use `$MAIN_REPO` (not the current cwd) wherever the steps below say `<repo_root>`. If `HEAD` is not `main` or the working tree is dirty, stop and ask the user — do not try to fix it automatically.

### Step 1: Identify the existing entry

User tells you the plan name (e.g. "replace 20260201_media_rescue"), or just the new zip's filename (e.g. "replace with 20261008_the_consortium.zip") — in that case the zip's basename is the existing plan name. Read its current entry in `$MAIN_REPO/_data/examples.yml`. Capture the **exact** `title:` line, the full `description:` block (or note that there is no description), and every field after `planexe_version:`/`thumbnail:` that `process_plan.py` does not generate — most commonly `featured: true`.

### Step 2: Process the new zip

```bash
cd "$MAIN_REPO/upsert_plan"
.venv/bin/python3 process_plan.py --name EXISTING_NAME --skip-images
```

Produces in `output/`:
- `EXISTING_NAME.zip` — GA-injected
- `EXISTING_NAME_report.html` — GA-injected
- `example_item.yml` — has new title (from report), `PLACEHOLDER_DESCRIPTION`, new prompt (from zip), `report_link`, `thumbnail`, and `planexe_version: 2` if the new zip is from PlanExe 2

Read the `PLANEXE_VERSION:` line on stdout and compare it with the old entry (old entry has `planexe_version: 2` → v2, no field → v1). Tell the user the outcome, e.g. "v1 → v2 (upgrade)" or "v1 → v1". If it is a **downgrade** (old entry v2, new zip v1), stop and ask the user before continuing — that is probably the wrong zip.

If the venv is broken: `rm -rf .venv && python3 -m venv .venv && .venv/bin/pip install pillow`.

### Step 3: Patch example_item.yml — restore old title, description, and curation flags

Use the `Edit` tool on `$MAIN_REPO/upsert_plan/output/example_item.yml`:
1. Replace the new `- title: …` line with the old title line copied verbatim from `_data/examples.yml`.
2. Replace the placeholder description block with the old description block copied verbatim from `_data/examples.yml`. If the old entry had no `description:` field, delete the entire `description: |` block (the `description:` line plus the indented block underneath it) from `example_item.yml`.
3. Append any curation fields captured in Step 1 (e.g. `  featured: true`) at the end of the entry, in the same order as the old entry.

Leave `prompt:`, `report_link:`, `thumbnail:`, and `planexe_version:` (if present) as generated.

### Step 4: Copy files into the repo root, upsert YAML

```bash
cd "$MAIN_REPO"
cp upsert_plan/output/EXISTING_NAME.zip .
cp upsert_plan/output/EXISTING_NAME_report.html .
cd upsert_plan
python3 upsert_examples_yml.py
```

`upsert_examples_yml.py` matches by `report_link` and replaces the entry in place.

### Step 5: Commit & push

```bash
git -C "$MAIN_REPO" add EXISTING_NAME.zip EXISTING_NAME_report.html _data/examples.yml
git -C "$MAIN_REPO" commit -m "improved plan EXISTING_NAME"
git -C "$MAIN_REPO" push
```

If the prompt in the new zip is unchanged, `_data/examples.yml` will have no diff — that's expected; the commit then contains only the zip and report. Before committing, confirm `git diff _data/examples.yml` shows no unintended removals (title, description, `featured`).

If `process_plan.py` or other scripts in the repo also changed, make a separate descriptive commit for those first.

### Step 6: Clean up

```bash
cd "$MAIN_REPO/upsert_plan"
python3 clean.py
```

## Conventions

- **Commit message**: always `improved plan EXISTING_NAME`.
- **No preview**: do not run `start_jekyll.py`.
- **No questions**: do not ask about title or description — always preserve.
