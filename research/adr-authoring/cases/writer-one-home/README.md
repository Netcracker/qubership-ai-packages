# Case: notes that restate the rules of other records

The input is two requests in one repository whose records are all accepted, with the text of six of their rules and
of one rule of a record in another repository, example/platform ADR-0012 R3. The notes of Request 1 decide which
tokens are M2M tokens and what a token that is not M2M may reach. They also repeat what other records already require:
why a service account token is safe as an M2M token, by the `sub` prefix of ADR-0004 R3, the topology file of ADR-0004
R5, and the audience of example/platform ADR-0012 R3; a second sentence for the tenant limit they have just stated;
and an outcome in the mode `legacy` that ADR-0004 R1 and ADR-0003 R4 already produce together. The skill states each
requirement once: the new record cites another rule by number and by what it is about, in every section, names the
other repository's record as `example/platform ADR-0012`, writes no rule for the repeated tenant limit or for `legacy`,
and edits no accepted record.

Request 2 is the noise input. Its rule gives every failed check HTTP 401 and excepts `TOKEN_KEYS_UNAVAILABLE`, whose
response ADR-0005 R2 gives. The rule keeps the exception, with the citation of ADR-0005 R2 or by the code alone, and
the record does not copy the status or the header of that response.

The case comes from ADR-0092 R7 of Netcracker/qubership-authz-agent at commit `f6bb3f86`: "A Kubernetes token is an
M2M token. ADR-0094 R16 refuses one whose `sub` does not start with `system:serviceaccount`." When the prefix of
ADR-0094 R16 was questioned in
[Netcracker/qubership-authz-agent#248](https://github.com/Netcracker/qubership-authz-agent/issues/248), both rules had
to be read and fixed, though ADR-0092 R7 needs only its first sentence.

## Skill parts

- `SKILL.md`: "What belongs in an ADR" (a guarantee is stated in Context only where its source is not a decision
  record; a decision record is cited), "Template" (the Context placeholder), "Rules" (**One home**: a
  citation of a rule of another record names what the rule is about, not what it decides, in every section; **No
  pointer rules**: a rule that only repeats a requirement of another rule is left out; **Cite only what the reader
  needs**; **Numbers freeze**: a rule of another repository as `owner/repo ADR-NNNN Rn`, and **Related ADRs** holds the
  records the text cites), "Drafting from the user's input" (the read before publishing), "Local conventions"
  (immutability: an accepted record is not edited)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Record 0007.** Request 1 writes `docs/adr/0007-<slug>.md`.
2. **Service account rule.** A rule of Request 1's record makes a service account token an M2M token.
3. **No pointer in the rule.** That rule names no rule of ADR-0004: the citation would change nothing it requires.
4. **No `sub` prefix.** No line of Request 1's record names `system:serviceaccount`.
5. **No namespace list.** No line of Request 1's record names the topology file.
6. **No provider rule.** No line of Request 1's record states what ADR-0004 R1 decides, alone or with ADR-0003 R4: the
   providers file of a mode, or what a service account token gets in the mode `legacy`. The marker reads only the
   providers file and a mode without a provider.
7. **One tenant rule.** Exactly one rule of Request 1's record limits a token that is not M2M to its tenant.
8. **No `legacy` rule.** No rule of Request 1's record names `TOKEN_ISSUER_UNKNOWN` or the mode `legacy`.
9. **Other records untouched.** Request 1 writes no record other than 0007.
10. **Record 0007 in Request 2.** Request 2 writes `docs/adr/0007-<slug>.md`.
11. **Rule for the 401.** Request 2's record has a rule with HTTP 401.
12. **Exception kept.** A rule of Request 2's record gives HTTP 401 and excepts `TOKEN_KEYS_UNAVAILABLE`, citing
    ADR-0005 R2 for that response or not. The marker reads HTTP 401 and the code in one rule, and not whether or which
    way the rule excepts the code: its evidence names the rule with a word that excepts, such as "except", "instead of",
    or "does not cover", or says that it found none, and the exception is graded by reading. Both controls that reverse
    the exception pass the marker.
13. **No copied response.** No line of Request 2's record names `503` or `Retry-After`.
14. **No copied status.** No sentence of Request 2's record outside its rules says what ADR-0003 R4 or ADR-0004 R3
    decides, the HTTP 401 or the code it gives. The marker reads a sentence that names one of those rules with `401`,
    inside one paragraph, list item, or heading, so its FAIL is a possible copy, graded by reading.
15. **Cited records listed.** **Related ADRs** of a record 0007 lists every record that the rest of the record cites, in
    both requests, linked where the writer knows the file. The marker reads only links, so a list without links passes
    by reading where it names every cited record.
16. **No guide written.** No request writes a `README.md`: the repository has its guide.
17. **Another repository named.** Every mention of ADR-0012 in a record 0007 has the form `example/platform ADR-0012`,
    or is the link of a line under **Related ADRs** to example/platform: a URL that leads to that repository, or one
    that names no repository under a link text that names it. The marker reads the repository of a URL on github.com
    or gitlab.com; any other URL, a GitHub Pages site included, names none. A record that cites ADR-0012 nowhere
    passes.
18. **No audience.** No line of Request 1's record says that example/platform ADR-0012 R3 gives the audience
    `netcracker`. An open point whose answers name `netcracker` as a requirement this record might add passes by
    reading; the marker reads any line that names `netcracker`.
19. **No citation that only points.** No sentence of a record 0007 cites a rule of another record only to point at it or
    to say that it still applies, such as "See also the issuer check of ADR-0003 R4." or "The statuses of ADR-0003 R4
    and ADR-0004 R3 stay the same." A citation that is part of a reason, gives an example of a check, names the subject
    of an open point, or names the rule a follow-up changes passes. The marker reads a citation that "see", "see also",
    "cf.", or "compare" introduces outside **Related ADRs**, so its FAIL is a possible pointer, graded by reading, and a
    pointer in other words, such as a reminder, passes the marker and fails by reading.

## Running it

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/writer-one-home opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/writer-one-home
```

`check.py` marks every check; a PASS is a marker found, so read the result before recording a grade.

`controls/before-opus.md`, `before-opus-2.md`, `before-sonnet.md`, and `before-sonnet-2.md` are unedited runs of this
prompt on 2026-11-25 on the skill before this change, commit `8d5f4c3`, tree `d42618eb`, at the default effort:
`research/adr-authoring/cases/run-case.sh <copy of this case> <model> result 8d5f4c3`. Graded by reading, each fails
checks 4, 5, 6, 13, 14, 17, and 18, Opus r2 also check 15, and Sonnet r1 also check 19, for the Negative consequence
"Their results do not change." about ADR-0003 R4 and ADR-0004 R3, a reminder that `check.py` does not read. Each Context
or Justification of Request 1 restates the `sub` prefix of ADR-0004 R3, the topology file of ADR-0004 R5, what ADR-0004
R1 leaves in the mode `legacy`, and the audience `netcracker` of example/platform ADR-0012 R3, which each writes as
`ADR-0012 R3 of example/platform`; each Context of Request 2 gives the HTTP 401 of ADR-0003 R4 and ADR-0004 R3 and the
HTTP 503 and `Retry-After: 5` of ADR-0005 R2. Opus r2 leaves example/platform ADR-0012 out of **Related ADRs**.
`check.py` also fails Opus r1 on check 7, whose marker does not read its tenant rule, Sonnet r2 on check 12, whose
marker does not read an exception that a second rule makes, and Sonnet r1 and r2 on check 15, whose lines under
**Related ADRs** have no links but name every cited record.

`controls/repeated-rules.md`, `controls/restated-citations.md`, and `controls/wrong-files.md` are the Opus r1 of tree
`ba170d99`, an earlier tree of this change, with edits; they answer the prompt before the audience of example/platform
ADR-0012 R3 was added, so checks 17 and 18 find nothing to read in them. That result already fails check 14: its Context
of Request 2 says that the issuer check of ADR-0003 R4 and the `sub` check of ADR-0004 R3 "state HTTP 401 and an error
code". `controls/repeated-rules.md` adds to R2 the sentence "ADR-0004 R3 and ADR-0004 R5 limit which service account
tokens pass verification", a rule that a token that is not M2M never reaches another tenant, and a rule for the mode
`legacy`; it fails checks 3, 6, 7, 8, and 14. `controls/restated-citations.md` gives R2 of Request 1 the second sentence
of ADR-0092 R7, with the prefix of ADR-0004 R3, and replaces `the response of ADR-0005 R2` in Request 2 with HTTP 503
and `Retry-After: 5`; it fails checks 3, 4, 6, 13, and 14. `controls/wrong-files.md` numbers both records 0008, adds a
changed ADR-0004 to Request 1, and writes a guide in Request 2; it fails checks 1, 2, 3, 7, 9, 10, 11, 12, and 16. Each
Context of these controls states the outcome in the mode `legacy` "through the providers rule of ADR-0004 R1 and the
issuer check of ADR-0003 R4", which check 6 grades and its marker does not read, so `check.py` passes the first two on
check 6; the third has no record 0007.

`controls/see-also.md`, `controls/needed-citation.md`, `controls/reversed-exception.md`, and
`controls/reversed-exception-worded.md` are the Opus r1 of tree `88a72faf`, which fails check 5, with one edit each.
`see-also.md` adds "See also the issuer check of ADR-0003 R4." to the Justification of Request 2 and fails check 19 as
well. `needed-citation.md` adds there instead "R2 names no response for unavailable keys and leaves it to the
unavailable-keys rule of ADR-0005 R2, so that a change of that response changes one record.", which tells the approver
why R2 cites that rule, and passes check 19. `reversed-exception.md` replaces the exception of R2 with "A token that
gets `TOKEN_KEYS_UNAVAILABLE` gets HTTP 401 as well.", and `reversed-exception-worded.md` with "A token that gets
`TOKEN_KEYS_UNAVAILABLE` gets HTTP 401 instead of the response of ADR-0005 R2."; both fail check 12 by reading.
`check.py` passes both, with "no word that excepts" in the evidence of the first and "instead of" in that of the second.
`check.py` also fails all four on check 18, as it fails that result (see Results). No other control cites a rule only to
point at it, so each passes check 19.

## Results

Runs of 2026-11-25 on tree `88a72faf`, graded by reading; both models at the default effort. "r1" and "r2" are
`result.md` and `result-2.md`. The case ran again on this tree because **One home** now asks for a citation of a rule of
another record by what the rule is about, in every section, the read before publishing covers every sentence that cites
a rule, **No pointer rules** leaves out a rule that only repeats a requirement of another rule, and the guarantee clause
of this tree states a guarantee in Context only where its source has no rules (the final tree, `dc50203b`, asks instead
whether the source is a decision record; see below); the prompt gained the audience of example/platform ADR-0012 R3,
with checks 17 and 18. Check 19 was added after these runs and graded on the same results; the results of the earlier
trees below were not graded on it.

Opus r1 and Opus r2 fail check 5, Sonnet r1 check 6, and Sonnet r2 checks 4, 5, 6, and 18: 7 failures in four runs,
against 30 for the same prompt on the skill before this change. Each Request 1 writes the service account rule as one
sentence with no citation, one tenant rule, and no rule for `legacy`, names the other repository's record with its
repository, and links every cited record under **Related ADRs**. The copies that remain: Opus r1 and Opus r2 name the
topology file of ADR-0004 R5 in a Negative consequence or the Justification; Sonnet r1 says in a Negative consequence
that the mode `legacy` has no provider of service account tokens (ADR-0004 R1); and Sonnet r2's Justification restates
the `sub` prefix of ADR-0004 R3, the topology file, and the audience `netcracker`, and its Implementation notes the
outcome in the mode `legacy`. No result cites a rule only to point at it: each citation outside the rules gives part of
a reason, an example of a check, or the subject of an open point, so all four pass check 19. All four write Request 2
and keep the exception for a token that gets only `TOKEN_KEYS_UNAVAILABLE`, and none copies the HTTP 401 of the cited
checks or the response of ADR-0005 R2. No run settles a token that also fails another check: Opus r1 gives it HTTP 401
in R3 and Opus r2 the response of the first check that fails in R4, each with the alternative or the order left to the
architect in O2, and Sonnet r1 (O1) and Sonnet r2 (O2) leave open which code such a token gets. Opus r2 also leaves the
checks of ADR-0003 R4 and ADR-0004 R3 out of its rule for every failed check, "because those rules set their own
response": it reads **One home** as forbidding a general rule to state a status that another record's rule already
gives. No check reads it; check 12 passes, since the rule still gives HTTP 401 and excepts `TOKEN_KEYS_UNAVAILABLE`. How
a general rule relates to the rules of other records that already decide part of its outcome is one of the shapes
Netcracker/qubership-ai-packages#284 takes. Opus r1 and Opus r2 also write a rule that gives the refusal of the
namespace check of ADR-0004 R5 a code of its own, a placeholder; how a record changes what an accepted rule of another
record leaves open is the question of
[Netcracker/qubership-ai-packages#278](https://github.com/Netcracker/qubership-ai-packages/issues/278), and no check of
this case reads it.

Tree `dc50203b` differs from `88a72faf` only in the guarantee clause, which it keys on whether the source is a decision
record rather than on whether the source has rules. The guarantee in the notes of this case comes from example/platform
ADR-0012 R3, a decision record with numbered rules, which both trees send to the citation, so the results above stand
for that tree.

`check.py` disagrees with these grades in three places: it fails Opus r1, Opus r2, and Sonnet r1 on check 18 for an
open point whose answers name the audience `netcracker` as a requirement this record might add, and which cites
ADR-0012 R3 by what it is about. A value that a proposed requirement names is no copy.

Two trees of the same day ran this prompt before, and this commit replaces their results. On `ad64edef`, whose guarantee
clause read "state it in Context as a fact, with its source; where the source is a rule of a decision record, cite that
rule instead", the four results failed 9 checks: each named the topology file and the outcome in the mode `legacy`, two
of them in Context, and Sonnet r2 restated the audience. On `3b37f1b0`, which said "a rule that repeats" without "only",
they failed 9 as well: the topology file in each, the audience in Sonnet r1, Opus r2's Context saying that service
account tokens reach token-gate only in the mode `k8s` "(the provider count of ADR-0004 R1)", and Sonnet r2 writing no
record for Request 2, saying that the accepted records already settle it. **One home** forbids such a copy where the
sentence cites the one rule it restates, and the topology file and the audience still appear in that form; a sentence
that states what several rules produce together or what another record decides without citing it, which no text of this
change names, goes with them to Netcracker/qubership-ai-packages#284.

On `ce37d0b5`, the tree this change had before the review of 2026-11-24 narrowed it to citation, the prompt had no
audience, and four results failed 14 checks, all of them copies in Context, the Justification, and Negative consequences
(checks 4, 5, 6, 13, and 14). Across the earlier trees of this change the case failed 8 checks in four runs on
`b7a46b78` and 11 on `0b92dea7`; a variant of `0b92dea7` that added "Context and Justification included" to **One
home**, tree `959b7842`, also failed 11 checks, and its results are not kept.

Five earlier trees of this change ran the case too; their results are not kept. On `6e5a051d`, which listed only "a
value, a prefix, a limit, or a list" as the conditions a citation does not copy, Opus r1 named the topology file in a
Negative consequence, and Sonnet r1 named it in the Justification after the right citation and restated ADR-0004 R1 in
Context. On `ba170d99`, Opus r1 failed check 14, Sonnet r1 check 5, and Sonnet r2 checks 13 and 14. On `d8b52781`, Opus
r1 passed every check, Opus r2 failed checks 5 and 15, and Sonnet r1 and r2 failed checks 5 and 14. On `b7a46b78`, Opus
r1 and r2 failed check 5, Sonnet r1 check 15, and Sonnet r2 checks 5, 6, 13, 14, and 15. On `0b92dea7`, Opus r1 and r2
failed checks 5 and 6, Sonnet r1 checks 6, 14, and 15, and Sonnet r2 checks 4, 5, 13, and 14: Sonnet r1's **Related
ADRs** linked ADR-0003, which Request 1 did not cite, and Sonnet r2's Justification wrote the sentence of ADR-0092 R7
that this case was built from.

The baselines ran on 2026-11-12 with `english-developer-style` alone, on the prompt without the audience; checks 17 and
18 find nothing to read in them. Opus writes its rules as ``**R1 (`verify`).**``, a shape the rule checks do not read,
and Sonnet writes no numbered rules, so both fail checks 2, 3, 7, 11, and 12 on the marker. Both restate ADR-0004 R1,
R3, and R5, ADR-0003 R4, and ADR-0005 R2, which fails checks 4, 5, 6, 13, and 14, and neither links the records it cites
under **Related ADRs**, which fails check 15. Opus restates ADR-0005 R2 inside the exception rule of Request 2 as well:
"gets the response that ADR-0005 R2 sets, HTTP 503 with `Retry-After: 5`". Opus also fails check 19 by reading, with the
Negative consequence "The statuses of ADR-0003 R4, ADR-0004 R3, and ADR-0005 R2 stay the same.", which the marker does
not read; Sonnet passes it.
