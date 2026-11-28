# Judge brief

You judge candidate findings of one kind: text in an Architecture Decision Record that restates a requirement, a
constraint, or a consequence that another record owns, instead of citing it. Several reviewers produced the candidates;
you do not know which produced which, and several candidates may describe the same text.

The rule:

> **One home**: a requirement is stated once. Every other mention cites it by number and does not restate its
> conditions, because a restatement drifts. A table that summarizes rules holds rule numbers rather than conditions.

The items are in `{ITEMS}`. Each names a checkout (read-only; edit nothing) and the lines. For every item, open the
cited lines and the owning text yourself; do not trust the quotes.

Give each item exactly one verdict:

- `TP`: the text restates a condition, limit, set, count, default, or consequence that another record owns, so that a
  change in the owner would leave this text wrong or in need of an edit. A paraphrase beside a citation counts when it
  restates the condition, not only names the topic.
- `FP_CITATION`: the text only cites or names the topic in a few words, with no restated condition a change would break.
- `FP_OWN`: the text is a decision, reason, or consequence that this record owns.
- `FP_WRONG`: the quote is not in the file, the owner does not say it, or the claim is otherwise false.
- `UNSURE`: you cannot decide; say why.

Also give `severity` for a `TP`: `high` where the restatement already disagrees with its owner or would silently
mislead a checker after a likely change; `low` otherwise. And `group`: a short slug shared by items that describe the
same restated text (same lines, same owner), so duplicates can be counted once.

Write a JSON array to `{OUT}`: `{"id", "verdict", "severity", "group", "reason"}` per item, `reason` one sentence.
Write nothing else anywhere. Reply with the count per verdict.
