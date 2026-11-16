# Case: a new rule that wins over rules of two proposed records

The input is a repository with two `Proposed` records, ADR-0010 and ADR-0011, and two requests handled apart. Request 1
adds a record whose rule answers HTTP 503 with a new reason code where the policy store is unreachable, and names only
ADR-0010, whose R3 refuses the same request with HTTP 403. ADR-0011 R2 lists the reason codes as a closed set, so the
new code breaks it too, and the request does not say so. The skill searches the records for rules on the same case,
gives each losing rule of a `Proposed` record an exception in the same change, one that points at the new rule and holds
only while that rule binds, and tells the user which records it edited; it leaves no follow-up that waits for
acceptance. Request 2 adds a record about the configuration file, which decides a case no other record decides: it is
the noise input for the search and the edits.

The case reproduces the output that version 2.2.0 of the skill fixes: a new rule that took precedence over rules of two
`Proposed` records, with the amendment of each left as a follow-up "when this rule is accepted", and one of the two not
found at all.

## Skill parts

- `SKILL.md`: "Rules" (**Precedence**, **Exceptions**), "Consequences" (**Follow-ups**), "What belongs in an ADR" (a
  part that changes what an earlier record decided)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **New rule.** Request 1 writes `docs/adr/0012-<slug>.md` with a rule that carries `503` and
   `POLICY_STORE_UNAVAILABLE`.
2. **Named loser excepted.** Request 1 gives ADR-0010 with an R3 whose exception points at a rule of ADR-0012 by
   number, and holds only while that rule binds. The snippet checks the rule number; read the result for the
   condition.
3. **Unnamed loser found.** Request 1 gives ADR-0011 with an R2 that gives way only where a rule of ADR-0012 applies,
   pointed at by number: an exception for the response that rule requires, or `POLICY_STORE_UNAVAILABLE` in a clause
   that points at it. A plain member of the closed list fails: it would stay allowed for any error if ADR-0012 were
   rejected. The snippet checks that every sentence naming the code points at ADR-0012 near it; read the result for
   whether the code stays out of the list's other members, and for the condition that the exception holds only while
   the rule binds.
4. **No follow-up for acceptance.** No follow-up of record 0012 in Request 1 defers an edit of ADR-0010 or ADR-0011,
   named or not. The snippet checks for the two numbers; read the Follow-ups for an unnamed deferral, such as "add the
   new code to the reason-code record when this one is accepted". A follow-up about other work, such as telling
   clients, passes.
5. **User told.** Request 1's message names ADR-0010 R3 and ADR-0011 R2 as edited. The snippet checks the two names;
   read the message for whether it says that each was edited.
6. **Noise: one record.** Request 2 writes record 0012 and no other record.
7. **Noise: no follow-up.** Record 0012 of Request 2 has no follow-up that names ADR-0010 or ADR-0011.
8. **No guide written.** Neither request writes a `README.md`.

## Running it

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/writer-proposed-precedence opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/writer-proposed-precedence
```

`check.py` marks every check; a PASS is a marker found, so read the result before recording a grade.

`controls/base-tree.md` and `controls/base-tree-sonnet.md` are runs of the same prompt on tree `d42618eb`, the skill
before the change that added this case, by Opus and Sonnet.

## Results

Runs of 2026-11-24 on tree `4eb880be`, graded by reading; both models at the default effort. "r1" and "r2" are
`result.md` and `result-2.md`. All four results pass all eight checks. Each Request 1 writes a `Proposed` ADR-0012 with
a 503 rule, gives ADR-0010 R3 and ADR-0011 R2 an exception that points at that rule and holds, by its own wording, only
while that rule binds, and names both edits in the message. No follow-up defers an edit of ADR-0010 or ADR-0011; Opus r1
has one follow-up, to tell the clients that branch on `reason` about the new code, and the other three have none. Each
Request 2 writes ADR-0012 alone and edits no other record.

No check grades the Decision sentence of ADR-0011, "a reason code from one closed list", which the item for a `Proposed`
record asks the writer to correct where the exception makes it false. The results split on whether it does: both Opus
results keep the sentence and say in the message that it still holds, Sonnet r1 adds "ADR-0012 adds one code to it"
without the binding condition, and Sonnet r2 changes "one closed list" to "a closed set".

The skill changed after these runs, to tree `1325f38e`, in four places. In the item of **The reading guide** on which
statuses bind and in step 4 of **Checking a change**, a sentence that made a `Proposed` rule winning over an accepted
rule bind nothing was taken out again; the case writes no guide and checks no checker, so neither text is on the path
from its input to a check. In **Precedence**, the sentence that gave every losing rule an exception now says that a
rule of an accepted record gives way by a replacement instead; what it asks of a rule of a `Proposed` record, the only
kind the case's input has, is unchanged, and so is the sentence on the exception's binding condition. In
`references/structural-invariant.md`, a clause moved from the follow-up to Context; the case does not read that
example. The results stand for the new tree.

Three earlier trees of this change ran the case four times each; those results are not kept. On `9ce9fe46`, where the
losing rule only had to "point at the winning rule", all four results added `POLICY_STORE_UNAVAILABLE` to the closed
list of ADR-0011 R2 as a plain member and failed check 3. On `7ff5c4cb`, where the exception "says that it holds only
while the winning rule binds", Sonnet r1 wrote the condition with the whole rule as its subject ("This does not apply to
a request that ADR-0012 R1 covers, and holds only while ADR-0012 R1 binds the change") and failed check 2 by reading. On
`a91c6550`, before the item for a `Proposed` record asked for the Decision sentence to be corrected, all four results
passed all eight checks.

On tree `d42618eb`, the skill before this change, Opus fails checks 2 and 3: its ADR-0010 R3 exception, "except where
ADR-0012 R1 applies", has no binding condition, and it adds the new code to ADR-0011 R2 as a plain member. Sonnet fails
checks 2, 3, 4, and 5: it leaves ADR-0010 and ADR-0011 as they are, states the exception and the new code in ADR-0012
alone, and adds a follow-up that the owner of ADR-0011 decides whether R2 is amended. One run each, so the controls show
the failure the change addresses, not its rate.
