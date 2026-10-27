# Axis: least surprise for the end user

Finding prefix: `SURP`.

Does the product do what its own words told the user it would do? A user who clicks "Disable", sets
`retentionDays: 30`, or runs `tool remove x` acts on an expectation, and the product created that expectation through
a label, an option name, a help line, a comment, or its own behavior elsewhere. This axis finds the places where the
behavior contradicts that expectation and the user pays for it: lost data, an exposure they did not choose, or a wrong
result they accept as right. Every finding pairs the expectation with the behavior and quotes both. A surprise that
cannot be pinned to something the product said or did is a preference, and it is not reported.

The surfaces are the ones a person operates: the UI, the CLI as typed by a human, configuration and chart values, and
an HTTP API where a person writes the requests by hand or through a thin client. When the run slices this axis to one
component, inventory that component's surfaces only, and list in the coverage the surfaces you did not reach.

## Where an expectation may come from

Strongest first. Cite the source in **Expected** by path and line, or by screenshot or command output.

1. **The product's own words** about this operation: a button or menu label, a confirmation dialog, a toast, the
   `--help` line, an option or field name, a values-file comment, a doc page, an error message.
2. **A platform convention the product visibly follows elsewhere.** A `--force` flag elsewhere in the tree implies the
   unforced default is safe; `disable` beside `delete` implies the first is reversible; HTTP `PUT` and `DELETE`
   semantics where the API otherwise follows them; `kubectl`-style verbs in a CLI that copies `kubectl`. Quote the
   place where the product follows the convention, not only the convention.
3. **The product's own behavior in a sibling place**: the same operation in the UI and in the API, the same value in
   two fields, the same verb on two resource types.

A convention the product nowhere follows, a competitor's behavior, or "users usually expect" is not a source.

## What counts as a finding

- **A destructive or irreversible action with no confirmation, warning, or undo,** worst where the name promises a soft
  action: "Disable" that deletes, "Uninstall" that drops the data volume, "Remove from view" that hard-deletes, a
  "Reset" that also discards saved settings. Also a confirmation that names less than the action destroys ("Delete
  this version?" when the call deletes the whole package).
- **A value silently coerced or reinterpreted:** a unit other than the one the name or comment states, case folding
  that merges two distinct names, truncation, clamping to a range nobody is told about, an invalid value replaced by
  the default instead of rejected, an empty string read as "all". The user believes their value is in effect.
- **A default that contradicts the label or name at the point of choice:** sharing on by default under a "Private"
  label, auto-deletion after N days under a setting named "Keep history", overwrite-on-conflict in an "Import" that
  merges everywhere else. The source is the label, name, or comment on the screen or in the file where the user makes
  the choice; a default you would not have chosen, with no such words beside it, is a preference.
- **A hidden side effect of an innocent-looking operation:** a "Save" that also publishes, a read or a "Preview" that
  mutates state, a rename that breaks every existing link, an import that replaces rather than merges.
- **Visible success that did not happen:** a "Saved" toast the code shows without reading the response, `Deleted 3
  items` when one was skipped, a CLI that prints the new value and persists the old one. A status code that reports
  success to a program is `error-model`'s on HTTP (`surfaces/rest-http.md`) and `api-ux`'s elsewhere. A browser screen
  that shows success or stale data because it lost a failed response is `frontend-web`'s.
- **Feedback the product's own words promise and never give:** a "Saving…" label that never resolves, a job whose help
  says it reports progress and does not, a background operation whose failure is shown nowhere the product tells the
  user to look. Quote the words. A browser screen that gives no feedback on a slow or failed request, with no such
  words, is `frontend-web`'s.
- **One concept meaning different things in different places:** "Archive" is reversible in the UI and a delete in the
  API; "version" counts from 0 in one screen and from 1 in another; the same filter is case-sensitive in search and
  not in export.

## What is not a finding

- An expectation with no source from the list above. Write it under *Отклонено автором* with "no product source".
- A surprise that costs nothing: a cosmetic inconsistency, an extra click, a different word for the same safe action.
- A destructive action whose words say exactly what it destroys and that asks before doing it. Destruction is not a
  surprise when it is announced.
- A behavior the product documents next to the control the user operates (the help line, the dialog, the field hint),
  even if you would have designed it otherwise. A doc page the user would not open from that control does not count
  as announcing it; see the rule under *Ownership*.
- Naming and discoverability defects that mislead nobody into a costly action. Those are `api-ux`.

## Method

1. **Inventory the state-changing operations** on each surface: UI actions (buttons, menu items, bulk actions, drag
   and drop), CLI subcommands that write, configuration values that change behavior, API calls a person issues. Use
   the route table, the CLI command tree, the values file, and the UI component tree. Reads stay in only when the UI
   presents them as a mutation-free preview.
2. **Write the expectation before you test.** For each operation, quote its own words and the sibling or convention
   that applies. Doing this first keeps the observed behavior from rewriting your expectation.
3. **Execute.** Run it against the runtime `00-commands.md` names: click it in the browser, run the CLI against a
   throwaway target, render the chart with the value, send the request. Then inspect state directly: the database
   row, the object store, the cluster, the file. The UI telling you it worked is the thing under test. Use a
   throwaway namespace, schema, or account; never run a destructive operation against shared data.
4. **Probe values at the boundaries** for every field and option with a unit, a range, or an enum: zero, negative, one
   past the maximum, wrong case, an unknown enum value, an empty string, the unit spelled out (`30s` where a number is
   expected). Record what was stored, not what was echoed back.
5. **Trace where you cannot execute,** from the control to the handler to the store, naming each branch. A traced
   destructive path still counts; say so in **Проверка**.
6. **Falsify.** Look for the confirmation in a parent component, the undo in a trash or soft-delete column, the
   validation in a schema, the warning in the dialog. Report only what survives.

## Required section: expectation table

The report carries a section `## Expectation table` with one row per operation you examined, finding or not:

| Operation | Expectation and its quoted source | Actual behavior | Evidence |
| --- | --- | --- | --- |
| UI: package menu → "Disable" | "Disable" beside a separate "Delete" item (`ui/src/PackageMenu.tsx:41`) | hard-deletes the package and its versions | DB row gone after click; `work/surp/disable.log` |

Executed rows without a finding go to *Checked and sound* as well. A row whose expectation has no source is not in the table.

## Severity

Rate by what the user who acted on the expectation loses.

| Consequence | Level |
| --- | --- |
| Data lost or overwritten with no recovery path; data exposed to people the user did not choose | `CRITICAL` |
| A wrong result accepted as right and acted on (a value coerced, a success that did not happen) in a flow that feeds a decision or a release; data lost with a recovery path only an administrator knows | `HIGH` |
| A side effect or default the user must notice and undo by hand; one concept with two meanings across surfaces | `MEDIUM` |
| Missing feedback where the user can still find out by looking; a surprise with a cheap, obvious undo | `LOW` |

A fix that changes behavior callers depend on (rejecting a value that used to be clamped) is still the fix; say in
**Fix** that it is a compatibility change, and leave the migration to `api-compatibility`.

## Ownership

**Surface packs win.** Where `references/surfaces/<form>.md` assigns a concern to an axis, that row decides. This axis
takes what no pack row names, and the consequence-based framing above.

**Docs versus behavior, one rule:** the owner is the side the fix must change. When the doc page is the only statement
of the behavior and the product's other words (labels, help, option name, siblings) agree with the code, correcting the
page makes the product truthful, so the finding is `docs-pages`. When the product's other words agree with the page,
or the page describes the safe behavior and the code does something a user cannot recover from, the behavior must
change, so the finding is `SURP`. When the evidence does not say which side is intended, `docs-pages` reports
it and names this axis; record one line under *Cross-axis notes*.

| Concern | Owner axis |
| --- | --- |
| The gap between what an operation's words promised and what it did to user state, data, or exposure; a UI that never shows the progress, completion, or failure its own words promise; a human-readable message stating a success that did not happen | `least-surprise` |
| Developer-facing naming, shape, and discoverability; a name that is merely unclear; a CLI with no `--help`, or help missing defaults and units (`surfaces/cli.md`) | `api-ux` |
| Help text and parser disagreeing on a flag, default, or precedence (`surfaces/cli.md`); code that deviates from what its own author intended (spec, doc comment, test name). Where the code does what its author intended and the intent contradicts what the user was told, the finding is `SURP` | `correctness` |
| Cascade, tombstone, retention, and recovery mechanics of a deletion. Whether the user was told the deletion would happen is `SURP` | `data-lifecycle` |
| A doc page wrong about the code, per the rule above | `docs-pages` |
| UI rendering, state, routing, and accessibility defects, such as a spinner stuck because of a race | `frontend-web` |
| Error classification and codes; how a program tells failure from success | `error-model` |
| An exposure an attacker reaches regardless of what the UI says; a bypass of a confirmation gate by attacker-influenced input. An exposure that exists because a label or default told the user otherwise is `SURP` | `security` |
| Configuration rejected too late or with a bad message. A value accepted and read with a meaning other than its name or comment states is `SURP`; template type coercion in a chart is `correctness` via `surfaces/helm.md` | `deployment-config` |
| Changing a default or a meaning between versions; the migration a `SURP` fix needs | `api-compatibility` |
