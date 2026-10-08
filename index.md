---
layout: planexe_empty_page
title: PlanExe - Agentic Planning Engine
---

<header class="post-header planexe-index-header">
<h1 class="post-title">PlanExe: Turn your idea into a detailed plan</h1>
<div class="header-description">
    <p class="subtitle">Executive summary, gantt, risks, swot, budget, premortem, and more.</p>
</div>
<div class="planexe-hero-cta">
    <a class="px-button px-button-primary px-button-hero" href="{{ '/get-started/' | relative_url }}">Get started &nbsp;&rarr;</a>
</div>
</header>

## How it works

<div class="px-steps-grid">
  <div class="px-step-card">
    <div class="px-step-number">1</div>
    <h3>Describe your idea</h3>
    <p>Enter a description of your project, from a startup pitch to a complex infrastructure project.</p>
  </div>
  <div class="px-step-card">
    <div class="px-step-number">2</div>
    <h3>AI pipeline runs</h3>
    <p>PlanExe orchestrates 100+ LLM calls across legal, financial, and engineering review stages — cross-referencing, challenging, and stress-testing your plan.</p>
  </div>
  <div class="px-step-card">
    <div class="px-step-number">3</div>
    <h3>Read your generated plan</h3>
    <p>Get a comprehensive report you can refine for investors, leadership, or internal planning.</p>
  </div>
</div>

## Who is PlanExe for?

- **Founders** — Stress-test ideas early and avoid expensive mistakes.
- **Project Managers** — Standardize project kickoffs with structured, exportable plans.
- **Developers** — Run PlanExe from Claude Code or Codex. Every stage is a plain folder of prompts and Python you can read and change.

## AI that pushes back

Most AI tools just agree with you. PlanExe red-teams your plan to find flaws before you commit serious time or money.

<div class="px-feature-grid">
  <div class="px-feature-card">
    <h3>Premise Attack</h3>
    <p>Deliberately argues that it's a bad idea. It doesn't matter how good your plan is — it will always argue against it.</p>
  </div>
  <div class="px-feature-card">
    <h3>Premortem Analysis</h3>
    <p>Imagines your project has already failed and works backwards to find out why.</p>
  </div>
  <div class="px-feature-card">
    <h3>Self-Audit</h3>
    <p>Cross-references experts across legal, financial, and engineering domains. Catches inconsistencies and contradictions.</p>
  </div>
</div>

## Your plans live on your machine

PlanExe runs on your own computer. Every plan is a folder of plain files that you own: you can read them, edit them and re-run, and PlanExe regenerates whatever depends on your changes.

## Get started

PlanExe runs on your computer and uses your Claude subscription through Claude Code. Clone the repo, start Claude Code, and ask for a plan:

```bash
git clone https://github.com/PlanExeOrg/PlanExe2.git
cd PlanExe2
claude
```

Then type something like *"make a plan for a bakery in Lyon"*. PlanExe asks a few questions, shows you the project description it will use, and starts once you confirm. One to two hours later, you have a full report.

<div class="planexe-cta-block">
  <a class="px-button px-button-primary" href="{{ '/get-started/' | relative_url }}">Read the getting started guide</a>
</div>

## Example plans

<div class="examples-card-wrapper">
{% for item in site.data.examples %}
{% if item.featured %}
<div class="examples-card">
{% if item.thumbnail %}
<div class="examples-card-image-wrapper">
<img src="{{ item.thumbnail }}" alt="{{ item.title }}" class="examples-card-thumbnail">
</div>
{% endif %}
<div class="examples-card-content">
<h2 class="examples-card-title">{{ item.title }}</h2>
{% if item.description %}
<div class="examples-card-description">
{{ item.description | markdownify }}
</div>
{% endif %}
<div class="examples-card-prompt">{{ item.prompt | markdownify }}</div>
</div>
<a class="examples-card-arrow-link" href="{{ item.report_link }}"></a>
</div>
{% endif %}
{% endfor %}
</div>
