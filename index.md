---
layout: planexe_empty_page
title: PlanExe - Agentic Planning Engine
---

<header class="post-header planexe-index-header">
<h1 class="post-title">PlanExe: convert idea to plan</h1>
<div class="header-description">
    <p class="subtitle">Executive summary, Gantt chart, risks, SWOT, budget, premortem, and more — in 15 minutes.</p>
</div>
</header>

## How it works

<div class="px-steps-grid">
  <div class="px-step-card">
    <div class="px-step-number">1</div>
    <h3>Describe your idea</h3>
    <p>Type a plain-English description of your project — from a startup pitch to a billion-dollar infrastructure initiative.</p>
  </div>
  <div class="px-step-card">
    <div class="px-step-number">2</div>
    <h3>AI pipeline runs</h3>
    <p>PlanExe orchestrates 100+ LLM calls across legal, financial, and engineering experts — cross-referencing, challenging, and stress-testing your plan.</p>
  </div>
  <div class="px-step-card">
    <div class="px-step-number">3</div>
    <h3>Read your battle-tested plan</h3>
    <p>Get a comprehensive report you can hand to investors, present to leadership, or use to kick off your project.</p>
  </div>
</div>

## AI that pushes back

Most AI tools just agree with you. PlanExe red-teams your plan to find fatal flaws before you spend a dime.

<div class="px-feature-grid">
  <div class="px-feature-card">
    <h3>Premise Attack</h3>
    <p>Challenges your core assumptions. If your idea has a hidden weakness, PlanExe will surface it before investors or reality does.</p>
  </div>
  <div class="px-feature-card">
    <h3>Premortem Analysis</h3>
    <p>Imagines your project has already failed and works backwards to find out why. Identifies risks like "The Austerity Asteroid" before they strike.</p>
  </div>
  <div class="px-feature-card">
    <h3>Self-Audit</h3>
    <p>Cross-references experts across legal, financial, and engineering domains. Catches inconsistencies a single consultant would miss.</p>
  </div>
</div>

## Who is PlanExe for?

<div class="px-persona-grid">
  <div class="px-persona-card">
    <h3>Founders & Startups</h3>
    <p>Stress-test business models and generate investor-grade risk assessments. Know if your idea is viable before burning runway.</p>
  </div>
  <div class="px-persona-card">
    <h3>Enterprise PMOs</h3>
    <p>Standardize project initiation with 20+ section reports covering budgets, legal, and risk matrices. Export CSV and Gantt data for import into your existing tools.</p>
  </div>
  <div class="px-persona-card">
    <h3>Developers & AI Agents</h3>
    <p>Orchestrate long-running planning tasks via MCP. Claude, Codex, Cursor and Windsurf can connect to PlanExe.</p>
  </div>
</div>

## Get started

<div class="px-paths-grid">
  <div class="planexe-split-panel">
    <div class="px-difficulty-badge px-difficulty-beginner">Beginner</div>
    <h3>PlanExe Cloud</h3>
    <p>Managed, fast, zero-setup. Type in your idea and read the generated plan.</p>
    <div class="planexe-cta-block">
      <a class="px-button px-button-primary" href="https://app.mach-ai.com/planexe_early_access">Try PlanExe</a>
      <div class="planexe-cta-helper">Create 1 plan for free. Additional plans are paid.</div>
    </div>
  </div>
  <div class="planexe-split-panel">
    <div class="px-difficulty-badge px-difficulty-medium">Medium</div>
    <h3>PlanExe Account</h3>
    <p>Get your API keys to connect PlanExe's MCP server to Claude, Codex, Cursor, or Windsurf. Manage credits and view your generated plans.</p>
    <div class="planexe-cta-block">
      <a class="px-button px-button-primary" href="https://home.planexe.org/">Manage Account</a>
    </div>
  </div>
  <div class="planexe-split-panel">
    <div class="px-difficulty-badge px-difficulty-expert">Expert</div>
    <h3>PlanExe Local</h3>
    <p>100% private. Install and run PlanExe locally on your own hardware. Open source, MIT license.</p>
    <p><a href="https://github.com/PlanExeOrg/PlanExe">github.com/PlanExeOrg/PlanExe</a></p>
  </div>
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

## Get involved

Introduce yourself on the [PlanExe Discord]({{ '/discord/' | relative_url }}) and ask how you can help.

- **Python Developer:** Tweak the core engine, DAG pipelines, and agent prompts.
- **Prompt Engineer:** Refine the system prompts for better expert responses and red-teaming.
- **Project Manager:** Provide feedback on missing project methodologies or export formats.
- **Designer:** Enhance the HTML report UI and interactive data visualizations.
