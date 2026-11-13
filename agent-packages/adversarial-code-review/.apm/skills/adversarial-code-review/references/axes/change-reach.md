# Axis: change reach

What else does the change have to reach that a search for the changed code does not find?

## Check

**Sets.** A change that adds a member to a set (a variable, a flag, a configuration option, an enum constant) has a
sibling in every place that lists the other members: a page's table of options, a help text, a CI matrix, a schema, a
switch over the enum. Search for two existing members by name, or for the one where the set had one, and read every file
that names both: a list there without the new member is a finding. Then search the prose for the set's old size, in
digits and in words (`both`, `two`, `the three`): a sentence that still counts the members as before is a finding.

**Commands.** For every command the change adds or edits in a page, a comment, a help text, or a recipe, and every
command whose outcome depends on a configuration the change creates, find the script, build target, or CI job that runs
that exact form, flags included; a form that differs by a flag, a tool, or a version does not count. Where none does,
compare what the tool's help text, reference, or source says the command acts on with the configuration the change
creates, in each version the change supports. Only where that leaves in doubt a concrete property of this configuration
that decides the outcome, report the doubt and ask for a run of that form or for the form a job runs.

**Remedies.** For every remedy, troubleshooting row, or step the change writes, list the paths its symptom or cause
names, such as two build targets, and check that its action names a step for each. A fix that answers a review comment
is where this is missed: the comment names one path, and the fix covers that one.

## Severity

A missing member in a list that code reads (a switch, a schema, a CI matrix) is `major`; in a page or a help text,
`minor`.
