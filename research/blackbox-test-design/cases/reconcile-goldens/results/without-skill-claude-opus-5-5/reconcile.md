# Reconciling model.py with round 12

## What changed

D4 was a list of regions whose member codes lose their leading zeros: `NL`, `BE`, `LU`. Each region joined the list
after a mismatch (r3-07, r5-14, r8-02, r10-11). Round 12 brought four more regions in one go (`DE`, `FR`, `IT`, `ES`,
six goldens). Adding four more names would follow that pattern, and so would the next round's mismatches.

D4 now says: **a member code made only of digits loses its leading zeros, in every region. A code with a letter in it
is kept as typed.**

- `model.py`: `STRIP_ZEROS_REGIONS` is gone. `member_key` strips leading zeros when the trimmed code is all ASCII
  digits, whatever the region.
- `DECISIONS.md`: D4 is rewritten with its new sources, and the six round 12 goldens are added to the leading-zero
  table.

## Why this rule

- **It fits every golden with a leading zero, rounds 1 to 12.** All 12 were checked against the new model: the six
  round 12 mismatches now match (status, tier and points), and the six older ones still match.
- **It explains r4-02.** `DE` `0A12` answered PLATINUM, which is the member stored as `0A12`. A rule that "strips
  zeros in DE" would have turned this into `A12` and UNKNOWN_MEMBER. Under the new rule `0A12` keeps its zero because
  it has a letter in it. That points to the likely mechanism: the legacy Java code reads all-digit codes as a number
  (something like `Long.parseLong`) and compares everything else as a string. If so, region never mattered. We only
  saw leading-zero numeric codes from NL, BE and LU until round 12.
- **Points did not need a change.** Each round 12 answer equals amount × 0.05, doubled for GOLD, rounded down, which
  is what D6 and D9 already say.

## What I changed without a golden

These cases are guesses either way. Round 13 should settle them.

1. **NL, BE and LU codes with a letter.** The old model stripped zeros from *any* code in those regions, so NL
   `0A12` was UNKNOWN_MEMBER and NL `0A0012` was SILVER. Now NL `0A12` is PLATINUM and NL `0A0012` is UNKNOWN_MEMBER.
   No golden covers either case.
2. **Regions we have never seen**, for example `PT`, `GR` or a new region: these now strip leading zeros.
3. **Non-ASCII digits and signs.** The model only treats ASCII `0-9` as digits. If the legacy service really uses
   `Long.parseLong`, it would also accept `+1234`, full-width `１２３４` and Arabic-Indic `١٢٣٤`.

## An open risk: which build answered round 12?

Rounds 1 to 11 came from `loyalty-points 4.2.7`. Nobody recorded the version for round 12. No golden from rounds 1 to
11 sends an all-digit code with a leading zero outside NL, BE and LU. So we can't tell these two stories apart:

- **(a)** The rule has always been "all-digit codes in every region" and round 12 was the first time we looked.
- **(b)** The stand was upgraded, and the new build strips in more regions than 4.2.7 did.

If (b) is true, the model now describes a different build from rounds 1 to 11, and we have to decide which build is
the migration target. **Before round 13, record `/actuator/info` before and after the batch**, and add the version to
every round from now on.

## Round 13: the 20 requests

Hypotheses we are testing:

- **H1 (the model now):** all-digit codes lose their leading zeros in every region; other codes are kept as typed.
- **H2:** every code loses its leading zeros in every region, but the service falls back to the raw code when the
  stripped one is unknown (this also explains r4-02).
- **H3:** it is still a region list, just a longer one (NL, BE, LU, DE, FR, IT, ES).
- **H4:** the build changed between round 11 and round 12.

Use amount 100 unless a different amount is given. "Model" is what `model.py` answers now.

| # | Region | memberCode | amount | Model | What it decides |
| --- | --- | --- | --- | --- | --- |
| 1 | NL | `0A0012` | 100 | UNKNOWN_MEMBER | Old model said SILVER. Checks the behavior I changed without a golden (H1 vs. the old region rule) |
| 2 | LU | `0A0012` | 100 | UNKNOWN_MEMBER | Same as #1, in a second region from the old list |
| 3 | NL | `0A12` | 100 | OK, PLATINUM, 10 | Old model said UNKNOWN_MEMBER. The other half of #1 |
| 4 | DE | `0A0012` | 100 | UNKNOWN_MEMBER | H1 vs. H2: under H2 the code strips to `A0012` and answers SILVER |
| 5 | DE | `0A12` | 100 | OK, PLATINUM, 10 | Re-runs r4-02. If the answer differs, the build changed (H4) |
| 6 | BE | `0001234` | 100 | OK, GOLD, 10 | Re-runs r10-11, a second check on H4 |
| 7 | DE | `01234` | 100 | OK, GOLD, 10 | Re-runs r12-03. Round 13 must run on the same build as round 12 |
| 8 | PT | `0778` | 30 | OK, SILVER, 2 | H1 vs. H3 in a region that rounds up (1.5 rounds to 2) |
| 9 | GR | `01234` | 15 | OK, GOLD, 2 | H1 vs. H3 in the other round-up region (1.5 rounds to 2) |
| 10 | PT | `0001234` | 15 | OK, GOLD, 2 | Zero-stripping, GOLD doubling and rounding up in one request |
| 11 | AT | `01234` | 100 | OK, GOLD, 10 | A region not seen in any golden. H1 vs. H3, or the region is rejected |
| 12 | SE | `00778` | 100 | OK, SILVER, 5 | A second unseen region |
| 13 | DE | `+1234` | 100 | UNKNOWN_MEMBER | `Long.parseLong` accepts a leading `+` and would answer GOLD |
| 14 | DE | `１２３４` (full-width) | 100 | UNKNOWN_MEMBER | `parseLong` accepts Unicode digits. GOLD here means we should drop `isascii()` |
| 15 | DE | `٠١٢٣٤` (Arabic-Indic) | 100 | UNKNOWN_MEMBER | Same check as #14 for a second script, with a leading zero |
| 16 | DE | `00000000000000000001234` (23 digits) | 100 | OK, GOLD, 10 | Fits in a long once parsed, but is longer than 19 characters. Catches length limits applied before parsing |
| 17 | DE | `99999999999999999999` (20 digits) | 100 | UNKNOWN_MEMBER | Overflows a long. The service may answer UNKNOWN_MEMBER, fall back to string lookup, or return a 400/500. We need the exact status and body |
| 18 | DE | `" 01234"` | 100 | OK, GOLD, 10 | D5 trimming combined with D4 stripping. Does the service trim before it parses? |
| 19 | DE | `" 1234"` (no-break space) | 100 | OK, GOLD, 10 | Python `strip()` removes the no-break space, Java `String.trim()` does not. If the answer is UNKNOWN_MEMBER, D5 has its own gap |
| 20 | DE | `-1234` | 100 | UNKNOWN_MEMBER | `parseLong` gives -1234, which is not 1234. If the answer is GOLD, the service strips signs or uses the absolute value |

### How to read the answers

- **#5 to #7 disagree with the earlier goldens:** stop and settle H4 (which build is the target) before using any
  other answer.
- **#1 and #2 answer SILVER and #3 answers UNKNOWN_MEMBER:** NL and LU strip zeros from every code. Keep that for the
  old regions and make the all-digit rule apply only to the others.
- **#4 answers SILVER:** H2 is the rule. Strip zeros from every code and fall back to the raw code.
- **#8, #9, #11 or #12 answer UNKNOWN_MEMBER:** H3 is the rule, so we go back to a region list. Then ask for the full
  list of regions the service supports, not one region per round.
- **#13 to #15 answer GOLD:** the service parses codes as numbers. Change the digit test in `member_key` to match what
  Java accepts.
