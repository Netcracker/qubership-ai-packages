# Case: a structural decision in a repository with records of another template

The repository has eleven accepted records in an older template: metadata under `####` headings with markdownlint
comments, and no terms or numbered rules. Request 1 records a structural decision, that the token packages import
nothing from the HTTP layer, which a depguard rule already checks, and says that the team agreed to a reading guide and
to the trailers. Request 2 is the noise input: a behavior rule, a refused `alg: none` token, with no test behind it yet.
Where its record cites the structural rule of Request 1, which keeps the HTTP status out of the token packages, the
citation names the rule by what it is about and copies none of its conditions; a record that does not cite it passes.

## Skill parts

- `SKILL.md`: "Local conventions" (**Location and metadata**), "Template", "Rules" (**Form**, the structural rule and
  the behavior rule; **Layer**; **One home**, a citation of a rule of another record by what the rule is about, not by
  what it decides), "Confirmation and implementation notes", "The reading guide" (the guide's contents and the paragraph
  for the agent that writes code), "Drafting from the user's input" (the read before publishing)
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
    requires of `net/http`, `internal/http/`, or the HTTP packages, such as that a token package cannot import them or
    that the rule bars them. A citation that names the rule by its subject, as in "the `net/http` import rule of
    ADR-0012 R2", passes. The marker pairs the HTTP packages with any word of prohibition in the sentence, so its FAIL
    is a possible copy to grade by reading.
12. **Citation by its subject.** Every citation of ADR-0012 or of one of its rules in record 0013, link text included,
    names what the cited rule is about, as in "the import rule of ADR-0012 R1", and not the number alone; a link whose
    text is the title of record 0012 names what the record is about, and a record that cites ADR-0012 nowhere passes.
    The marker reads a citation of a rule, `ADR-0012 Rn`, with a noun phrase right before it that ends in rule,
    restriction, requirement, invariant, check, ban, or limit and is followed by "of", "in", an opening parenthesis, or
    a comma, as in "the import rule (ADR-0012 R1)". Its FAIL is a possible citation without a subject, and a subject
    written after the number, or a citation of the record alone, is graded by reading.

## Running it

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/writer-structural opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/writer-structural
```

`check.py` marks every check; a PASS is a marker found, so read the result before recording a grade.

`controls/template-metadata.md` is the Opus r1 of tree `d42618eb` with the metadata headings of record 0012 at `###`; it
fails check 2. `controls/wrong-number.md` is the same result with record 0012 written as 0001; it fails checks 1 to 5,
which read record 0012. `controls/invented-check.md` is the same result with a **Confirmation** entry for a test that
does not exist added to record 0013 and a guide rewritten in Request 2; it fails checks 9 and 10. That result's record
0013 says under **Related ADRs** that ADR-0012 R2 keeps `net/http` out of the token packages, so all three also fail
checks 11 and 12.

`controls/citation-with-subject.md` and `controls/citation-without-subject.md` are the Opus r2 of tree `ad64edef`, which
cites ADR-0012 nowhere in record 0013, with ADR-0012 linked under **Related ADRs** and one sentence added to the
Justification: "R2 is a rule of its own, with the tag `http`, because the import rule of ADR-0012 R1 applies to token
verification." The first passes every check. The second cites "ADR-0012 R1" without "the import rule of" and fails
check 12 alone.

## Results

Runs of 2026-11-25 on tree `ad64edef`, graded by reading; both models at the default effort. "r1" and "r2" are
`result.md` and `result-2.md`. The case ran again on this tree because **One home** now asks for a citation of a rule of
another record by what the rule is about, in every section, and the read before publishing covers every sentence that
cites a rule; the record of Request 2 may cite ADR-0012.

Opus r2 passes every check, Opus r1 and Sonnet r2 fail check 11, and Sonnet r1 fails checks 11 and 12. Check 12 was
added after these runs and graded on the same results. Each result writes ADR-0012 with the
repository's `####` metadata, numbered import rules tagged `token`, which its guide maps to `internal/token/`, and a
**Confirmation** that names `token-no-http`; each writes the guide and adds to `AGENTS.md` a paragraph that names the
guide and the trailers. Opus r2 cites ADR-0012 nowhere in record 0013. The three others cite it for why
`internal/http/` sets the 401 and say what it decides: Opus r1 that "the import rule of ADR-0012 R1 keeps `net/http` out
of `internal/token/verify`", Sonnet r1 that `internal/token/verify` "cannot import `net/http` (ADR-0012 R1)", and
Sonnet r2 that "the import restriction of ADR-0012 R1 keeps `net/http` out of `internal/token/verify`". Opus r1 and
Sonnet r2 name the rule by its subject before saying what it decides; Sonnet r1 gives the number alone. `check.py`
agrees with these grades.

Trees `88a72faf` and `dc50203b` differ from `ad64edef` only in the guarantee of a dependency under "What belongs in an
ADR": `88a72faf` states it in Context as a fact only where its source has no rules, and `dc50203b` only where its source
is not a decision record. The inputs of this case hold no guarantee of a dependency, so the results above stand for
both trees.

The results of the earlier trees in the next two paragraphs were not graded on check 12, except the Opus r1 of
`d42618eb` through the controls made from it.

On `3b37f1b0`, a tree of the same day whose results this commit replaces, only Sonnet r2 failed check 11; Opus r2 and
Sonnet r1 cited ADR-0012 by its subject, with the consequence for `internal/token/verify` but not the imports the rule
forbids. With four runs per tree, check 11 failed in none to three results across the trees of this change.

On `0b92dea7`, an earlier tree of this change, all four results passed checks 1 to 10, and three passed check 11 because
their record 0013 did not cite ADR-0012; Sonnet r2 said that "a token package cannot import HTTP packages (ADR-0012
R1)". On tree `d42618eb`, before this change, all four said that ADR-0012 keeps `net/http` out of the token packages and
failed check 11. Four other earlier trees of this change ran the case, and their results are not kept: check 11 passed
in two of four results on `ba170d99`, four on `d8b52781`, three on `b7a46b78`, and two on `8fe854e2`.

No result names a defect. The intermediate trees of the previous change, `89cbfb4e` to `1db689e3`, ran this case as
well and passed checks 1 to 10 by meaning; their results are not kept.

The baselines ran on 2026-11-11 with `english-developer-style` alone. Both keep the repository's metadata, but write no
numbered rules, name `token-no-http` only in the Decision, and write a guide that maps no layer. They fail checks 3 to 6
and 8, and Sonnet also fails check 7: its line in `AGENTS.md` never names the guide. Both also fail checks 11 and 12,
each saying that ADR-0012 keeps `net/http` out of the token packages and citing the record by its number alone, which
the marker of check 12 does not read.
