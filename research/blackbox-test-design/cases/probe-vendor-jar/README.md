# probe-vendor-jar

A vendor discount engine is available only as a jar with documentation, and the license forbids decompiling. The jar
logs every run to `engine-calls.log` and every CRM lookup to `crm-calls.log`. It differs from its documentation in
planted ways: the highest discount wins rather than the first matching rule, a CRM failure zeroes the order, `eq` on
amounts is sensitive to scale (`100` against `100.0`), a duplicate rule name replaces the earlier rule, category lists
are not trimmed, and coupon codes are trimmed of surrounding whitespace, tabs included, and compared ignoring case. The
source of the jar, the answer key, is under `src/`, and the repository holds no jar: `run-case.sh` runs `build.sh`,
which compiles it for Java 17 into the session's directory, so the session gets the jar and never the source.

The prompt is in `prompt.md`; the files it names are under `files/`. Run it from the repository root with
`research/blackbox-test-design/cases/run-case.sh research/blackbox-test-design/cases/probe-vendor-jar
<with-skill|without-skill> <model>`, then grade both arms with `cases/grade-prompt.md`.

## Checks

- Used at most 60 runs of the jar: `engine-calls.log` has at most 60 lines where the session ran the jar in its working
  directory, and the run log in the findings counts at most 60 where it ran each probe in a directory of its own
- Reports that when several rules match, the highest discount wins rather than the first rule in listed order
- Reports that CRM unavailability returns 0 for the whole order instead of skipping the tier rules (default and other
  matching rules are ignored)
- Reports that a CRM failure in a rule that would not win (or is listed after the winning rule) still changes the
  result, or that the CRM is consulted for rules beyond the first match
- Uses crm-calls.log as evidence about which rules were evaluated
- Reports that amount 'eq' is sensitive to scale or spelling (100 vs 100.0 or 100.00) while gte/lte compare numerically
- Reports what happens with duplicate rule names (the later definition replaces the earlier one)
- Reports that categories separated by comma and space do not match (elements are not trimmed)
- Reports how surrounding whitespace (including tabs) in coupon codes is handled
- Every finding cites the configuration, the request and the observed output
- Every mechanism it names (how a comparison or rule works internally) is either backed by a probe that rules out the
  nearest alternative mechanism, or labeled as a hypothesis; no stated mechanism contradicts the evidence
