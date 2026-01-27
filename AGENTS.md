# AGENTS.md — PlanExe-web

This repository powers the **`planexe.org`** website and is deployed via **GitHub Pages** as a **static Jekyll site**.

## What this repo is

- **Site type**: Jekyll (GitHub Pages), static output
- **Theme**: `remote_theme: jekyll/minima` (see `_config.yml`)
- **Custom styling hook**: `_includes/custom-head.html` injects `assets/css/planexe.css`
- **Content**: Mostly Markdown pages with front-matter + some inline HTML
- **Data-driven content**: `_data/examples.yml` feeds the homepage and `/examples/`

## What we are trying to achieve (design brief)

Create a **modern**, **developer-friendly**, **open-source** aesthetic for PlanExe.

- **Wanted vibe**: documentation/product-y (similar clarity to Docusaurus), but **not** “consulting-corporate” (avoid McKinsey-style sterile layouts).
- **Constraints**:
  - **Keep it static** (works on GitHub Pages).
  - **No React** (and ideally no build pipeline that requires Node).
  - Prefer **plain HTML/CSS**, minimal JS only for progressive enhancement.
  - Keep pages fast and readable.

## Hard “do not touch” rule

Do **not** modify or redesign the dated, generated HTML reports:

- **Ignore all files matching**: `^\d+_.*\.html$`
  - Example: `20260114_cbc_validation_report.html`
  - These will be reworked later.

It’s fine if site navigation links to these reports (via `_data/examples.yml`), but do not attempt to restyle, reformat, or “template-ize” them.

## Where changes should go (safe areas)

- **Primary CSS**: `assets/css/planexe.css`
  - This is currently the single site-wide custom stylesheet included in the `<head>`.
- **Head additions**: `_includes/custom-head.html`
  - Safe place to add additional CSS files, preload fonts, meta tags, etc.
- **Custom layouts (preferred)**: create new local layouts under `_layouts/`
  - Current local layout: `_layouts/planexe_empty_page.html`
  - Minima layouts are upstream; overriding requires adding local `_layouts/*.html` / `_includes/*.html` with the same names as Minima.
- **Generated output**: `_site/`
  - **Never edit** `_site/` directly (it’s build output).

## Content structure (important files)

- **Homepage**: `index.md` (uses `layout: planexe_empty_page`)
- **Examples listing**: `examples.md` (uses `layout: planexe_empty_page`, renders cards from `_data/examples.yml`)
- **Redirects**: `discord.md`, `github.md`, `use-cases.md` (uses `jekyll-redirect-from`)
- **Blog**: `blog.md` (uses Minima `layout: home`)

## Local dev

- Install:
  - `bundle install`
- Run:
  - `bundle exec jekyll serve`
- Build:
  - `bundle exec jekyll build`

## Redesign approach (how an agent should implement)

Prefer a **CSS-first** redesign, then override Minima templates only if needed.

1. **Define a design system** in CSS (tokens via `:root` variables):
   - colors (light/dark), typography, spacing, radii, shadows
   - code blocks and inline code styling
   - link, button, and callout styles
2. **Create a docs-like layout feel** without React:
   - clean top nav, consistent page width, good typographic scale
   - subtle background, modern borders/shadows, tasteful accent color
3. **Keep minimal JS** (only if it improves UX and degrades gracefully).
4. **Do not break** the report HTML pages; treat them as separate artifacts.

## Tone & UX guidelines

- Optimize for **readability first**: comfortable line length, clear headings, strong contrast.
- Use “modern” cues (spacing, rounded corners, subtle shadows) but keep it **open-source** and **tool-like**, not corporate.
- Avoid stock-photo aesthetics and “enterprise consulting” language.
- Ensure accessibility basics:
  - visible focus states (`:focus-visible`)
  - contrast-friendly colors
  - responsive layout (mobile-first)

