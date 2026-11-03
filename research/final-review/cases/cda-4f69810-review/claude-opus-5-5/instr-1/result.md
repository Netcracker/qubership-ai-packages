# Final review of `d79c43d..4f69810`: one commit, "stop drafts from inventing symptoms and translating hunks"

There was no separate task statement, so I took the claimed cases from the commit message alone. The change has no code. It touches a skill, the package README and three version fields, so each item below says which §2a analogue it uses. I did not run `comment-drift.py` because the change is Markdown, YAML and JSON only, and the script has nothing to parse.

Skills loaded: `apm-authoring` and `english-developer-style` (from the given folder). `test-authoring` is not used for a change with no code.

## Item 1: comments consistent with the code and with each other

*Analogue: statements one file makes about another, and the worked examples.*

1. **The What-slot *After* example (SKILL.md:353–355) breaks the rule it illustrates.**
   - Its second sentence ends with "with the pool open from startup it sends directly". A reviewer gets that from one hunk (`execute` uses `sendDirect`). It sits under a lead-in that states a reason, which is exactly what :342–345 call translation: "even under a lead-in that states a reason … state the reason for the decision, not the edit that carries it".
   - Its first sentence says "a caller that runs before startup completes fails at once". That is a caller-visible outcome written in prose. :357–358 then send the same outcome to "User-visible changes", and :232 says "A fact stated in slot 3 is not restated in slot 2."
   - So the commit message's claim that the example "no longer puts an outcome in prose" is false.
   - The `apm-authoring` rule *One canonical example per concern* applies: an agent copies the example, not the rule.
2. **"Recovered from one hunk" (SKILL.md:342) can be read two ways.**
   - The What slot (:195) owes "the behavioral change". In a one-hunk fix, the sentence stating the behavioral change is also recoverable from that hunk.
   - One reading cuts the behavioral change itself. The other keeps any sentence worded at the caller's level. The *After*'s first sentence ("The pool opens at startup") passes only under the second reading.
3. **Rules conflict for a defect an audit found and that was later reproduced.**
   - :91–92 ("name what found it and end the sentence there"), the slot 2 skip cell (:81) and changelog part 3 (:475, "the condition alone") all fire on how the defect was found.
   - Slot 2's own first sentence (:90) and the Symptom checklist (:803–806, "quoted from an observation") ask for the observed diagnostic.
   - For an audit-found defect that a test or a user then reproduced, the changelog loses the literal that R3 greps for.
4. **The README contradicts the skill on derived consequences.** README:28–29 says an audit-found defect is described "with neither a predicted failure nor a claim that none was seen". SKILL.md:98–101 allows a consequence derived from the code once it is traced to the caller and marked as derived. Someone reading the README would expect a flat ban.

There are no narration words (`now`, `no longer`) in the added rules outside examples. The cross-references are correct: §7 (:762–764) points to the What slot, and changelog part 3 cites §2 slot 2.

## Item 2: claimed cases covered

*Analogue: each claim in the commit message against the section that handles it.*

| Claim in the commit message | Where the change handles it |
| --- | --- |
| Slot 2: name what found it, and end the sentence | :91–93, :81 |
| Changelog names the condition alone | :475 |
| A derived consequence must be traced and marked | :98–101 |
| "Say so" kept for a defect with no symptom by construction | :94–96 |
| What slot: one-hunk sentence is translation, even with a reason | :342–345 |
| A public identifier is named once | :345–347 |
| §7 points to the rule | :762–764 |
| §2 asks for "what changed that the diff does not show" | :288 |
| Rejected alternative stated as a fact about the merged code | :370–374 |
| Open questions: answered, kept in Scope, or dropped | :458–464, :199 |
| Checklist: Symptom, Alternatives, Discussion, Translation | :803, :832, :835, :826 |
| Bad and good examples for slot 2 and the What slot | :92–93, :349–355 |

- "Each fix … has a checklist item" is partly false. The public-identifier exception (:345) has no checklist item; Translation (:826) is the closest. Whether the changelog's "condition alone" (:475) is covered depends on reading the Symptom item's "the sentence" to include the changelog.
- **Hunks no sentence claims:**
  - The README hunk (README:26–32).
  - The 1.3.0 → 1.4.0 bump in `apm.yml`, the package `apm.yml` and `marketplace.json`. The three earlier commits on this package each state "Version 1.x.0 to 1.y.0"; this one does not.
- **Commands:** the change adds no command lines.
- "This skill has no cases under research/" holds: `research/change-description-authoring/` has phase notes and the classifier check, and no draft cases.

## Item 3: boundaries, partitions, and the negative control

*Analogue: the situations claimed, the control arm, and the table of added instructions.*

- **Partitions:**
  - The trials cover the four defect kinds the commit names.
  - Per the commit, two parts were not re-run: the current open-question rule (Scope placement) and the rewritten What-slot example. The partition "a question only a maintainer can settle" therefore has no evidence.
  - Hunk translation "persists in about one draft in two", so the rule is known not to fully hold.
- **Earlier state:** consumers on 1.3.0 receive a minor bump. No persisted state is involved.

Added instructions: 7, no rows.

Not findings: `:94`, `:98`, `:288`, `:345`, `:370`, `:458`.

The conflict at :91 is filed under item 1, finding 3.

## Item 3a: level, placement, and the environment

*Analogue: which file each rule lives in, and the repository's own gate.*

- Each rule sits in the section it governs: slot 2 rules under the commit body, the open-question rule under Scope, checklist items in §8.
- The gate passed: `make check` (exits 0), `scripts/check-skill-descriptions.py` ("all 27 skill descriptions are within 1020 characters") and `research/change-description-authoring/check-classifier-target-ref.sh` (all ok).
- No added sentence is generic tutorial material.

## Item 4: names by content, not by position

- SKILL.md:357–358 says "the first sentence says why they are no longer needed". It points at the *After* by position rather than content, e.g. "the startup sentence". This is taste.
- Section numbers (§2, §7, §8) are the file's own convention.

## Item 5: the failure report

*Analogue: does each detection detect its rule?*

- **Translation (:826)** is weaker than its rule. "Delete each sentence … where the diff still says it, leave it deleted" keeps any sentence that also carries a reason, because the diff does not state the reason. The rule (:343) targets exactly that case ("even under a lead-in that states a reason"), so the check passes the *After*'s second sentence.
- Symptom, Alternatives and Discussion each restate their rule and are reached from §8.

## Item 6: what the writer says it verified

- The commit states before and after counts for each defect: symptom 2/2 → 5/10 → 0/2, retold obstacle 2/4 → 0/4, open question 3/3 → 0/4. It also says honestly that the final open-question rule and the What-slot example were not re-run, and that drafts ran against 1.0.1.
- Not stated: a noise-case check. That would be an input where the added item does not apply (no open question in the discussion, a defect found from a user report), with a check that the description did not grow there.
- Not stated: re-applying the rewritten rule to its own *After* example. That check fails (item 1, finding 1).

## Item 7: siblings of the change

- The package README is updated.
- The `marketplace.json` and `apm.yml` descriptions are unchanged, and the scope was not widened, so they still route correctly. All three version fields agree at 1.4.0.
- `english-developer-style` §7 (commit messages and pull request descriptions) defers to this skill and does not conflict.
- `git grep` found no other skill with a symptom or "no failure observed" rule for audit-found defects; `problem-report-authoring` has none.
- No set gained a member.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| The What-slot *After* translates a hunk ("it sends directly") and puts an outcome in prose ("fails at once"), against :343 and :232. The commit message says otherwise. | Substantive | SKILL.md:353–355 | Rewrite the *After* to give only the reasons (pool opened at startup; sendWithRetry existed only to reopen) and leave the outcome to User-visible. Re-run drafts on it, or correct the commit message's claim. |
| "Recovered from one hunk" reads two ways for the behavioral change itself | Substantive | SKILL.md:342 | Add a clause, e.g. "a statement of the behavior at the caller's level is not translation". |
| Audit-found rules drop an observed diagnostic once the defect is reproduced | Substantive | SKILL.md:81, :91, :475 | Limit them to "… and no observation or reproduction shows a symptom". |
| The README bans a predicted failure outright, but the skill allows a traced, marked derivation | Substantive | README.md:28–29 | Say "with no predicted failure unless traced to the caller and marked as derived", or match the skill's wording. |
| The Translation check cannot catch a reason lead-in wrapped around a hunk | Substantive | SKILL.md:826 | Check clause by clause: "where a clause the diff says sits beside a reason, cut the clause and keep the reason". |
| The README hunk and the 1.3.0 → 1.4.0 bump are claimed by no sentence | Substantive | README.md:26; apm.yml:168; package apm.yml:2; marketplace.json:291 | Add "Version 1.3.0 to 1.4.0." and a line on the README summary, as the previous commits do. |
| No noise-case check for the added rules | Substantive | commit message | Report one input where each added item does not apply, and show that the output did not grow. |
| The public-identifier exception has no checklist item, though the commit says every fix has one | Substantive | SKILL.md:345, §8 | Add it to the Translation item, or narrow the commit's claim. |
| "The first sentence" is a positional reference | Taste | SKILL.md:357 | "The startup sentence". |

This review did not run any blind drafts against the rewritten rules, did not run the `make test` suite or the install smoke test (they need the network), and did not do a style-only pass over the prose.
