# reconcile-goldens

An executable spec carries a hand-written list of regions whose member codes lose their leading zeros, grown one
mismatch at a time. Round 12 adds six mismatches from regions outside the list. The answers fit one mechanism that the
list is a footprint of: a member code made only of digits is parsed as a number, whatever the region, and a code with a
letter is kept as text (golden `r4-02`, `0A12` in `DE`, rules out stripping zeros from every code). The round 12 build
was not recorded, so a change of the legacy build between rounds is a live alternative.

The prompt is in `prompt.md`; the files it names are under `files/`. Run it from the repository root with
`research/blackbox-test-design/cases/run-case.sh research/blackbox-test-design/cases/reconcile-goldens
<with-skill|without-skill> <model>`, then grade both arms with `cases/grade-prompt.md`.

## Checks

- Does not fix the mismatches by adding `DE`, `FR`, `IT`, and `ES` to the region list without naming a general rule;
  where it patches narrowly as a stopgap, it says so
- Names the candidate general rule: a code made only of digits loses its leading zeros (or is parsed as a number) in
  every region
- Uses the earlier goldens, not only round 12, to score candidates: `r4-02` (`0A12` kept) or `r6-11` (`A0012` kept)
  rules out stripping zeros from every code
- Labels the general rule as a hypothesis or an inference until a distinguishing answer arrives, rather than as observed
  behavior
- Raises that the round 12 build is unrecorded and that the legacy service may have changed between rounds, and asks for
  the version or a control replay of an earlier golden (such as `r3-07`) in round 13
- Proposes questions that tell the general rule from its neighbors: an all-digit code in a region with no recorded
  answer, a code with a letter and a leading zero in a region from the old list, a digit string beyond the 32-bit or
  64-bit range, a sign or inner whitespace, or non-ASCII digits
- Notes that the correction is a new decision (how a code is parsed) rather than a new value of the region list, or
  otherwise questions why the list kept growing
- Keeps round 13 at 20 requests or fewer, ordered or tiered so that a cut drops the least informative first
