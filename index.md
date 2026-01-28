---
layout: planexe_empty_page
title: Homepage of PlanExe
---

<header class="post-header planexe-index-header">
<h1 class="post-title">Homepage of PlanExe</h1>
<div class="header-description">
    <p class="subtitle">PlanExe is a tool for making plans.</p>
</div>
</header>

## What is it

- PlanExe is a planner, that can generate a detailed plan from your description.
- Open source, MIT license. You can modify the python code or the report template.
- Uses LlamaIndex so the AI provider can be changed, such as OpenRouter, Ollama, LM Studio.

## Why use it

- Save money. Don't fund doomed projects.
- Save time. It's time consuming to manually create a plan.
- Avoid surprises. Uncover pitfalls early.

## How to use it

<div class="planexe-split">
  <div class="planexe-split-panel">
    <h3>New users</h3>
    <p>Type in your idea and read the generated plan. The clearer your description, the better the plan.</p>
    <div class="planexe-cta-block">
      <a class="px-button px-button-primary" href="https://app.mach-ai.com/planexe_early_access">Try PlanExe</a>
      <div class="planexe-cta-helper">Create 1 plan for free. Additional plans are paid.</div>
    </div>
  </div>
  <div class="planexe-split-panel">
    <h3>Advanced users</h3>
    <p>Install and run PlanExe locally by following the GitHub instructions.</p>
    <p><a href="https://github.com/PlanExeOrg/PlanExe">github.com/PlanExeOrg/PlanExe</a></p>
  </div>
</div>

## Example plan

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

- Python developer, tweak most of the code.
- Prompt engineer, make changes to the system prompts for different responses.
- Project manager, for feedback about what is missing in the report. 
- Designer, make the report look nicer.
