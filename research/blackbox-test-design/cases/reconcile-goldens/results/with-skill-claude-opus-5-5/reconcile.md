# Reconciling model.py with round 12

## What changed

D4 changed shape. It used to be a list of regions; now it is a rule about what a member code looks like:

| | Before | After |
| --- | --- | --- |
| D4 | Codes in `NL`, `BE`, `LU` lose their leading zeros | Codes made only of ASCII digits lose their leading zeros, in every region; codes with a letter keep them |

In `model.py`, `STRIP_ZEROS_REGIONS` is replaced by `NUMERIC_CODE`. `member_key` no longer takes the region. DECISIONS.md
row D4 is updated to match. Nothing else changed: D5 (trim), D6 (double tiers) and D9 (round up in PT/GR) already gave
the right points for all six goldens once the member was found.

The new model gives the recorded answer for all six round 12 mismatches and for every golden listed in DECISIONS.md
(r1-04, r3-07, r4-02, r5-14, r6-11, r8-02, r10-11). I checked this with a one-off script. The repository has no golden
suite, so **the other 74 round 12 answers and rounds 1 to 11 have not been re-run against the new model.** Do that
before relying on it. In particular, if any round 12 answer that "matched" was `UNKNOWN_MEMBER` for an all-digit code
with a leading zero (say PT `0778`), the new rule contradicts it.

## Why not just add DE, FR, IT, ES to the list

That was the cheapest patch, and it is wrong. **r4-02** (DE, `0A12` → OK, PLATINUM) shows that DE does not strip
`0A12` down to `A12`. If DE were on the list, that golden would come back `UNKNOWN_MEMBER`.

The list was also a footprint, not a rule. All four entries (r3-07, r5-14, r8-02, r10-11) were added one region at a
time, each when a golden failed. No golden before round 12 sent an all-digit code with a leading zero in any other
region (see the table in DECISIONS.md), so nothing ever supported "only these regions". Round 12 is the first time
other regions were asked, and four of four strip.

## Evidence for each part of the new D4

- **observed**: all-digit codes with leading zeros resolve in NL, BE, LU, DE, FR, IT, ES (10 goldens).
- **observed**: DE `0A12` resolves as `0A12`, so the zero is kept when the code contains a letter (r4-02).
- **inferred**: the same holds in every region, including PT, GR and regions never asked. Assumption: there is one
  rule, not a per-region table that just happens to cover the 7 regions asked so far.
- **inferred** (the model had to pick one): only ASCII `0-9` count as digits, there is no sign, and zeros are stripped
  after trimming.
- **hypothesis**, live and not yet told apart by any answer:
  - **H-parse**: the Java service parses all-digit codes as integers (`Long.parseLong` or similar). That would also
    accept `+778` and non-ASCII digits such as `０７７８`, and could fail or reject codes that are too long.
  - **H-fallback**: the code is looked up as sent, and if that misses, looked up again with leading zeros stripped,
    letters or not. This fits every golden too: `0A12` hits on the first lookup. It differs from the model on
    `0A0012`, which would fall back to `A0012` (SILVER).
  - **H-build**: round 12 ran on a different legacy build from rounds 1 to 11 (`4.2.7`). Nobody recorded the version
    for round 12. If the build changed, r4-02 may not hold on it any more, and "strip leading zeros from every code"
    becomes possible.

A second handling point came up while checking this. It is not new from round 12, but it is untested:

- **hypothesis**: D5 trims with Python `str.strip()`, which also removes non-breaking space and other Unicode
  whitespace. Java's `String.trim()` removes only characters up to U+0020. On a Java service the model probably
  accepts `" 1234"` when the legacy service would not.
- **model gap**: a `memberCode` sent as a JSON number (`778`) crashes the model. Jackson would usually coerce it to
  `"778"`.

## Round 13: 20 questions

Before you start and after you finish, record `/actuator/info` (this costs no questions). Ask the vendor whether member
code handling changed after 4.2.7 (also free). Use an amount that keeps the expected points unambiguous. "Model" is the
prediction of the updated `model.py`.

### Must (9)

| # | Region | memberCode | amount | Model | What the answer tells apart |
| --- | --- | --- | --- | --- | --- |
| 1 | DE | `0A12` | 100 | OK, PLATINUM, 10 | Control at the start: replays r4-02. A change means H-build, and every answer below needs a second look |
| 2 | DE | `01234` | 100 | OK, GOLD, 10 | Control at the start: replays r12-03 |
| 3 | NL | `0A12` | 100 | OK, PLATINUM, 10 | Did the old NL rule strip codes with letters? The old model and "strip everything" say UNKNOWN_MEMBER |
| 4 | DE | `0A0012` | 40 | UNKNOWN_MEMBER | H-fallback and "strip everything" say OK, SILVER, 2 |
| 5 | LU | `0A0012` | 40 | UNKNOWN_MEMBER | Same as 4, in a region from the old list |
| 6 | PT | `0778` | 30 | OK, SILVER, 2 | Is the rule region-wide? This region has not been asked yet; the answer also checks round-up (1.5 → 2) |
| 7 | DE | `+778` | 40 | UNKNOWN_MEMBER | H-parse says OK, SILVER, 2 |
| 8 | DE | `" 1234"` (NBSP) | 100 | OK, GOLD, 10 | Java `trim()` says UNKNOWN_MEMBER (D5 is wrong for NBSP) |
| 9 | DE | `" 01234 "` | 100 | OK, GOLD, 10 | Stripping zeros before trimming would say UNKNOWN_MEMBER |

### Should (5)

| # | Region | memberCode | amount | Model | What the answer tells apart |
| --- | --- | --- | --- | --- | --- |
| 10 | GR | `001234` | 15 | OK, GOLD, 2 | Second round-up region not yet asked (1.5 → 2) |
| 11 | DE | `０７７８` (fullwidth) | 40 | UNKNOWN_MEMBER | H-parse (`Character.digit` accepts these) says OK, SILVER, 2 |
| 12 | DE | `778` as a JSON number | 40 | crashes | Jackson coercion says OK, SILVER, 2; a type check gives an error. The model needs a decision either way |
| 13 | DE | `00000000000000001234` | 100 | OK, GOLD, 10 | Is there a length limit or a validation error on long codes? |
| 14 | DE | `0000` | 100 | UNKNOWN_MEMBER | Is an all-zero code `UNKNOWN_MEMBER`, or rejected as invalid? |

### May (3)

| # | Region | memberCode | amount | Model | What the answer tells apart |
| --- | --- | --- | --- | --- | --- |
| 15 | DE | `٠٧٧٨` (Arabic-Indic) | 40 | UNKNOWN_MEMBER | Same as 11, with another Unicode digit block |
| 16 | DE | `0a12` | 100 | UNKNOWN_MEMBER | Case-insensitive lookup says OK, PLATINUM, 10 |
| 17 | IT | `-0778` | 40 | UNKNOWN_MEMBER | H-parse gives -778; this shows whether the sign is rejected or the code is unknown |

### Controls at the end (3)

| # | Golden replayed | Expected |
| --- | --- | --- |
| 18 | r4-02 (DE `0A12`) | OK, PLATINUM |
| 19 | r12-09 (FR `0778`, 40) | OK, SILVER, 2 |
| 20 | r3-07 (NL `0778`, as originally sent) | OK, SILVER |

If the budget is cut, drop the May questions first, then the Should questions from the bottom up. Keep the controls:
without them, a build change between rounds looks the same as a model error.

### How the answers would change the model

- 1 or 18 changes: H-build. Redo the whole D4 analysis against the new build. Do not mix its answers with those from
  4.2.7.
- 3 is UNKNOWN_MEMBER: NL really does strip codes with letters, and region does matter. Ask BE and LU the same way.
- 4 or 5 is SILVER: go with H-fallback, or "strip everything" if 1 also changed.
- 7, 11 or 15 resolves: go with H-parse. Make D4 a numeric parse and ask about overflow next round.
- 8 is UNKNOWN_MEMBER: change D5 to trim only characters up to U+0020.
