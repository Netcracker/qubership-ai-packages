# Case: notes that restate the rules of other records

The input is two requests in one repository whose records are all accepted, with the text of six of their rules. The
notes of Request 1 decide which tokens are M2M tokens and what a token that is not M2M may reach. They also repeat
what other records already require: why a service account token is safe as an M2M token, by the `sub` prefix of
ADR-0004 R3 and the topology file of ADR-0004 R5; a second sentence for the tenant limit they have just stated; and an
outcome in the mode `legacy` that ADR-0004 R1 and ADR-0003 R4 already produce together. The skill states each
requirement once: the new record cites another rule by number without its values, writes no rule for the repeated
tenant limit or for `legacy`, and edits no accepted record.

Request 2 is the noise input. Its rule needs another record's rule, because the exception for `TOKEN_KEYS_UNAVAILABLE`
gets the response of ADR-0005 R2. The citation stays in the rule, and the record does not copy the status or the
header of that response.

The case comes from ADR-0092 R7 of Netcracker/qubership-authz-agent at commit `f6bb3f86`: "A Kubernetes token is an
M2M token. ADR-0094 R16 refuses one whose `sub` does not start with `system:serviceaccount`." When the prefix of
ADR-0094 R16 was questioned in
[Netcracker/qubership-authz-agent#248](https://github.com/Netcracker/qubership-authz-agent/issues/248), both rules had
to be read and fixed, though ADR-0092 R7 needs only its first sentence.

## Skill parts

- `SKILL.md`: "Rules" (**One home**: a rule cites another rule only where the citation changes what it requires; a
  citation of a rule of another record, in any section, says nothing of what that rule requires; a rule that other
  rules imply is left out), "Local conventions" (immutability: an accepted record is not edited)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Record 0007.** Request 1 writes `docs/adr/0007-<slug>.md`.
2. **Service account rule.** A rule of Request 1's record makes a service account token an M2M token.
3. **No pointer in the rule.** That rule names no rule of ADR-0004: the citation would change nothing it requires.
4. **No `sub` prefix.** No line of Request 1's record names `system:serviceaccount`.
5. **No namespace list.** No line of Request 1's record names the topology file.
6. **No provider rule.** No line of Request 1's record names the providers file, the condition of ADR-0004 R1.
7. **One tenant rule.** Exactly one rule of Request 1's record limits a token that is not M2M to its tenant.
8. **No `legacy` rule.** No rule of Request 1's record names `TOKEN_ISSUER_UNKNOWN` or the mode `legacy`.
9. **Other records untouched.** Request 1 writes no record other than 0007.
10. **Record 0007 in Request 2.** Request 2 writes `docs/adr/0007-<slug>.md`.
11. **Rule for the 401.** Request 2's record has a rule with HTTP 401.
12. **Exception cited.** A rule of Request 2's record names `TOKEN_KEYS_UNAVAILABLE` and `ADR-0005 R2`.
13. **No copied response.** No line of Request 2's record names `503` or `Retry-After`.
14. **No copied status.** No sentence of Request 2's record outside its rules names ADR-0003 R4 or ADR-0004 R3 together
    with `401`.
15. **No guide written.** No request writes a `README.md`: the repository has its guide.

## Running it

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/writer-one-home opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/writer-one-home
```

`check.py` marks every check; a PASS is a marker found, so read the result before recording a grade.

`controls/before-opus.md` and `controls/before-sonnet.md` are unedited runs of this prompt on the skill before this
change, commit `82565c6`, tree `d42618eb`, at the default effort: `research/adr-authoring/cases/run-case.sh <copy of
this case> <model> result 82565c6`. Both fail checks 4, 5, 6, 13, and 14, by the same sentences: the Context of Request
1 restates ADR-0004 R3 with its prefix, ADR-0004 R5 with the topology file, and ADR-0004 R1 with the providers file, and
the Context of Request 2 gives the HTTP 401 of ADR-0003 R4 and ADR-0004 R3 and the HTTP 503 and `Retry-After: 5` of
ADR-0005 R2. Opus also restates ADR-0004 R3 and R5 in the Justification of Request 1. Neither writes a rule that
restates another rule: both leave the `legacy` outcome and the second sentence on the tenant limit without a rule, and
both keep `ADR-0005 R2` in the exception of Request 2.

The other controls are the Opus r1 of tree `ba170d99`, an earlier tree of this change, with edits. That result already
fails check 14: its Context of Request 2 says that the issuer check of ADR-0003 R4 and the `sub` check of ADR-0004 R3
"state HTTP 401 and an error code". `controls/repeated-rules.md` adds to R2 the sentence "ADR-0004 R3 and ADR-0004 R5
limit which service account tokens pass verification", a rule that a token that is not M2M never reaches another
tenant, and a rule for the mode `legacy`; it fails checks 3, 7, 8, and 14. `controls/restated-citations.md` gives R2 of
Request 1 the second sentence of ADR-0092 R7, with the prefix of ADR-0004 R3, and replaces `the response of ADR-0005
R2` in Request 2 with HTTP 503 and `Retry-After: 5`; it fails checks 3, 4, 12, 13, and 14. `controls/wrong-files.md`
numbers both records 0008, adds a changed ADR-0004 to Request 1, and writes a guide in Request 2; it fails checks 1, 2,
3, 7, 9, 10, 11, 12, and 15.

## Results

Runs of 2026-11-12 on tree `d8b52781`, graded by reading; both models at the default effort. "r1" and "r2" are
`result.md` and `result-2.md`.

All four results pass checks 1 to 4, 7 to 13, and 15. Each writes the service account rule as one sentence, such as
"Every service account token in `Authorization` is an M2M token.", with no citation; writes one tenant rule and no rule
for the mode `legacy`; edits no accepted record; and keeps `ADR-0005 R2` in the exception of Request 2 without its
status. Each cites ADR-0004 R3 and R5 as "the `sub` check of ADR-0004 R3" and "the namespace check of ADR-0004 R5",
and none names the `sub` prefix or the HTTP 503.

Opus r1 passes all fifteen checks. Opus r2 fails check 5: a Negative consequence says that "an edit of the topology
file, which the namespace check of ADR-0004 R5 reads", decides which workloads act across tenants. Sonnet r1 and r2
fail check 5 with a Negative consequence on "a namespace that the topology file lists", and check 14: the Context of
Request 2 says that the checks of ADR-0003 R4 and ADR-0004 R3 give HTTP 401. By meaning Sonnet r2 also fails check 6,
though not on the marker: its Justification says that "the provider rule of ADR-0004 R1 leaves the mode `legacy`
without a provider".

The skill before this change fails five checks per run, and the copies left after it sit in a Negative consequence and
in Context, not in a rule. The Negative consequence on the topology file is a cost for an approver: whoever edits that
file decides which workloads reach every tenant, and three of four results name the file to say so, where the skill
keeps the source of the cited list in ADR-0004 R5.

Two earlier trees of this change ran the case; their results are not kept. On `6e5a051d`, which listed only "a value, a
prefix, a limit, or a list" as the conditions a citation does not copy, Opus r1 named the topology file in a Negative
consequence, and Sonnet r1 named it in the Justification after the right citation and restated ADR-0004 R1 in Context.
On `ba170d99`, before the edits that settle how a structural rule, a rule of the same record, and a replaced answer are
cited, Opus r1 failed check 14, Sonnet r1 check 5, and Sonnet r2 checks 13 and 14.

The baselines ran on 2026-11-12 with `english-developer-style` alone. Opus writes its rules as ``**R1 (`verify`).**``,
a shape the rule checks do not read, and Sonnet writes no numbered rules, so both fail checks 2, 3, 7, 11, and 12 on
the marker. Both restate ADR-0004 R1, R3, and R5, ADR-0003 R4, and ADR-0005 R2, which fails checks 4, 5, 6, 13, and 14.
Opus restates ADR-0005 R2 inside the exception rule of Request 2 as well: "gets the response that ADR-0005 R2 sets,
HTTP 503 with `Retry-After: 5`".
