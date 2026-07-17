# Report quality

## Independent classifications

Classify each retained candidate independently on these axes:

- Finding confidence: `Confirmed` for directly reproduced behavior with decisive evidence; `Strong static evidence`
  for a defect demonstrated by exact code or configuration paths without runtime reproduction; `Suspected` for a
  plausible risk that still needs decisive evidence.
- Evidence source: `Runtime`, `Browser`, `Test or executable check`, `Static`, or `Mixed`. Use `Mixed` only when the
  claim materially depends on more than one source.
- Check outcome: `Reproduced` when the check observed the candidate, `Not reproduced` when an aligned and adequate
  check did not observe it, or `Not checked` when the check was not run or could not answer the claim.
- Severity: `Critical`, `High`, `Medium`, or `Low`, based on impact and recoverability rather than confidence or source.

Apply this severity rubric:

- `Critical`: catastrophic or broadly exploitable security, integrity, availability, or irreversible data impact with
  no practical containment or recovery path.
- `High`: major impact to core or broad use, security, or data integrity; recovery is difficult, risky, or unavailable
  to affected users, and no practical workaround exists.
- `Medium`: meaningful functional, operational, compatibility, or security impact with limited scope, a practical
  workaround, or reliable recovery.
- `Low`: localized or minor impact that is easy to avoid or recover from and does not compromise a core contract.

## Candidate decisions

Challenge every candidate against intended requirements, exact changed behavior, public and persisted contracts, the
base revision, tests, ADRs, documented limitations, explicit deferrals, accepted risks, and contradictory evidence.
Reject candidates that do not violate an applicable requirement. Record useful rejection reasons when they prevent
repeated work.

Merge candidates that share one cause, impact, fix, and retest. Split claims that can fail, be fixed, or be retested
independently. Reclassify rather than inflate confidence when evidence supports only part of a claim. `Suspected`
candidates stay in follow-ups or limitations and outside the main finding count.

Prefer two anchors for each main finding: one anchor at the defective implementation or configuration and one at the
affected caller, consumer, contract, test, runtime evidence, or user-visible result. Use one anchor only when it proves
both cause and impact; explain the supported scope without speculation.

## Previous runs

Reconcile every available prior finding as `Reproduced`, `Not reproduced`, `Superseded`, `Accepted or out of scope`,
or `Not checked`, with the evidence or blocking constraint. Do not infer that an unexecuted check is fixed, and do not
drop a prior item silently.

## Report validation

Before finalizing, verify that:

- the target revisions and final recheck are complete and internally consistent;
- every required coverage row has a terminal status and records the impact of partial or skipped work;
- finding counts match the listed confidence and severity classifications, excluding suspected candidates;
- each main finding includes severity, confidence, evidence source, check outcome, problem, anchors, reproduction,
  actual and expected behavior, affected scope, supported fix direction, and retest criteria;
- negative results, limitations, permissions, runtime alignment, mutations, cleanup, and previous-run decisions are
  represented accurately;
- every code, report, and artifact link resolves, refers to the intended target, and does not expose sensitive data;
  and
- screenshots, logs, command output, and other artifacts exist at the recorded paths and support the claims that cite
  them.

Keep unavailable evidence explicit. Never promote predicted behavior to an observed result or finalize while a
material permission or runtime decision remains unresolved.
