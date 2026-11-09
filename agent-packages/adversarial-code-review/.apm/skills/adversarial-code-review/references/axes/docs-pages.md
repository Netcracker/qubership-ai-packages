# Axis: documentation pages

Load `docs-page-authoring` and `english-developer-style`.

## Check

- Whether the change owes a page an entry, by `docs-page-authoring`: a user-settable option, a user-visible error or
  diagnostic, a supported version, a changed behavior. A change that owes one and has none is a finding; name the page.
- Pages the change edits: every claim against the code (defaults, units, option names, error text), and the slots the
  skill requires.
- Pages the change does not edit but makes wrong: search the documentation for the option, the behavior, or the error
  the change touches.

## Severity

A page that now states the wrong behavior or default is `major`; a missing entry is `minor`.
