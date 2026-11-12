# Case: notes that mix a decision with a defect fix and a dependency's guarantee

The input is three requests in one repository. Request 1 has notes on running the service under Docker, which is a
decision, and three more points that are not decisions. The service's Dockerfile replaces the entrypoint of the platform
base image, which the platform's guide says to keep and the repository's other image keeps, so restoring it is a defect
fix; the notes ask it as an open question. The base image's entrypoint adds the certificates under `/tmp/cert` to the
trust store, a guarantee of the base image. The chart volumes that the restored entrypoint needs only make the fix work.
The skill writes rules for the decision alone, proposes a Bug issue for the entrypoint with the chart volumes in it,
keeps the issue and the fix out of the record, and offers no choice between the two entrypoints.

Requests 2 and 3 are the noise inputs, decisions that look like the other two kinds and get rules with no defect named.
In Request 2 the security architect refuses `none` and the HMAC algorithms, while the library already refuses `none`
without the reason code and the code accepts HMAC today. In Request 3 the architect requires TLS 1.2 or later for the
outgoing connections, which Go's TLS client already enforces by default with no code of the repository.

The case comes from the first draft of ADR-0101 in
[Netcracker/qubership-authz-agent#235](https://github.com/Netcracker/qubership-authz-agent/pull/235). Its writer asked
the user to choose between the two entrypoints and wrote the answer as R2. It also wrote the base image's handling of
`/tmp/cert` as R3, and the chart's support for that entrypoint under a read-only root file system as R18.

## Skill parts

- `SKILL.md`: "What belongs in an ADR" (a rule records a decision, also one a dependency already provides; a defect
  becomes a proposed issue that the record does not name, and a requirement that only makes the fix work goes into it; a
  dependency's guarantee is a fact in Context), "Open points" (a question about a defect gets no open point), "Drafting
  from the user's input" (a question about a defect gets the issue, not a choice), "Template" (Context), "Rules"
  (**Form**, the behavior rule; **One home**, a rule that other rules imply, which a dependency's default is not),
  "Local conventions" (the next free number), "The reading guide" (no guide rewritten where one exists)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Record 0007.** Request 1 writes `docs/adr/0007-<slug>.md`.
2. **No entrypoint rule.** No rule of Request 1's record names the entrypoint or `CMD`.
3. **No certificate rule.** No rule of Request 1's record states that the service trusts the certificates under
   `/tmp/cert`. A rule on what the Compose example mounts or what a page documents passes by meaning, though it fails
   on the marker.
4. **No chart volume rule.** No rule of Request 1's record names the `emptyDir` volumes or their paths.
5. **Bug proposed.** Request 1's message proposes an issue of the type Bug for the entrypoint of
   `build/token-gate/Dockerfile`.
6. **Volumes with the fix.** Request 1's message names the chart volumes after the Bug, in the proposed issue.
7. **No choice offered.** Request 1's record has no open point on the entrypoint, and its message asks no question
   that offers keeping the binary as the entrypoint as one of the answers.
8. **Guarantee as a fact.** Where Request 1's record names `/tmp/cert`, its **Context** states it with the base image
   as the source.
9. **Fix not in the record.** No line of Request 1's record names the entrypoint or the Dockerfile together with a bug,
   its fix, or its tracking.
10. **Rule for `none`.** Request 2's record has a rule with HTTP 401 and `TOKEN_ALG_NONE`.
11. **Rule for HMAC.** Request 2's record has a rule with HTTP 401 and `TOKEN_ALG_SYMMETRIC`.
12. **No defect in Request 2.** Request 2's message names no bug and calls nothing a defect.
13. **Rule for TLS 1.2.** Request 3's record has a rule that names TLS and the version 1.2.
14. **No defect in Request 3.** Request 3's message names no bug and calls nothing a defect.
15. **No guide written.** No request writes a `README.md`: the repository has its guide.

## Running it

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/writer-defect-and-guarantee opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/writer-defect-and-guarantee
```

`check.py` marks every check; a PASS is a marker found, so read the result before recording a grade.

`controls/before-opus.md` and `controls/before-sonnet.md` are unedited runs of this prompt on the skill before this
change, commit `9a65906`, tree `3b230c74`, at the default effort: `research/adr-authoring/cases/run-case.sh <copy of
this case> <model> result 9a65906`. Opus fails checks 3, 5, 6, and 7 on the marker: R5 says that every certificate of a
private CA file joins the trust store, O1 offers the two entrypoints as answers, and no issue is proposed. Answer (a) of
its O1 spells out the fix, replacing `ENTRYPOINT` with `CMD`, so by meaning it fails check 9 as well. Sonnet fails
checks 2 to 7 and 9: R4 has the container add the certificates to its trust store, R5 puts the `emptyDir` volumes on the
chart, O1 offers the two entrypoints, its implementation notes say to remove the `ENTRYPOINT` line, and no issue is
proposed. Both pass checks 10 to 14: the noise inputs get rules with or without the change.

The other controls are Opus r1 of tree `3b2184a9`, an earlier tree of this change, with one edit each.
`controls/hmac-as-bug.md` removes the HMAC rule of Request 2 and proposes a Bug in its place; it fails checks 11 and 12.
`controls/tls-as-guarantee.md` removes the rule of Request 3, states the minimum version as a guarantee of Go's TLS
client, and calls the missing minimum a defect; it fails checks 13 and 14. `controls/context-without-source.md` cuts
Request 1's Context to two sentences that name no base image, while the record still names `/tmp/cert` in its
implementation notes; it fails check 8. `controls/fix-in-record.md` adds a follow-up that restores the entrypoint under
its own Bug; it fails check 9. `controls/wrong-number-and-guide.md` writes record 0007 as 0006 and adds a
`docs/adr/README.md`; it fails checks 1 and 15.

`controls/fix-exception-opus.md` is an unedited Opus run on tree `1db689e3`, where the Defect bullet let
**Implementation notes** name the fix for a rule that could be met only after it. The run used that exception: its R2
says that the HTTPS calls trust every certificate mounted under `/tmp/cert`, and its message says that R2 can be met
only after the Bug is fixed. It fails check 3, and checks 10 and 11 on the marker, since its Request 2 carries the HTTP
401 in the term "refuse". The exception was dropped, and the final tree has no such clause.

## Results

Runs of 2026-11-12 on tree `d8b52781`, graded by reading; both models at the default effort. "r1" and "r2" are
`result.md` and `result-2.md`. The case ran again on this tree because **One home** now leaves out a rule that other
rules imply, and the TLS rule of Request 3 is met by Go's default, which is no rule, so it has to stay. All four
results pass all fifteen checks, by the marker and by meaning. Each writes ADR-0007 with rules for the configuration,
the Compose example, and the CI job, and none on the entrypoint, the certificates, or the chart volumes. Each message
says that the platform's guide and the base image's README settle the entrypoint, and proposes a Bug for the replaced
entrypoint; each Context states, from the base image's README, what its entrypoint does with `/tmp/cert`. In Request 2,
all four refuse `none` and the HMAC algorithms in rules with HTTP 401, and in Request 3 all four write a rule for TLS
1.2 or later, though Go's default already meets it.

An earlier tree of this change, `ba170d99`, ran the case too and passed by meaning; `check.py` failed three of its
checks on the marker, and its results are not kept.

On tree `d42618eb`, before this change, all four results passed all fifteen checks by meaning as well; `check.py`
failed three of them on the marker.

Earlier trees of the change that added this case ran it too. On `89cbfb4e`, before Request 3, check 9, and the clause
that keeps the issue and the fix out of the record, two of four results named the pending fix in the record: Opus r2
under Follow-ups and Sonnet r2 in its implementation notes. On `3b2184a9`, all four passed by meaning. On `1db689e3`,
the exception that `controls/fix-exception-opus.md` shows brought the certificate rule back in one of four results.

The baselines ran on 2026-11-11 with `english-developer-style` alone. Neither record writes its rules as `R1`, so both
fail checks 10, 11, and 13, and neither proposes an issue, which fails checks 5 and 6. Both name the fix in the record
and fail check 9: Opus says that its rule 4 holds only if token-gate runs behind the base entrypoint, and Sonnet lists
switching to the base entrypoint as an option. By meaning both also fail checks 3 and 7: each states the `/tmp/cert`
trust as its rule 4 and offers the two entrypoints under an "Open question" heading. Sonnet's rule 5 requires the base
entrypoint, which fails check 2.
