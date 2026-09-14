# Editing the telemetry-authoring package

Three of the rules in [`../test-authoring/AGENTS.md`](../test-authoring/AGENTS.md) apply here unchanged. A rule that
moves in one place moves in every place that restates it: here, the section of `SKILL.md`, its item in the §10
checklist, the ecosystem files under `references/` that give its detection, and the trigger paragraph in
`.apm/instructions/`. A cross-reference names a section by its heading and never by an ordinal. A paragraph is rewrapped
whole after an edit. The rules there about test frameworks and measured failure output do not apply. `make test` runs
`../test-authoring/scripts/check-skill.sh` over this package.

A rule that holds in every ecosystem belongs in `SKILL.md`, stated with its detection. A reference file carries only
what its ecosystem answers differently: what a host sees when it configures nothing, which call decides where output
goes, what the formatter does to arguments, and which linter reports what. The six worked cases in
`research/telemetry-authoring/phase2_result.md` §5 are the regression fixture: an edit that changes what the skill emits
for any of them is a reason to re-run that pass, not to patch the skill.
