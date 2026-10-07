# Decisions in model.py

| Id | Decision | Source |
| --- | --- | --- |
| D4 | Member codes in `NL`, `BE`, `LU` are normalized by stripping leading zeros | r3-07 (NL, `0778`), r5-14 (BE, `001234`), r8-02 (LU, `0778`), r10-11 (BE, `0001234`); each was a mismatch fixed by adding the region |
| D5 | Member codes are trimmed of surrounding spaces | r1-04 (DE, `" 1234"`) |
| D6 | `GOLD` and `PLATINUM` earn double points | r2-01, r4-09 |
| D9 | `PT` and `GR` round points up | r7-03, r9-15 |

## Goldens that involve member codes with a leading zero, rounds 1 to 11

| Golden | Region | memberCode | Response |
| --- | --- | --- | --- |
| r3-07 | NL | `0778` | OK, SILVER |
| r4-02 | DE | `0A12` | OK, PLATINUM |
| r5-14 | BE | `001234` | OK, GOLD |
| r6-11 | FR | `A0012` | OK, SILVER |
| r8-02 | LU | `0778` | OK, SILVER |
| r10-11 | BE | `0001234` | OK, GOLD |

The legacy build that answered rounds 1 to 11 reported `loyalty-points 4.2.7` on `/actuator/info`. Nobody recorded the
version for round 12.
