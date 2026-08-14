# Axis: protocol and format conformance

Finding prefix: `PROTO`.

The specification is the acceptance criterion, and the specification is not in this repository. Find it, read the
normative parts, and compare. Findings on this axis must cite the specification section as well as the code.

## Before anything else

Identify the exact normative source: the RFC and its errata, the standard's version, the vendor document, or — for a
client of someone else's service — that service's source code if it is reachable. Record it in the report. A review
of a protocol implementation against the reviewer's memory of the protocol is worthless; if the source cannot be
found, say so and downgrade every finding to `PLAUSIBLE`.

## What to compare

- **MUST versus SHOULD versus MAY.** Every `MUST` in the relevant sections is a checklist item. Violations of `MUST`
  are at least `HIGH`. Note where the implementation makes a `SHOULD` decision and whether it documents the choice.
- **Encoding and decoding.** Field widths, alignment and padding, endianness, length prefixes that include or exclude
  themselves, optional and variable-length fields, repeated fields, nesting depth, and the maximum sizes the
  specification permits versus the ones the code assumes.
- **Round-trip.** Decode-then-encode must reproduce the bytes for every message the specification allows, including
  the ones this implementation does not understand. Unknown-field handling is where interop breaks.
- **State machine.** The specification's states and transitions against the code's. Connection establishment,
  capability exchange, keep-alive, graceful shutdown, and every "unexpected message in state X" case.
- **Timers and retransmission.** Every timer the specification names: default value, where it is configurable, what
  fires on expiry, and whether the implementation's default matches the normative one.
- **Error and result codes.** The full enumeration, the code the implementation sends for each condition, and what it
  does with a code it does not know.
- **Hostile input.** Truncated messages, length fields that lie, sizes that overflow, deeply nested structures,
  duplicated fields, values outside the permitted range, and messages that are valid but arrive in the wrong state.
  For each: does the implementation reject cleanly, or does it allocate, hang, or corrupt?

## Interop

Ask what this implementation has actually been tested against — a reference implementation, a certified peer, a
recorded capture, or nothing. "Tested against itself" is a finding: two copies of the same wrong assumption agree.

If a reference implementation or a public conformance suite exists and can be run, run it and report the result. If
capture files exist in the repository or the specification's appendix carries example encodings, decode them in a
test.

## Fuzzing

Parsers earn a fuzzer. Check whether one exists and runs in CI. If none exists and the toolchain makes it cheap
(`go-fuzz`, `cargo-fuzz`, Jazzer, `atheris`), run a short session against the decoder and report what it found —
including "nothing in N iterations", which is useful evidence.
