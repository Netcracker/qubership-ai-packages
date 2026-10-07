# Is the spec "proven"?

**No.** All three numbers measure the spec against itself, or against inputs the team already picked. None of them
measures the spec against legacy behaviour nobody has asked about yet, and that unasked behaviour is where a port
breaks. Testing can't prove two systems equivalent. What you can earn is a bounded, stated confidence. Right now the
bound only covers the inputs you recorded.

## What each number actually shows

| Claim | What it shows | What it doesn't show |
| --- | --- | --- |
| Matches 5,000 goldens | The spec agrees with legacy on those 5,000 inputs. If the spec was tuned until it matched them, this is a training score, not a validation score. | Anything about inputs outside the recording's distribution. Recorded traffic is mostly common cases, while legacy defects and odd behaviour sit in rare ones. Even if the samples were independent and random, 0 failures in 5,000 only bounds the error rate at about 0.06% (95%, rule of three) *for that same traffic mix*. It says nothing about rare inputs. |
| 98% mutation score over config knobs | Your goldens are sensitive: changing a knob in the spec usually breaks a golden. | (a) Whether the spec is *right*. Mutation testing grades the test suite, not the model. (b) Faults in the rule logic. Knob mutations don't flip `<` to `<=`, drop a condition, reorder rule precedence, or change a default branch. (c) The other 2%. Each survivor is either an equivalent mutant or a place where the goldens can't tell two different behaviours apart. That second kind is exactly a question you haven't asked legacy yet. |
| Pairwise coverage complete over 14 dimensions | Every pair of value classes in **the spec's own model** of the input space occurs in some test. | (a) Inputs legacy depends on that the spec has no dimension for (see below). (b) Value classes that are too coarse, e.g. legacy treats two roles differently that the spec puts in one class. (c) Interactions of 3 or more factors. Authorization rules are usually conjunctions like "role ∧ resource-type ∧ ownership", and pairwise coverage doesn't promise to hit those. (d) Whether the covering tests carry a **legacy-observed** expected value. If the pairs are covered by tests whose expected value came from the spec, the spec is grading itself. |

The common flaw: all three use the spec's own frame (its dimensions, its knobs, its partitions) or reuse the same
5,000 recorded inputs. Behaviour that is outside the spec's model can't be seen by any metric built from that model.

## What's specifically missing

1. **Hidden inputs.** Legacy may read things the spec doesn't model: clock, timezone and DST, locale, case and Unicode
   normalisation, header or field order, caller identity, caching and session history, rule or config version,
   backing data that changes over time. Test for this by sending the *same* request again at different times, in a
   different order, and after state changes. Any difference in the answer is a dimension the spec lacks.
2. **Boundaries and malformed input.** Thresholds and their neighbours, empty vs. missing vs. null fields, duplicate
   keys, very large values, invalid encodings, unknown enum values. Also the error paths: which error code comes
   back, and whether the service fails open or closed.
3. **Full output comparison.** Make sure goldens compare the whole response (reason codes, obligations, headers,
   audit or side effects, timeout behaviour), not just allow/deny.
4. **History and state.** Sequences like grant→revoke→check, or concurrent updates, if legacy has state at all.
5. **Interactions of 3+ factors** for the dimensions that appear together in rule conditions.
6. **Stand fidelity.** Check that the legacy stand runs the same version, config and data as production. A spec that
   perfectly matches a stand that has drifted from production is still wrong.
7. **Held-out evidence.** Right now nothing shows the spec generalises beyond the data it was fitted to.

## What I'd add

Each of these turns a doubt into concrete questions for the stand. That's the reason **not** to stop asking it yet.

1. **Resolve every surviving mutant.** For each survivor, build an input where the mutant and the spec disagree and
   ask legacy for the answer. Then it's either a new golden or an equivalent mutant with a documented reason. Never
   leave a survivor as "covered".
2. **Mutate the rule logic, not only the knobs.** Use relational and boundary operators, condition removal, negation,
   rule-order or precedence swaps, and default-branch changes. Treat each survivor as in step 1.
3. **Differential testing on fresh, spec-blind inputs.** Generate inputs with a property-based or grammar-based
   generator that ignores the spec's partitions, weighted toward boundaries and malformed data. Send each to both
   systems and diff the full responses. Shrink every disagreement and keep it as a named golden.
4. **Query by disagreement.** Wherever the spec had to guess (ambiguous docs, choices between alternatives), keep the
   alternatives as variants and query legacy only on inputs where the variants disagree. This gets the most
   information per question.
5. **3-way covering arrays** over the dimensions that interact in rule conditions, with legacy-observed expected values.
6. **Hidden-input probes:** repeated, reordered, time-shifted and state-shifted copies of the same request (item 1 above).
7. **A held-out set.** Freeze the spec, record a new batch of goldens from *recent production* traffic, and report
   agreement on that batch. This is the honest version of the "5,000" number.
8. **Legacy-side coverage, if possible.** If you can instrument legacy, or it returns rule IDs, logs or reason codes,
   list the legacy rules or branches the goldens never trigger. Those are your blind spots, seen from legacy's side
   rather than the spec's.
9. **Shadow mode before cutover.** Run the spec next to legacy on live traffic, log every divergence, and treat each
   one as a bug in the spec or as a documented intentional difference. This is the strongest evidence you can
   collect, because it covers the real input distribution, including its tail.

## A stopping rule worth agreeing with the lead

Stop *routinely* asking the stand when all of these hold, rather than when it feels "proven":

- every surviving mutant (knob and logic) is resolved by a legacy answer or documented as equivalent;
- N fresh spec-blind differential inputs (pick N, e.g. 10k+, split across generators) produce zero unexplained
  disagreements;
- the held-out production batch agrees at the target rate;
- hidden-input probes show legacy is deterministic in every dimension the spec ignores, or the spec models them;
- shadow-mode divergence stays below an agreed threshold for an agreed period, covering at least one full business
  cycle (month-end, DST change, config release).

Even then, keep the stand available for questions. Every future spec change, and every disagreement found in
production, will raise a question that only legacy can answer.
