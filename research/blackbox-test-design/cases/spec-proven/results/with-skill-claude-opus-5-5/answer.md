# Is the executable spec "proven"?

**No.** All three numbers are real, but they share one weakness. Each one measures the spec **against itself**, or
against inputs somebody already thought to record. None of them can show a rule the spec does not have. "Proven" means
"no input exists on which the spec and the legacy service disagree", and none of the three numbers supports that
claim. Stopping questions to the legacy stand now would freeze the spec's blind spots into the replacement.

For an authorization-like service this matters more than usual. A wrong "allow" is the costly kind of error, and it
tends to sit in exactly the places these measures cannot see: evaluation order, how a failure is handled, odd spellings
of identities, and duplicate rules.

## What each number actually shows

| Claim | What it shows | What it cannot show |
| --- | --- | --- |
| Matches all 5,000 goldens | The spec agrees with the service on those 5,000 inputs, **as the comparator sees them** | Anything outside the recorded inputs. Anything the comparator normalizes away (order, null versus absent, error detail). Whether the goldens came from the build that runs today |
| 98% mutation score over config knobs | For almost every alternative value **someone listed** for each knob, some golden tells it apart | Alternatives nobody listed, and above all **missing knobs**: a rule the spec lacks has no mutant. The surviving 2% are alternatives no golden rules out, which makes them open questions, not noise |
| Complete pairwise coverage over 14 dimensions | Every pair of values of the spec's **own** 14 concepts shows up in some case | Features that are not among the 14: the position of a rule, the order of entries, the outcome of a sibling rule, duplicate names, how a value is spelled. A pair also counts as "covered" when the **spec says** a case reaches it, which is circular |

The 5,000 goldens also do not give a statistical bound. "n random agreements bound the disagreement rate at about
3/n" holds only when the inputs are independent draws from a stated distribution. Goldens are usually captured from
whatever traffic or scenarios came to hand, so they say little about the input space as a whole, and nothing about
inputs nobody sends today.

A quick self-check for your team: look at the last ten fixes to the spec. If most of them **added a new rule or
decision**, rather than changing the value of a knob that already existed, then the mutation and pairwise measures
could not have predicted those bugs. The same will hold for the next ones.

## What is missing, concretely

1. **A provenance list of decisions.** For each place where the service could have behaved more than one way: the
   choice the spec made, and the golden that forces it, or "inferred" if none does. Decisions pinned by one golden or
   by none are guesses, and they are where to start asking.
2. **Oracle strength.**
   - Audit the comparator. Feed it pairs of responses that differ in one detail each (order, null versus missing, case,
     whitespace, error code versus message) and record which pairs it treats as equal. No golden can pin a spec
     decision whose alternatives differ only inside one of those merged classes.
   - Check that the goldens tell apart outcomes that look the same in the verdict: "rule denied", "rule did not apply",
     and "rule errored and was skipped" can all come out as the same final deny or allow. Each probe needs a context
     that separates them, such as a fallback rule or a sibling whose effect depends on whether evaluation reached it.
   - Record every side channel the stand offers: error text, trace or debug logs, which dependencies were called.
3. **Evaluation order and laziness.** Use sentinels (a dependency or attribute lookup that logs the call and changes
   nothing) and poisons (one that fails, or a reference to something absent) at each position: each rule, each
   condition operand, each list element, each pipeline stage. Then ask: is this position evaluated at all? In what
   order? When two positions fail, which failure decides the answer: fail-open or fail-closed, first error or last?
   "Error in rule 3 while rule 1 already decided" is a classic place where a spec and a legacy service disagree on
   allow versus deny.
4. **Structural metamorphic relations.** The relation itself is the oracle, so you need no expected value:
   - reorder rules, policy entries, and list items (first-match versus all-match versus last-wins);
   - add a rule that never applies, before and after the existing ones;
   - split an `A or B` rule into two rules, or merge two rules into one;
   - wrap a condition in a group of one, or flatten such a group;
   - move a setting to another level where the documentation says it means the same thing;
   - cross-endpoint checks: a batch call versus single calls, a "list what I can access" call versus individual checks.

   Add a negative control: deliberately break the spec's composition (reverse one order) and check that the relation
   suite catches it.
5. **Identity collisions.** Two rules, roles, or groups with the same name in one configuration. The same id reused
   across tenants or scopes. One identity in two spellings: case, surrounding whitespace, leading zeros, Unicode case
   folding. A service built on a map keeps either the first or the last entry; one built on a list keeps both. Your
   spec probably never had to decide, which makes this a prime source of privilege escalation.
6. **Platform idioms at each handling point.** Find out what the legacy service runs on (JVM, .NET, and so on). At
   each place where it trims, splits, compares case-insensitively, parses numbers or dates, binds JSON, or matches a
   pattern, list the common behaviors of that platform as standing hypotheses next to the one your Python spec uses.
   Python's `str.strip()`, `lower()`, `int()` and `re` all behave differently from Java's `trim()`,
   `toLowerCase(Locale)`, `Integer.parseInt` and `matches()` on edge input.
7. **Representation boundaries.** For every field, build a state matrix from the input format, not from the spec:
   absent, `null`, `""`, blank (space, tab, NBSP, and other whitespace), the value with padding, the value as another
   JSON type (number versus string, scalar versus one-element list), plus leading zeros, exponents, very long values,
   and non-ASCII case mappings. Ask in **opposite pairs**, two spellings of the same value in the same position, so
   that any difference is a finding.
8. **Combinatorial coverage over raw input features.** Use factors that can be computed without running the spec:
   the number of rules, a rule's position among its siblings, the kinds of its neighbors, nesting depth, which fields
   are present, caller and tenant shape, and **an order index**. Cover pairs, plus triples that involve order or
   sibling kind. Then list the cases the 14-dimension measure calls covered but the raw measure does not. Those are
   places where the spec merges inputs the service may treat differently.
9. **Hand-written exception lists.** Collect every `if x in (…)` and every special-case table in the spec. Several such
   lists are usually the footprints of one mechanism (a phase, a conversion, an order). Propose general rules that fit
   all 5,000 goldens but predict more exceptions than the lists do, and ask the question that tells each rule apart
   from the list.
10. **State and sequences.** Caches, sessions, revocation, role changes taking effect, retries, re-uploading a
    configuration. No single-request golden can show these. Ask short sequences instead: grant, check, revoke, check.
11. **The version of the reference.** Record which legacy build produced each golden. A contradiction you find later
    has to be told apart from a spec bug.
12. **An independent second model.** Have someone build a second spec, ideally in a separate session or by another
    person, from the goldens, the input format and the docs only, without reading the first spec. Give it a different
    architecture: if the current spec is a declarative table, write the second one as an imperative interpreter in
    the style of the legacy platform. Run both on the generators from items 3 to 8. Every input where they disagree
    and no golden covers it is a question for the stand.

## What I would add, in order

The cheap items come first, and they are the ones worth doing this week.

1. **Turn the surviving 2% of mutants into questions.** Each surviving mutant is an alternative no golden rules out.
   Its minimal input that tells it apart from the spec is a question that is ready to send.
2. **Run the spec's own pairwise and property suites against the stand**, not just against the spec.
3. **Run shadow traffic** if production or staging traffic can be mirrored. Mirror reads only, or isolate any writes.
   Compare responses **raw**, not through the parity normalizer.
4. **Audit the comparator** (item 2 above), and write a helper that wraps any probe in a context that separates
   "denied" from "did not apply" from "errored".
5. **Probe evaluation order and failures** with sentinels and poisons (item 3), weighted towards inputs where a wrong
   answer would be an "allow".
6. **Run the identity-collision and field state-matrix probes** (items 5 and 7), plus platform-idiom hypotheses
   (item 6) once you know the legacy stack.
7. **Add structural metamorphic relations** with a negative control (item 4), and raw-feature combinatorial coverage
   including order (item 8).
8. **Start the second model now** (item 12). It needs nothing else to begin, and the harness that compares the two
   models can be wired in last.

Run each round on a fixed budget. Score candidate questions by how many live alternatives each answer would rule out,
weighted by the cost of a wrong allow. Tier them (must, should, may) so that a budget cut drops the weakest ones.
Replay a few already-answered questions at the start and end of each round to detect drift on the stand. Run anything
that changes configuration in an isolated tenant.

## When it *would* be reasonable to stop asking

Stop on a rule about the **questions**, never on a score the spec gives itself. For example:

- the last round or two produced no **new** decisions, only changed values of existing ones, or nothing at all;
- every open hypothesis has been asked: surviving mutants, the comparator's merged classes, order and failure
  probes, collisions, spelling classes, and disagreements between the two models;
- `n` independent random inputs drawn from a **stated** input distribution all agreed with the stand. That bounds the
  disagreement rate at about `3/n` (95% confidence) **for that distribution only**, so pick a distribution that
  includes the adversarial shapes listed above, not just typical traffic.

Even then, describe the result as "no known disagreement, under these question sources, against legacy build X",
not as "proven". Keep shadow comparison running through cutover, so that the first real difference shows up as a diff
and not as an incident.
