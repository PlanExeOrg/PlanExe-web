---
name: jekyll
description: Start, stop, and manage the local Jekyll development server for PlanExe-web. Use this skill when doing web development on the site — editing CSS, layouts, index.md, examples, or any site content that needs a local preview.
---

# Jekyll Development Server

## Prerequisites

Ruby 3.3 is required. The PATH must include the Ruby 3.3 bin directory.

## Starting the server

Run Jekyll in a **background Bash process** so it stays alive for the duration of the session:

```bash
PATH="/opt/homebrew/opt/ruby@3.3/bin:$PATH" LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 bundle exec jekyll serve --port 4000
```

Use `run_in_background: true` with the Bash tool. This keeps the server running while you continue working.

After starting, wait a few seconds then verify it's up:

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:4000/
```

The user browses to http://localhost:4000/ to preview.

## Hot reload

Jekyll has **auto-regeneration** enabled by default. When you edit files (index.md, CSS, _data/examples.yml, layouts, etc.), Jekyll detects the change and rebuilds `_site/` automatically. The user just refreshes their browser — **do NOT restart the server after editing files**.

## Stopping the server

Only stop the server when the user explicitly asks, or when the session is ending. Kill it with:

```bash
pkill -f "jekyll serve"
```

## Important rules

1. **Never use `upsert_plan/start_jekyll.py` or `upsert_plan/stop_jekyll.py`** for web development. Those scripts are for plan management workflows only.
2. **Never restart the server after file edits.** Auto-regeneration handles it. Only restart if the server has actually crashed.
3. **Never kill Jekyll just because you're done previewing.** The user manages their own browser tabs and will stop the server themselves with Ctrl-C when done.
4. If port 4000 is occupied, use `--port 4001`.
