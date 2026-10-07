# shadow-diff-normalizer

A team mirrors production traffic to an old and a new service and has written a normalizer that brings the diff from
about 30% to under 1%. Each rule erases a class of differences, and several erase differences a client can observe. The
review should say which rules hide behavior, and how to keep the noise down without losing it.

The prompt is in `prompt.md`; the files it names are under `files/`. Run it from the repository root with
`research/blackbox-test-design/cases/run-case.sh research/blackbox-test-design/cases/shadow-diff-normalizer
<with-skill|without-skill> <model>`, then grade both arms with `cases/grade-prompt.md`.

## Checks

- Flags that sorting every array hides order a client can observe (line items, the order of errors), and proposes
  sorting only where the contract says order does not matter
- Flags that dropping nulls merges `null` with an absent field, which a client or a later deserializer can tell apart
- Flags that comparing numbers as doubles hides scale and precision (money such as `10.10` against `10.1`, large ids or
  amounts past 2^53), and proposes a decimal comparison or a per-field rule
- Flags that a case-insensitive `status` hides a real contract change for clients that compare the string
- Flags that ignoring every `id`, the HTTP status, or the headers hides differences a client depends on (201 against 200
  on a POST, a `Location` header, a foreign key in a nested `id`)
- Proposes checking each rule's merged classes, by feeding the normalizer pairs that differ in one aspect or by counting
  how many raw differences each rule erases, rather than trusting the 1% figure
- Keeps the raw diff, or a record of what each rule erased, next to the normalized one
- Raises the safety of mirrored writes: shadowed POST or PUT requests must not reach shared side effects (Oracle rows,
  payments, emails), or must go to an isolated environment
- Orders its findings by the cost of being wrong, with money and status fields first
