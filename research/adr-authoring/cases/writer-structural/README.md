# Case: a structural decision in a repository with records of another template

The repository has eleven accepted records in an older template: metadata under `####` headings with markdownlint
comments, and no terms or numbered rules. Request 1 records a structural decision, that the token packages import
nothing from the HTTP layer, which a depguard rule already checks, and says that the team agreed to a reading guide and
to the trailers. Request 2 is the noise input: a behavior rule, a refused `alg: none` token, with no test behind it yet.
Its record cites the structural rule of Request 1, which keeps the HTTP status out of the token packages, and the
citation copies none of that rule's conditions.

## Skill parts

- `SKILL.md`: "Local conventions" (**Location and metadata**), "Template", "Rules" (**Form**, the structural rule and
  the behavior rule; **Layer**; **One home**, a citation that copies no condition of the cited rule), "Confirmation and
  implementation notes", "The reading guide" (the guide's contents, among them the line that sends the agent that
  writes code to the **Related ADRs** of a cited record, and the paragraph for the agent that writes code)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Record 0012.** Request 1 writes `docs/adr/0012-<slug>.md`.
2. **Metadata from the repository.** Record 0012 keeps the repository's metadata headings: `#### Owner`, as the
   existing records write it.
3. **Rules from the template.** Record 0012 has a **Rules** heading with numbered rules, which the existing records
   lack.
4. **Tag of the constrained code.** Every rule of record 0012 about importing `internal/http/` or `net/http` carries a
   layer tag that the guide Request 1 writes maps to `internal/token/`: the code the invariant ranges over, not the
   place where depguard runs.
5. **Confirmation names the check.** Record 0012's **Confirmation** names `token-no-http`.
6. **Guide added.** Request 1 writes `docs/adr/README.md`, which maps `internal/token/` and lists `docs/adr/` among the
   paths that belong to no layer.
7. **Paragraph for the agent that writes code.** Request 1 changes the hand-written `AGENTS.md` to name
   `docs/adr/README.md` and the trailers, keeps its two lines, and does not copy the map: no `internal/token` in it.
8. **Behavior rule.** Request 2's record 0013 has a rule with HTTP 401 and `TOKEN_ALG_NONE`.
9. **No invented check.** Record 0013's **Confirmation** has no entry: no test covers the rule yet.
10. **Guide left alone.** Request 2 writes neither `docs/adr/README.md` nor `AGENTS.md`: both exist after Request 1,
    and a behavior rule in a mapped layer changes neither.
11. **Citation without the condition.** No sentence of record 0013 says, outside the text of a link, what ADR-0012
    requires of `net/http`, such as that a token package cannot import it. A citation that names the rule by its
    subject, as in "the `net/http` import rule of ADR-0012 R2", passes.
12. **Guide names replaced rules.** The guide of Request 1 sends the reader of a cited rule to the **Related ADRs** of
    its record for a record that replaces it.

## Running it

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/writer-structural opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/writer-structural
```

`check.py` marks every check; a PASS is a marker found, so read the result before recording a grade.

`controls/template-metadata.md` is the Opus r1 of tree `d42618eb` with the metadata headings of record 0012 at `###`;
it fails check 2. `controls/wrong-number.md` is the same result with record 0012 written as 0001; it fails checks 1 to
5, which read record 0012. `controls/invented-check.md` is the same result with a **Confirmation** entry for a test
that does not exist added to record 0013 and a guide rewritten in Request 2; it fails checks 9 and 10. That result's
record 0013 says that ADR-0012 R2 keeps `net/http` out of the token packages, and its guide does not send the reader to
**Related ADRs**, so all three also fail checks 11 and 12.

## Results

Runs of 2026-11-12 on tree `8fe854e2`, graded by reading; both models at the default effort. "r1" and "r2" are
`result.md` and `result-2.md`. The case ran again on this tree because **One home** now says how a citation of another
record's rule reads, and Request 2 cites ADR-0012, and because the guide's contents now send the agent that writes code
to the **Related ADRs** of a cited record. All four results pass checks 1 to 10 and 12 by meaning. Each writes ADR-0012
with the repository's `####` metadata, numbered import rules tagged `token`, which its guide maps to `internal/token/`,
and a **Confirmation** that names `token-no-http`; each writes the guide and adds to `AGENTS.md` a paragraph that names
the guide and the trailers. Each guide says, in one sentence or two, that where a rule cites a rule of another record,
the reader also reads that record's **Related ADRs**, where a line names any later record that replaces the cited rule.
In Request 2, Sonnet r2 writes one rule tagged `token` and `http`, the others a `token` rule and an `http` rule, and
none invents a test name. `check.py` fails Sonnet r2 on check 8 by the marker alone: its HTTP 401 sits in the term
"refuse", which its R1 uses.

Check 11 passes in two of four results. Opus r1 and r2 cite "the import rule of ADR-0012 R1" and say nothing of what it
requires. Sonnet r1 and r2 fail it: Sonnet r1 says that "the import rule of ADR-0012 R1 keeps `net/http` out of
`internal/token/verify`", and Sonnet r2 that "the `net/http` import rule of ADR-0012 R2 keeps the status constants of
`net/http` out of" the token package. On tree `d42618eb`, before this change, all four results said that ADR-0012 keeps
`net/http` out of the token packages, and the results of that tree, replaced in this commit, all fail check 11. Three
earlier trees of this change ran the case and their results are not kept: on `ba170d99` two of four passed check 11, on
`d8b52781` four of four, and on `b7a46b78` three of four. No result of those trees passes check 12, which their skill
did not ask for.

No result names a defect. The intermediate trees of the previous change, `89cbfb4e` to `1db689e3`, ran this case as
well and passed checks 1 to 10 by meaning; their results are not kept.

The baselines ran on 2026-11-11 with `english-developer-style` alone. Both keep the repository's metadata, but write no
numbered rules, name `token-no-http` only in the Decision, and write a guide that maps no layer. They fail checks 3 to 6
and 8, and Sonnet also fails check 7: its line in `AGENTS.md` never names the guide. Both also fail check 11, each
saying that ADR-0012 keeps `net/http` out of the token packages, and check 12.
