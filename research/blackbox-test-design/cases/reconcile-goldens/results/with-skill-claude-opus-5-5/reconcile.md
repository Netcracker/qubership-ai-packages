# Reconciling model.py with round 12

## What the six mismatches have in common

All six are all-digit member codes with leading zeros, sent from regions that were not in the D4 list (DE, FR, IT, ES).
The legacy stand found each one under the code without its zeros (`01234` → `1234` GOLD, `0778` → `778` SILVER), and
the points match what the model already computes for that tier. D5, D6 and D9 are not involved.

D4 was an exception list that grew one region at a time: NL after r3-07, BE after r5-14, LU after r8-02. Each patch was
the narrowest change that fixed the latest mismatch. Round 12 adds four more regions in one go. That pattern suggests a
single rule that never depended on the region, not a list that happens to get longer.

## What changed

- `model.py`: `STRIP_ZEROS_REGIONS` is gone. `member_key` now strips leading zeros from a code that is all ASCII digits
  (after trimming), in **every** region. A code containing a letter is kept as sent.
- `DECISIONS.md`: D4 rewritten with the new rule and all ten goldens behind it, plus a round 12 section in the
  leading-zero table.

**Checked:** a scratch script runs all 13 leading-zero and trimming goldens recorded in DECISIONS.md and
round-12-mismatches.md (r1-04, r3-07, r4-02, r5-14, r6-11, r8-02, r10-11, r12-03/09/17/22/40/51) against the new
model. All 13 match, including the points of the six round 12 cases.

**Not checked:** the 74 other round 12 answers and the full goldens from rounds 1 to 11, because they are not in this
repo. The new rule gives a different answer from the old one in only one case: a code with a leading zero *and* a letter,
sent from NL, BE or LU (for example NL `0A12`). The old model stripped it to `A12` and answered UNKNOWN_MEMBER. The new
model keeps it and answers PLATINUM. DECISIONS.md lists no such golden for rounds 1 to 11. **Please rerun the full
golden suite before relying on this change.**

### Why this rule and not "add DE, FR, IT, ES to the list"

Both fit every recorded answer. The list predicts that PT, GR, AT, PL and any other region not yet seen keep the zeros
(UNKNOWN_MEMBER). Seven out of seven regions that have been sent a leading-zero numeric code stripped the zeros, so the
list has been wrong every time it was tested. The all-digit condition is there because of r4-02: DE `0A12` was found as
`0A12`, so the zeros are not stripped from every code. This is the behavior you would get from the Java service reading
digit-only codes as numbers (for example `Long.parseLong`, or a numeric key column). That mechanism is a
**hypothesis**: nothing observed so far separates it from the alternatives below.

## Status of the claims

| Claim | Status |
| --- | --- |
| DE, FR, IT, ES strip leading zeros from all-digit codes | observed (r12-03, -09, -17, -22, -40, -51) |
| NL, BE, LU strip leading zeros from all-digit codes | observed (r3-07, r5-14, r8-02, r10-11) |
| DE keeps a leading zero when the code has a letter | observed (r4-02, rounds 1 to 11 build) |
| Every region strips the zeros, including ones never asked | inferred, assuming the rule ignores region |
| Only all-ASCII-digit codes are stripped | hypothesis (H1, adopted) |

Live alternatives, all of which fit every recorded answer:

- **H1 (adopted):** strip the zeros from an all-digit code in any region; keep codes with a letter as sent.
- **H2:** in any region, look up the exact code first, then the code with its zeros stripped. This also explains r4-02.
  It differs from H1 on `0A0012`, which H2 finds as `A0012` SILVER.
- **H3:** the list is real and is now NL, BE, LU, DE, FR, IT, ES. It differs from H1 in any other region.
- **H4:** NL, BE, LU strip zeros from every code, as the old model did; the other regions strip only all-digit codes.
  It differs from H1 on NL `0A12`.
- **H5: the build changed.** Rounds 1 to 11 came from `loyalty-points 4.2.7`. Nobody recorded the version for round 12.
  If round 12 ran on a newer build, the region list could have been right for 4.2.7 and been dropped later. In that case
  the model has to target one version on purpose. No question sent to the current stand can rule this out; recording
  the version and replaying controls can.

## Round 13: what to ask (20 requests)

Before the round, at no cost against the budget:

- Read `/actuator/info` before and after the round and store the version with the answers. Also ask whoever ran round
  12 which build it was. That answers H5.
- Ask the vendor or the stand owners whether member codes are stored or looked up as numbers.

Model predictions come from the updated model.py. Amounts are picked so that rounding or the double-points tier would
show in the points.

| # | Tier | Region | memberCode | amount | Model predicts | Separates |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | must | DE | `0A12` | 100 | OK PLATINUM 10 | control, replays r4-02; anchors "letters keep zeros" on this build (H5) |
| 2 | must | DE | `01234` | 100 | OK GOLD 10 | control, replays r12-03 |
| 3 | must | NL | `0778` | 100 | OK SILVER 5 | control, replays r3-07 |
| 4 | must | PT | `0778` | 30 | OK SILVER 2 | H1 vs H3 (region not yet asked); also D9 rounding up after stripping (1.5 → 2) |
| 5 | must | AT | `01234` | 100 | OK GOLD 10 | H1 vs H3, region that has never appeared in any golden |
| 6 | must | NL | `0A12` | 100 | OK PLATINUM 10 | H1 vs H4 and the old model (UNKNOWN_MEMBER) |
| 7 | must | DE | `0A0012` | 100 | UNKNOWN_MEMBER | H1 vs H2 (H2: SILVER) |
| 8 | must | NL | `0A0012` | 100 | UNKNOWN_MEMBER | with #6 and #7, tells H2 from H4 (H4: SILVER in NL only) |
| 9 | should | GR | `001234` | 15 | OK GOLD 2 | H1 vs H3 in the other round-up region (1.5 → 2) |
| 10 | should | PL | `0778` | 40 | OK SILVER 2 | H1 vs H3, a third region outside the list |
| 11 | should | DE | `+1234` | 100 | UNKNOWN_MEMBER | `Long.parseLong` accepts `+` (GOLD); a digit-only check does not |
| 12 | should | DE | ` 1234` (no-break space) | 100 | OK GOLD 10 | D5 trimming: Python `strip` (the model) removes NBSP, Java `trim` does not |
| 13 | should | DE | `" 01234 "` | 100 | OK GOLD 10 | whether trimming happens before stripping zeros (order of D5 and D4) |
| 14 | should | DE | `1234` as a JSON number, not a string | 100 | model crashes (`.strip` on int) | Jackson converts it to `"1234"` by default; the model has no opinion. Fix the model whatever the answer |
| 15 | may | DE | `١٢٣٤` (Arabic-Indic digits) | 100 | UNKNOWN_MEMBER | `Long.parseLong` reads non-ASCII digits as 1234 (GOLD) |
| 16 | may | DE | `０１２３４` (full-width digits) | 100 | UNKNOWN_MEMBER | same, with a leading full-width zero |
| 17 | may | DE | `99999999999999999999` | 100 | UNKNOWN_MEMBER | overflows a `long`: watch for a 500 or another error status instead of UNKNOWN_MEMBER |
| 18 | may | DE | `00000000000000000001234` (23 chars) | 100 | OK GOLD 10 | a numeric reading versus a length or format check on the raw string |
| 19 | must | DE | `0A12` | 100 | OK PLATINUM 10 | end control, repeats #1 |
| 20 | must | DE | `01234` | 100 | OK GOLD 10 | end control, repeats #2 |

**Drop order if the budget is cut:** drop `may` first (15–18), then `should` from the bottom up (14 → 9). Keep both
end controls if possible; if only one fits, keep #19. Questions 1–8 are the minimum that decides between H1 to H4.

**How to read the answers:**

- If any control answers differently from before, or the version is not 4.2.7, check H5 before changing the model.
- If #4, #5, #9 or #10 answer UNKNOWN_MEMBER, H3 holds: put back a region list and record exactly which regions strip.
- If #6 or #8 differ from #7, the region does matter for codes with letters (H4).
- If #11, #15 or #16 answer GOLD, the service parses the code as a number. Then the model should copy Java's
  `Long.parseLong` (sign, Unicode digits) and not just `isdigit`.
- If #12 answers UNKNOWN_MEMBER, change D5 to Java `trim()` semantics (strip only characters ≤ U+0020).

Each change in round 13 should go back through this process: decide whether it changes the value of an existing
decision or adds a new one. Another round that turns up a new decision means the questions are still finding structure
the model doesn't have.
