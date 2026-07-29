# troubleshooting-skill-creator

A single user-invoked skill that builds a repository's own troubleshooting-skill APM package: it scans the target
repository, harvests the troubleshooting material already there, researches how the technologies it ships fail in the
field, compiles a symptom-indexed reference, and wraps it in the skill that reads it.

It generates one read-only advisory skill per repository, backed by one curated troubleshooting reference and without
requiring live-system access.

## Contents

| Path | Purpose |
| ---- | ------- |
| [`SKILL.md`](.apm/skills/troubleshooting-skill-creator/SKILL.md) | The eight-phase authoring procedure. |
| [`references/troubleshooting-format.md`](.apm/skills/troubleshooting-skill-creator/references/troubleshooting-format.md) | The format contract every generated reference follows. |
| [`references/research-playbook.md`](.apm/skills/troubleshooting-skill-creator/references/research-playbook.md) | How to find real failures and ground them in vendor documentation. |
| [`references/deep-research-handoff.md`](.apm/skills/troubleshooting-skill-creator/references/deep-research-handoff.md) | The contract for delegated and external research. |
| [`references/evidence-checklist.md`](.apm/skills/troubleshooting-skill-creator/references/evidence-checklist.md) | The read-only verification checklist. |
| [`references/package-template.md`](.apm/skills/troubleshooting-skill-creator/references/package-template.md) | Verbatim scaffolding for the generated package. |
| [`scripts/show_cases.py`](.apm/skills/troubleshooting-skill-creator/scripts/show_cases.py) | The symptom-catalog and section reader copied into generated skills. |
