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
    <a class="px-button px-button-primary px-button-hero" href="https://app.mach-ai.com/planexe_early_access">Create your first plan free &nbsp;&rarr;</a>
</div>
</header>

## How it works

<div class="px-steps-grid">
  <div class="px-step-card">
    <div class="px-step-number">1</div>
    <h3>Describe your idea</h3>
    <p>Input a description of your project, from a startup pitch to a complex infrastructure project.</p>
  </div>
  <div class="px-step-card">
    <div class="px-step-number">2</div>
    <h3>AI pipeline runs</h3>
    <p>PlanExe orchestrates 100+ LLM calls across legal, financial, and engineering experts — cross-referencing, challenging, and stress-testing your plan.</p>
  </div>
  <div class="px-step-card">
    <div class="px-step-number">3</div>
    <h3>Read your generated plan</h3>
    <p>Get a comprehensive report you can refine for investors, leadership, or internal planning.</p>
  </div>
</div>

## Who is PlanExe for?

<div class="px-persona-grid">
  <div class="px-persona-card">
    <h3>Founders & Startups</h3>
    <p>Stress-test business models and surface risks before they become expensive. Find out early if your idea is doomed.</p>
  </div>
  <div class="px-persona-card">
    <h3>Enterprise PMOs</h3>
    <p>Standardize project initiation with 20+ section reports covering budgets, legal, and risk matrices. Export csv and gantt for import into your existing tools.</p>
  </div>
  <div class="px-persona-card">
    <h3>Developers & AI Agents</h3>
    <p>Orchestrate long-running planning tasks via MCP. Claude, Codex, Cursor and Windsurf can connect to PlanExe.</p>
  </div>
</div>

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

## Your plans stay yours

Unlike cloud-based alternatives, PlanExe can run fully offline on your own hardware. That means you can work on sensitive plans without sending them to external services.

## Get started

<div class="px-paths-grid">
  <div class="planexe-split-panel">
    <div class="px-difficulty-badge px-difficulty-beginner">Beginner</div>
    <h3>PlanExe Cloud</h3>
    <p>Recommended way to try PlanExe. No setup. Type in your idea and read the generated plan.</p>
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
