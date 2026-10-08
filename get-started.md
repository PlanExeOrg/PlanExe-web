---
layout: planexe_empty_page
title: Get started
permalink: /get-started/
---

<header class="post-header planexe-usecases-header">
<h1 class="post-title">Get started with PlanExe</h1>
<div class="header-description">
    <p class="subtitle">Go from an idea to a detailed plan in one to two hours, on your own computer.</p>
</div>
</header>

## What PlanExe does

You describe a project in a few paragraphs: what you want to do, where, on what budget and by when. PlanExe takes that description and works through it the way a planning workshop would. It makes about 250 LLM calls that draft the plan, argue against it, check the numbers and look for contradictions.

The result is a single `report.html` that you open in your browser. It starts with the decisions you still have to make and the key facts the plan relies on, followed by a Gantt chart, risks, SWOT, a premortem, a work breakdown and more. Treat it as a strong first draft: it shows you the questions to answer, but it doesn't answer them for you.

## What you need

- **Python 3.11 or newer.** PlanExe uses only the standard library, so you don't need to `pip install` anything.
- **The Claude Code CLI, logged in.** PlanExe makes its LLM calls through Claude Code on your Claude subscription. If you haven't logged in yet, run `claude auth login`.
- **Some time and usage budget.** A full plan takes about 220–260 LLM calls and 1–2 hours.
- **Git**, to download PlanExe.

## Step 1: Download PlanExe

Clone the repository and start Claude Code inside it:

```bash
git clone https://github.com/PlanExeOrg/PlanExe2.git
cd PlanExe2
claude
```

## Step 2: Ask for a plan

Tell Claude Code what you have in mind, in plain words. For example:

> Make a plan for a bakery in Lyon.

A one-line idea is fine. PlanExe's `make-plan` skill takes over from here:

1. It asks you a few short questions to fill in the gaps, such as budget, timeline, location and who's involved.
2. It turns your answers into a fuller project description of about 300–800 words.
3. It checks that description and shows it to you.
4. It starts generating the plan only after you confirm.

You keep control the whole way. If the description doesn't match what you meant, say so and it will revise it.

## Step 3: Let it run

Generating the plan takes 1–2 hours. You'll see a progress bar with an estimated time left. If something interrupts it, running it again resumes where it left off; finished work isn't repeated.

## Step 4: Read your plan

Your plan is saved in a folder named after the date and your project, for example `runs/20261008_bakery_lyon/`. Open `report.html` from that folder in your browser.

The report is long, so here's a good order to read it in:

1. **Decision Dashboard and Decisions Required**: the go/no-go gates and the open choices, each with options, consequences, an owner and a deadline. This also lists the choices PlanExe made on your behalf, which you should confirm or change.
2. **Canonical Facts, Executive Summary and Gantt**: the key numbers and dates, the plan in brief, and the timeline.
3. **Supporting analysis**: the pitch, assumptions, governance, SWOT, team, expert criticism, work breakdown and premortem. Dip into whichever sections matter to you.
4. **Audit trail**: what was checked and how, for when you want to know how far to trust a section.

Want to see the format before making your own? Browse the [example plans]({{ '/examples/' | relative_url }}).

## Tips for a good plan

The plan can only be as good as the description it starts from. Whether you write it yourself or let `make-plan` help you, it's worth covering:

- **Objective**: what success looks like.
- **Scope**: what's included, and what isn't.
- **Location**: where it happens.
- **Budget and timeline**: rough figures are fine.
- **Stakeholders**: who is involved or affected.
- **Constraints**: regulations, hard deadlines, things you won't compromise on.

Write it as flowing prose rather than bullet points, the way you'd explain the project to a colleague.

## Other ways to run it

**Without cloning first.** In any Claude Code session, paste:

> Clone https://github.com/PlanExeOrg/PlanExe2, read its CLAUDE.md, and use its make-plan skill to make me a plan for a bakery in Lyon.

This works, but starting Claude Code inside the cloned folder (Step 1) is more reliable.

**With Codex or another agent.** Other coding agents follow the same steps through the repo's `AGENTS.md`.

**By hand.** If you'd rather write the prompt yourself and run the commands directly:

```bash
python3 -m planexe_skill check-prompt --prompt-file my_prompt.txt
python3 -m planexe_skill create runs/my_plan --prompt-file my_prompt.txt
python3 -m planexe_skill run runs/20261008_my_plan
```

The `create` command prints the actual folder name it made, since it adds the date to the front.

## Good to know

- **Update** PlanExe with `git pull` inside the `PlanExe2` folder.
- **Edit and re-run.** Every step writes plain files to your plan's folder. If you edit one and run again, PlanExe keeps your edit and regenerates everything that depends on it.
- **Sandboxed agents.** If you run Claude Code with its sandbox switched on, run the plan outside the sandbox. PlanExe starts its own `claude` process, and that process needs access to your login.

## Stuck or curious?

The [README on GitHub](https://github.com/PlanExeOrg/PlanExe2) has the full command reference. For questions, ideas or feedback, come say hello on [Discord]({{ '/discord/' | relative_url }}).
