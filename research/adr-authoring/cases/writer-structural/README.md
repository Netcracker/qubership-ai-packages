# Case: a structural decision in a repository with records of another template

The repository has eleven accepted records in an older template: metadata under `####` headings with markdownlint
comments, and no terms or numbered rules. Request 1 records a structural decision, that the token packages import
nothing from the HTTP layer, which a depguard rule already checks, and says that the team agreed to a reading guide and
to the trailers. Request 2 is the noise input: a behavior rule, a refused `alg: none` token, with no test behind it yet.

## Skill parts

- `SKILL.md`: "Local conventions" (**Location and metadata**), "Template", "Rules" (**Form**, the structural rule and
  the behavior rule; **Layer**), "Confirmation and implementation notes", "The reading guide" (the guide's contents and
  the paragraph for the agent that writes code)
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

## Running it

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/writer-structural opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/writer-structural
```

`check.py` marks every check; a PASS is a marker found, so read the result before recording a grade.

`controls/template-metadata.md` is `opus/result.md` with the metadata headings of record 0012 at `###`; it fails check
2. `controls/wrong-number.md` is the same result with record 0012 written as 0001; it fails checks 1 to 5, which read
record 0012. `controls/invented-check.md` is the same result with a **Confirmation** entry for a test that does not
exist added to record 0013 and a guide rewritten in Request 2; it fails checks 9 and 10.

## Results

Runs of 2026-11-11 on tree `d42618eb`, graded by reading; both models at the default effort. "r1" and "r2" are
`result.md` and `result-2.md`. The case ran again on this tree because "What belongs in an ADR" now sorts each
requirement into a decision, a defect, or a guarantee of a dependency, "Open points" gives a question about a defect no
open point, and "Drafting from the user's input" says how such a question is answered. Every requirement of its two
requests is a decision, so the new passages have to stay quiet. All four results pass all ten checks. Each writes
ADR-0012 with the repository's `####` metadata, numbered import rules tagged `token`, which its guide maps to
`internal/token/`, and a **Confirmation** that names `token-no-http`. Each writes the guide and adds to `AGENTS.md` a
paragraph that names the guide and the trailers. In Request 2, each cites ADR-0012 and invents no test name. Opus r1,
Opus r2, and Sonnet r1 write a `token` rule, that verification refuses the token with `TOKEN_ALG_NONE`, and an `http`
rule for the HTTP 401; Sonnet r2 writes one rule tagged `token` and `http` for the response.

No result names a defect. Sonnet r2 suggests an issue of the type Task for the missing tests of Request 2, as Opus r2 of
the previous round asked whether to open one; both rules stay rules. The guide of Opus r2 shows the trailers with a
number that looks real, `Defers: ADR-0013 R3 to #42`. The intermediate trees of this change, `89cbfb4e` to `1db689e3`,
ran this case as well and passed by meaning; their results are not kept.

The baselines ran on 2026-11-11 with `english-developer-style` alone. Both keep the repository's metadata, but write no
numbered rules, name `token-no-http` only in the Decision, and write a guide that maps no layer. They fail checks 3 to 6
and 8, and Sonnet also fails check 7: its line in `AGENTS.md` never names the guide.
