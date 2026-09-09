# Editing the final-review package

The rules for editing this skill's text are the ones in
[`../test-authoring/AGENTS.md`](../test-authoring/AGENTS.md): a rule that moves in one place moves in every place
that restates it (here, the item in `SKILL.md`, its line in `README.md`, and the trigger paragraph in
`.apm/instructions/`), a carve-out ships with the check that tells it from the rule, a cross-reference names an item
by its heading and never by a number that an insertion would shift, and a paragraph is rewrapped whole after an
edit. `make test` runs `../test-authoring/scripts/check-skill.sh` over this package.
