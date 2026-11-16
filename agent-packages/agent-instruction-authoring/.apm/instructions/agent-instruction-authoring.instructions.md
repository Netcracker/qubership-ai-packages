---
description: "Trigger for the agent-instruction-authoring skill: load it before writing, editing, fixing, or reviewing text an AI agent follows, and above all before changing a skill after a failed case or eval run."
applyTo: "**"
---

Before writing, editing, fixing, or reviewing text an AI agent will follow, load `agent-instruction-authoring`: a
`SKILL.md`, an `AGENTS.md` or `CLAUDE.md`, a rules or instructions file, an agent persona, a review checklist, or a
brief for a subagent or another model that a skill, script, or workflow keeps. Load it above all when a case, an eval
run, or a user reports a bad output and you are about to change the skill or instruction that produced it, before the
first line of the fix.
