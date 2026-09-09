# Pass 2: rules for a test authoring and review skill

Every claim below carries a label. **Studied** means a measured result in a paper, with the sample named in section 11.
**Asserted** means a practitioner or a document states it without measurement. **Derived** means it follows from the
mechanics of a tool or a language, and no source states it in that form.

Figures were checked against the paper text, not against summaries. Section 11 records what Pass 1 got wrong.

## 1. Executive summary

**Rule contributors.** Six sources survive as sources of rules an agent can apply: *Software Engineering at Google*
chapters 11 to 14 (the largest single contributor, and the only one covering robustness, the failure report, doubles,
and the size taxonomy together); the Go wiki's TestComments and CodeReviewComments (the sharpest T1 source in any
literature); `obra/superpowers` `writing-good-tests.md` (the only source that treats the test's author as an
adversary); the ISTQB CTFL v4.0 section 4.2 (input selection); Khorikov's managed/unmanaged criterion (the one
decidable mock rule); and the framework and mutation-tool documentation (the per-framework table and the oracle
semantics). Everything else drops to **supporting** — it supplies an evidence label, a proportion, or a name, not a
rule. That includes the whole empirical cluster (Inozemtseva, Just, Zhang and Mesbah, Petrović, Luo, Parry,
Panichella), the agent-behaviour studies, Beck's desiderata (headings, not rules), Meszaros (names, not rules), and
Spotify. Nothing on the shortlist is a reject; the pyramid/honeycomb pair collapses into Google's size taxonomy
(question 3) and survives only as background.

**Questions settled.** Eleven of fourteen. Question 1 (assertion count) is settled by Panichella's *semantic
coherence* criterion, which supplies exactly the reviewer test the brief asked for. Question 2 (doubles) is settled:
the four positions are one order with one decidable criterion per step. Question 3 (pyramid) is settled: replace the
shape argument with Google's constraint-defined sizes. Question 4 (smells) is settled decisively and against Pass 1's
expectation — Panichella's per-smell numbers kill Eager Test and Assertion Roulette as agent-applicable checks.
Question 6 (sensitivity) is settled and is the strongest part of the pass. Questions 7, 9, 10, 11, 12, 13 are settled
at the level of rules, all asserted or derived.

**Questions that stayed open.** Question 5 (the level rule) stays **derived**: no source states it, the derivation
below is defensible, but the "is a second level owed" half remains a judgment. Question 8 is settled for the
technique rules but **not for the evidence**: Reid 1997 is behind IEEE's paywall and every accessible route returned
the abstract or a citing summary, so the 0.79 and 0.33 figures are *not confirmed* here. Question 14 (baseline audit)
is answered, but one of its rules turns out to rest on a finding pointing the other way (section 10).

**Bucket split.** Of 44 rules: **30 apply from the diff and the test file alone**, which is the right proportion for
an agent that usually has nothing else; **5 need the suite run** (the two-run regression evidence, the random-order
run, the parameterized-name uniqueness check, what the runner actually prints, and flake reproduction); **5 need a
tool** (mutation on changed lines, a coverage report read negatively, a smell detector used only for two surviving
smells, a random-order runner, a property-test shrinker); **4 are human judgments** the agent may raise but not
decide (is a partition missing, is a surviving mutant equivalent, does a flake fix belong in the code under test, is
a second level worth its cost).

**Gaming.** The rules that resist a writer optimizing for green are the ones whose satisfaction is checked against
something outside the test: the two-run evidence, the mutation verdict on changed lines, the named production change,
the semantic-coherence check against the test's own name, and the "expected value written down independently" rule.
The rules that can be satisfied without the test being worth anything are all the shape rules — an assertion count,
a naming pattern, a partition checklist, a parameterized-case name, a message argument. A writer can satisfy every
one of them with a test that cannot fail. Section 3's Gaming column says, per rule, what the reviewer checks instead;
the skill must never present a shape rule as evidence of adequacy.

## 2. Deep candidate evaluation

| # | Candidate | Disposition | Strongest contribution | Main weakness | Evidence | Maintenance | Examples | FP risk | Portability |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | SWE at Google ch. 11–14 + Testing on the Toilet — [ch11](https://abseil.io/resources/swe-book/html/ch11.html), [ch12](https://abseil.io/resources/swe-book/html/ch12.html), [ch13](https://abseil.io/resources/swe-book/html/ch13.html), [ch14](https://abseil.io/resources/swe-book/html/ch14.html) | rule contributor | The only source giving robustness, the failure report, doubles, DAMP, and the size taxonomy with a rationale each | Every claim asserted; the ToT posts are largely unreadable through a fetcher, so cite the book | asserted (industrial practice at Google scale) | active | yes | low | easy |
| 2 | Go wiki [TestComments](https://go.dev/wiki/TestComments), [CodeReviewComments](https://go.dev/wiki/CodeReviewComments) | rule contributor | Failure line must name the function, the input, got, want, and a directed diff | Go-specific operand order; its "avoid assert libraries" advice does not port | asserted | active | yes | low | easy once operand order is per-framework |
| 3 | [obra/superpowers `writing-good-tests.md`](https://raw.githubusercontent.com/obra/superpowers/main/skills/test-driven-development/writing-good-tests.md) | rule contributor | Ten named gameable shapes plus three gate functions; "name the production change that fails this test" | No rationale per rule, no evidence, no sample; some shapes overlap | asserted | active (2025–26) | partial | medium (Trivial Coverage, Framework Test over-fire) | easy — already rule-shaped |
| 4 | Sensitivity cluster: [Inozemtseva](https://www.cs.ubc.ca/~rtholmes/papers/icse_2014_inozemtseva.pdf), [Just](https://homes.cs.washington.edu/~mernst/pubs/mutation-effectiveness-fse2014.pdf), [Zhang & Mesbah](https://people.ece.ubc.ca/amesbah/resources/papers/fse15.pdf), [Petrović](https://homes.cs.washington.edu/~rjust/publ/mutation_testing_practices_icse_2021.pdf) | supporting | Turns two rules from asserted to studied: coverage is not evidence, a surviving mutant is | Measures suites, not individual tests; nothing about the failure report | studied — samples in §11 | Just won a 10-year award (2024); Petrović active | no | n/a | easy as evidence labels |
| 5 | Mutation tools: [Stryker](https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/), [cargo-mutants](https://mutants.rs/using-results.html), [PIT](https://pitest.org/quickstart/mutators/), [mutmut](https://mutmut.readthedocs.io/en/latest/) | rule contributor | Exact oracle semantics; cargo-mutants states the caveat in the doc itself | Slow; no tool for every language; equivalent mutants stay a human call | asserted (tool contracts) | active | yes | low | easy |
| 6 | Flakiness: [Luo](https://petertsehsun.github.io/soen7481/papers/flakyTests.pdf), [Parry](https://eprints.whiterose.ac.uk/id/eprint/230095/1/parry2021.pdf), [pytest-randomly](https://github.com/pytest-dev/pytest-randomly), [MethodOrderer.Random](https://docs.junit.org/current/api/org.junit.jupiter.api/org/junit/jupiter/api/MethodOrderer.Random.html) | supporting + rule contributor (the runners) | A cause taxonomy with proportions, and one cheap oracle for the one cause the file does not show | The proportions come from Java/Apache and Mozilla; generalization untested | studied (Luo, Parry) + asserted (tool docs) | active | yes | low | easy as a checklist keyed by cause |
| 7 | Smells: [Meszaros](http://xunitpatterns.com/Test%20Smells.html), Bavota, Spadini, [Panichella](https://link.springer.com/article/10.1007/s10664-022-10207-5) | supporting (Meszaros: names only) | Panichella's per-smell numbers, which decide which smells an agent may flag | The catalog's two most-cited smells do not survive Panichella | studied (Panichella) vs studied (Bavota) — conflict resolved in §8 | Panichella active; Meszaros 2007 | yes | **high** if the catalog is applied mechanically | medium — only 3 smells survive |
| 8 | [ISTQB CTFL v4.0 §4.2](https://istqb.org/?sdm_process_download=1&download_id=3345) + Reid 1997 + Myers ch. 4 | rule contributor (ISTQB); background (Reid, Myers) | Precise, free definitions of partition, boundary, 2- vs 3-value BVA, decision table, state transition, with a coverage measure each | Says nothing about whether the test can fail; Reid unreachable | asserted (ISTQB); Reid **unconfirmed** | active (v4.0.1, 2024) | yes | medium (partitions need the spec) | easy |
| 9 | [Beck, Test Desiderata](https://testdesiderata.com/) | background | Twelve one-line properties; *Behavioral*, *Structure-insensitive*, *Specific*, *Isolated*, *Deterministic* are the vocabulary the other sources use unnamed | Properties, not rules; nothing is checkable | asserted | stale (2019) | no | n/a | easy as section headings only |
| 10 | [Khorikov, "When to mock"](https://enterprisecraftsmanship.com/posts/when-to-mock/) + the book | rule contributor | The one *decidable* mock criterion: is the dependency observable to another application? | Asserted; the managed/unmanaged line blurs for a shared database | asserted | stale (2020) | yes | low | easy — one question |
| 11 | Framework docs (JUnit, AssertJ, Truth, Hamcrest, pytest, Go, Rust, Jest, Vitest, node:test, KUnit) | rule contributor | The §4 table; which assertion prints operands and where the message goes | Per-framework; nothing generalizes except by translation | asserted (docs) + **measured** (`framework_output.md`) | active | yes | low | medium — must ship as a table, never as a universal rule |
| 12 | Agent studies: [over-mocking](https://arxiv.org/abs/2602.00409), [rethinking](https://arxiv.org/abs/2602.07900), [building to the test](https://arxiv.org/abs/2606.28430), [SWT-Bench](https://arxiv.org/abs/2406.12952), [overfitting](https://arxiv.org/abs/2511.16858), Schäfer, Yuan, Ouédraogo, Siddiq | supporting | Names the defect shapes the consumer actually produces, with frequencies for two of them | Observational; none evaluates a rule or an intervention that fixes the defect | studied — samples in §11 | active (2023–26) | no | n/a | easy as a "what you will do wrong" list |

## 3. Extracted rules

44 rules. Reader codes: T1 red-build reader, T2 reviewer, T3 refactorer, T4 next author. Bucket: **D** agent from the
diff, **S** suite run, **X** tool, **H** human.

### Sensitivity — can this test fail?

| # | Rule | Rationale | Reader | Source | Basis | Applies to | Detection | Gaming | Repair | Bucket |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Every test must assert on at least one value the code under test produced. | A test with no assertion covers lines and reports nothing; T2 reads coverage as evidence and gets none. | T2 | Zhang & Mesbah FSE 2015; Panichella §5.3 "Absence of Assertions"; superpowers | studied (assertion count and assertion coverage correlate with effectiveness; Panichella found assertion-free generated tests) | all tests | No assertion call in the test body, or the only call is a print/log | Yes — add an assertion on anything. Reviewer checks rule 2 and rule 7 next. | Assert the value the change is about | D |
| 2 | Write the expected value down as a literal or derive it independently; never compute it with the code under test or with a helper that duplicates it. | An expectation computed by the subject is an identity; the test passes for every implementation, and T2 is told nothing. | T2 | superpowers ("Mirror Assertion"); Google ch. 12 "Don't Put Logic in Tests" | asserted | all tests | The expected side of the assertion calls the unit under test, or the same builder produces both sides | No — this is checkable from the diff and cannot be faked by adding assertions | Replace with a literal or a value computed by hand | D |
| 3 | Do not assert on a value the test itself supplied and the code never transformed. | A round-trip through a setter and a getter asserts the language, not the change. | T2 | superpowers ("Trivial Coverage", "setup and assertion share the same object") | asserted | all tests | The asserted value is the same expression the arrange block passed in | Yes — a writer can transform trivially. Reviewer applies rule 7. | Assert on the output of the behaviour under test | D |
| 4 | Never mock, stub, or spy the unit under test. | A doubled subject makes the test assert the double; the real code is never executed. | T2 | superpowers ("Overmocked Dependency", "Partial Mock"); Google ch. 13 | asserted | tests with doubles | The mocked type is the type the test's name and file name refer to | No — visible in the diff | Construct the real subject; double its collaborators only | D |
| 5 | Never assert on a test double — not its call count, its presence, nor an identifier that exists only because it is a double. | The double is test scaffolding; asserting on it pins the scaffolding and can never detect a product defect. | T2 | superpowers ("Mock Assertion"); Google "Test State, Not Interactions" | asserted | tests with doubles | An assertion whose subject is the mock object or a `*-mock` literal | No | Assert the state the collaboration produced, or delete the assertion | D |
| 6 | A test that would pass merely because nothing threw must state the property it checks as an assertion. | "It did not crash" is a weaker claim than the test's name promises, and T1 cannot tell which claim failed. | T2 | superpowers ("Test fails only through panic or crash"); Panichella §5.3 | asserted | all tests | The body calls the subject and asserts nothing, or only asserts non-nullity of a construction | Yes — assert non-null. Reviewer applies rule 7. | Assert the value or the raised type and message | D |
| 7 | Before writing the body, name the single production change that would make this test fail; if you cannot name one, the test is not owed. | The only writer-side check that survives a writer rewarded for green. | T2 | superpowers ("Gate Functions") | asserted | all tests | Compare the named change against the diff: it must be inside the changed lines | No — the reviewer re-runs the question against the diff | Redesign the test around an observable behaviour | D |
| 8 | A regression test must be observed failing before the fix and passing after, and the pull request must say so. | Without the red run, nothing distinguishes a regression test from a test that always passed. | T2 | [Django](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/submitting-patches/) ("the test should fail before the fix is applied"); [rustc](https://rustc-dev-guide.rust-lang.org/tests/adding.html) ("should fail in `main` but pass after the PR"); [pytest](https://docs.pytest.org/en/stable/contributing.html) | asserted (three independent project policies) | regression tests | Run the new test against the pre-fix tree, or read the two-run evidence in the description | No — the red run is the evidence | Stash the fix, run the test, record the failure output | S |
| 9 | Never weaken an assertion, widen a tolerance, or delete a case to make a test pass. | A weakened assertion is indistinguishable from a passing one in the report, and permanently lowers what the suite guards. | T3 | superpowers; Google ch. 12 | asserted | all tests | An assertion changed in the same commit that changed the code, in the loosening direction (`assertEquals` → `assertNotNull`, an exact value → a range) | No — visible as a diff of the assertion itself | Fix the code, or state in the message why the looser claim is the real contract | D |
| 10 | Read every snapshot or golden file you accept, and assert on the parts the change is about. | An accepted snapshot records whatever the code does, including the defect; it is a change detector with no author. | T3 | Google "change-detector tests"; [PostgreSQL test evaluation](https://www.postgresql.org/docs/devel/regress-evaluation.html) | asserted | snapshot and golden-output tests | A snapshot file added or updated with no reviewed diff, or updated wholesale in a fix commit | Yes — a writer regenerates the file. Reviewer requires the snapshot diff in the review. | Review the diff line by line, or replace with targeted assertions | D |
| 11 | A coverage number is never evidence that a test can fail; do not cite one as adequacy. | Coverage measures execution, not checking; T2 who accepts it accepts nothing. | T2 | [Inozemtseva & Holmes ICSE 2014](https://www.cs.ubc.ca/~rtholmes/papers/icse_2014_inozemtseva.pdf) | **studied** (31,000 suites, 5 systems; correlation drops to low-to-moderate once suite size is controlled; the type of coverage barely matters) | all tests | A description or comment offering a coverage percentage as the argument | No | Cite the named production change (rule 7) or a mutation verdict (rule 12) | D |
| 12 | Run the mutation tool scoped to the changed lines, and treat *survived* on a changed line as a defect in the test until shown equivalent. | The only mechanical oracle for "this test can fail"; scoping to the diff is what makes it affordable. | T2 | [Stryker states](https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/); [cargo-mutants](https://mutants.rs/using-results.html); [Petrović ICSE 2021](https://homes.cs.washington.edu/~rjust/publ/mutation_testing_practices_icse_2021.pdf) / [TSE 2021](https://arxiv.org/abs/2102.11378) | studied (Google: developers exposed to mutants write more tests and their suites detect more mutants; incremental mutation on changed code only) + asserted (tool semantics) | changed lines with a test | Tool verdict. *Survived* = every test passed with the mutant active. *No coverage* = no test ran the line at all. *Unviable* = did not compile, inconclusive, no action. | No — the tool is external to the writer | Add the case that kills the mutant, or argue equivalence in the review | X |
| 13 | Equivalence of a surviving mutant is a claim for a human to accept, not for the author to assert in passing. | cargo-mutants states it in its own documentation: a missed mutant "may be indistinguishable from the correct code". | T2 | [cargo-mutants](https://mutants.rs/using-results.html); PIT's equivalence filters | asserted (tool contract) | mutation results | An unexplained suppression or skip annotation added with the change | Yes — suppress the mutant. Reviewer requires the argument in the review, not in a config file. | State why no observable behaviour differs | H |

### Robustness — will this test survive a refactoring?

| # | Rule | Rationale | Reader | Source | Basis | Applies to | Detection | Gaming | Repair | Bucket |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 14 | Drive the subject through the API its callers use; reach a private helper through the public entry point that calls it. | A test bound to an implementation detail turns every refactoring into a test edit, and T3 stops refactoring. | T3 | [Google ch. 12](https://abseil.io/resources/swe-book/html/ch12.html) ("invoke the system being tested in the same way its users would"); Khorikov ("observable behaviour") | asserted | all tests | The test calls a package-private or reflectively reached member, or imports a type not in the module's exported surface | Yes — a writer widens the visibility of the helper. Reviewer treats a visibility change made for a test as the violation. | Reach the helper through the entry point; if none reaches it, the helper is dead | D |
| 15 | Assert on the state the operation produced, not on the calls it made. | Interaction assertions record how the result was reached; T3 changes how and the test fails for no reason. | T3 | Google ch. 12 "Test State, Not Interactions" ("interaction tests check *how* a system arrived at its result, whereas usually you should care only *what* the result is") | asserted | tests with doubles | `verify(...)` / `toHaveBeenCalled` / `assert_called_with` where a returned or stored value is available | Yes — keep the verification and add a weak state assertion. Reviewer checks that the state assertion alone would fail. | Assert the returned value or the recorded state | D |
| 16 | Verify an interaction only when the call itself is the observable behaviour: a state-changing call to something outside the system. | Google and Khorikov agree on the same case from different directions; a query verification asserts nothing about correctness. | T3 | [Google ch. 13](https://abseil.io/resources/swe-book/html/ch13.html) ("you should perform interaction testing only for functions that are state-changing"); [Khorikov](https://enterprisecraftsmanship.com/posts/when-to-mock/) ("inter-system communications … form the observable behaviour") | asserted (two independent sources, same conclusion) | tests with doubles | A `verify` on a method that returns a value and changes nothing | No — the method's own signature decides | Delete the verification; stub the query instead | D |
| 17 | Prefer, in order: the real dependency; a fake maintained by the dependency's owner; a stub; an interaction assertion — and step down only when the level above is not fast, deterministic, and simple to construct. | Each step down trades fidelity for convenience; Google names the exact three properties that justify a step. | T3 | Google ch. 13 ("A real implementation is preferred if it is fast, deterministic, and has simple dependencies") | asserted | tests with a collaborator | A double for a dependency that is a pure function, a value type, or an in-memory structure | Yes — claim the real thing is slow. Reviewer asks for the measurement. | Use the real thing; ask the owner for a fake | D |
| 18 | Double a dependency only when another application can observe it: an SMTP server, a message bus, a third-party API. Use the real one for a database or a cache that only this application reaches. | This is the only mock criterion an agent can decide without asking the author. | T3 | Khorikov, "When to mock" ("Only unmanaged dependencies should be replaced with mocks") | asserted | tests with an external dependency | A mocked repository, DAO, or cache client; conversely, a real call to a third-party endpoint | No — the question is answerable from the dependency's type | Replace the mock with a real instance or a container; mock the outward-facing one | D |
| 19 | Do not mock a type you do not own. | You cannot know the real type's contract, so the double drifts and the test asserts your guess about someone else's code. | T3 | Google ch. 13 `@DoNotMock` ("this type should not be mocked because better alternatives exist"); Panichella (Java API invocations should be exempt from Indirect Testing) | asserted | tests with doubles | The mocked type comes from a third-party or standard-library package | Yes — wrap the type and mock the wrapper, which is correct. Reviewer accepts a wrapper, rejects a direct mock. | Use the real type, its own fake, or a thin owned wrapper | D |
| 20 | Do not assert on anything the product does not promise: private field layout, log text, exact error strings, source text, or call order that no caller can observe. | A change-detector test fires on every intentional change and sleeps through every accidental one. | T3 | [Google, change-detector tests](https://testing.googleblog.com/2015/01/testing-on-toilet-change-detector-tests.html); superpowers ("Change Detector", "Text Assertion"); Go wiki ("test error semantics", not error strings) | asserted | all tests | An assertion on a private member, a formatted log line, a full error message, or the presence of a string in a source file | Yes — a writer relaxes to a substring match. Reviewer asks whether a caller could depend on the string. | Assert on the typed error, the returned value, or the documented behaviour | D |
| 21 | The test body contains no conditional, loop, arithmetic, or string concatenation that computes an expected value. | Logic in a test is code that no test tests; T1 cannot tell whether the product or the test miscomputed. | T1 | Google ch. 12 ("if you feel like you need to write a test to verify your test, something has gone wrong"); Meszaros [Conditional Test Logic](http://xunitpatterns.com/Test%20Smells.html) | asserted | all tests | `if`, `for`, `while`, `try/catch` used for control, or an expected value built by concatenation, in the test body | Yes — move the logic to a helper. Reviewer follows the helper. | Inline the value as a literal; split into a parameterized case per branch | D |
| 22 | No test may read or write state that outlives it: a static field, a singleton, a shared temporary path, a shared record in a database. | A shared fixture makes the result depend on what else ran; T3's green suite stops meaning anything. | T3 | Meszaros General Fixture / Interacting Tests ("anything that outlives the lifetime of the test can lead to interactions"); [Parry](https://eprints.whiterose.ac.uk/id/eprint/230095/1/parry2021.pdf) | studied (Parry: static-field sharing facilitated 61% of order-dependent tests in Java) | all tests | A mutable static or module-level binding assigned in the test, or a fixed path/port/table name | Yes — reset it in teardown, which is a partial fix. Reviewer requires per-test construction where possible. | Construct per test; use a unique temporary directory and an ephemeral port | D |

### The failure report — what T1 holds

| # | Rule | Rationale | Reader | Source | Basis | Applies to | Detection | Gaming | Repair | Bucket |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 23 | Use the assertion that prints both operands; never assert a comparison through a boolean assertion. | `assertTrue(a == b)` and `assert ok` reduce the report to `true`/`false`; T1 then has to open an IDE. | T1 | [Go wiki](https://go.dev/wiki/TestComments); JUnit, AssertJ, Truth, Rust, node docs; **measured** in `framework_output.md` | **measured** (`assertTrue` → `expected: <true> but was: <false>`; JUnit 4 `assertTrue` → a bare `AssertionError`; Rust `assert!` prints the expression, `assert_eq!` prints left and right; pytest keeps introspection unless the comparison is bound to a variable first) | all tests | A boolean assertion whose argument is a comparison, or a comparison stored in a variable and then asserted | Yes — add a message. The message does not restore the operands (§4). | Switch to the equality/containment assertion for that framework | D |
| 24 | The failure must identify the function called and the input it was called with. | T1 holds only the report; without the input, the test name is a guess about which case broke. | T1 | Go wiki ("failure messages should include the name of the function that failed"); [Kubernetes](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-testing/writing-good-e2e-tests.md) ("Timeout" is not a useful error message) | asserted | all tests | The assertion prints two values and nothing that names the call or the argument | Yes — restate the test name in the message, which adds nothing. Reviewer requires the *input*. | Add the call and its argument to the message: `ensureBytes(-1) = -1, want 0` | D |
| 25 | Build the expected value as one whole structure and compare it in one assertion; do not assert field by field. | Field-by-field assertions stop at the first difference and hide the rest; T1 gets one field per run. | T1 | Go wiki ("Compare full structures"); Truth ("a `value of` line … the contents of the full multimap") | asserted + **measured** (testify and Jest print a field-level diff; JUnit `assertArrayEquals` names the differing index) | tests asserting on structures | Three or more assertions on fields of the same returned object | Yes — a writer wraps the fields in a tuple. That is the fix. | Construct the expected value and compare once | D |
| 26 | When the compared values are large, print a diff and say which side is which. | An undirected diff costs T1 a second run to work out which side is the product. | T1 | Go wiki ("Add some text to your failure message explaining the direction of the diff", e.g. `diff -want +got`) | asserted + **measured** (node prints `+ actual - expected`; Jest prints `- Expected / + Received`; testify prints `--- Expected +++ Actual`) | tests asserting on large values | A diff printed with no direction legend, or two long values printed whole | Yes | Use the framework's diff and label the direction | D |
| 27 | Put the operands in the order the framework's own report labels them, and never mix conventions inside one repository. | Reversed operands make the report lie: T1 reads the product's value as the expectation. | T1 | Go wiki (got before want); JUnit (`assertEquals(expected, actual)`); AssertJ/Truth/Jest/Vitest (`assertThat(actual)…`); Rust (`left`/`right`, no prescription) | asserted + **measured**; §4 carries the per-framework mapping | all tests | An `assertEquals` whose first argument is a call to the subject; a testify `assert.Equal` with the actual value first | No — mechanical | Swap the arguments | D |
| 28 | The message argument adds the context the assertion cannot know — the input, the case, the invariant — and never repeats what the assertion already prints. | Framework behaviour differs: in some frameworks a message *replaces* the generated text, so a redundant message destroys information. | T1 | JUnit, AssertJ, Hamcrest, pytest, Rust, node docs; **measured** | **measured** — JUnit/pytest/Rust `assert_eq!` **add**; AssertJ `withFailMessage`, Rust `assert!` with a message, and node `assert.ok` with a message **replace** (§4) | all tests | A message that restates the test name, or a `withFailMessage`/`assert!`-with-message that discards the operands | Yes — the presence of a message is not quality. Reviewer reads what the message adds. | Put the input in the message; use `as(...)` rather than `withFailMessage(...)` in AssertJ | D |
| 29 | Prefer the non-fatal assertion so one run reports every failure; use the fatal form only when continuing would crash or report nonsense. | One run per defect is the cost of the fatal form, and T1 pays it. | T1 | Go wiki ("Prefer calling `t.Error` over `t.Fatal`"); [KUnit tips](https://www.kernel.org/doc/html/next/dev-tools/kunit/tips.html) (`KUNIT_EXPECT_*` continues, `KUNIT_ASSERT_*` aborts) | asserted + **measured** (JUnit `assertAll` → `Multiple Failures (2 failures)`; Vitest `expect.soft` → two FAIL blocks; testify `require` stops, `assert` continues) | all tests | `t.Fatal`/`require`/`ASSERT` used for an ordinary value check rather than for setup | Yes — a writer uses the soft form for unrelated behaviours, which is rule 32's violation | Use `t.Error`, `assert`, `assertAll`, `expect.soft`, `KUNIT_EXPECT_*` | D |
| 30 | Every parameterized case carries a name derived from its data, never from its index. | `case_3` tells T1 nothing and changes meaning when a case is inserted. | T1 | Go wiki ("Never use test table indices as substitutes for naming"); [JUnit placeholders](https://docs.junit.org/current/writing-tests/parameterized-classes-and-tests.html); [pytest ids](https://docs.pytest.org/en/stable/how-to/parametrize.html); [Jest `.each`](https://jestjs.io/docs/api) | asserted + **measured** (Go turns spaces into underscores; pytest ids appear in the node id `test_eval[6*9-42]`; JUnit 4's default is `refused[0]`) | parameterized tests | A case name equal to an index, or a JUnit `@Parameterized` with no `name` attribute | Yes — a generated name from a large object is unreadable. Reviewer reads the rendered name. | Set `ids=`, `@ParameterizedTest(name = ...)`, or a `name` field in the table struct | D |
| 31 | The test's name states the condition and the expected outcome, not the method it calls. | T1 reads the name first; a name that repeats the method name adds nothing to the report. | T1 | Google ch. 12 ("describe both the actions that are being taken on a system and the expected outcome"); Go wiki (human-readable subtest names) | asserted (Wu & Clause detect non-descriptive names at 95% precision, but no study measures diagnosis time) | all tests | A name equal to the method name plus a counter or the word "test" | Yes — a long name is not a good name | Rename to condition-plus-outcome | D |
| 32 | One test covers one scenario: several assertions are correct when they all describe the state after a single operation, and wrong when they describe two independent scenarios. | This is the settled form of "one assertion per test" (§8). | T2 | [Panichella EMSE 2022](https://link.springer.com/article/10.1007/s10664-022-10207-5) *Semantic Coherence*; Google "Keep Tests Focused" | **studied** (Panichella: 39/49 developer suites were "eager" by the mechanical rule, but only 4 were semantically incoherent; eagerness predicted incoherence in 10% of cases) | all tests | Compare the asserted properties with the test's own name: do they all belong to the scenario the name states? | Yes — a writer splits by assertion count, producing more tests that each say less | Split by scenario, or turn the repeated scenario into a parameterized case | D |

### Inputs

| # | Rule | Rationale | Reader | Source | Basis | Applies to | Detection | Gaming | Repair | Bucket |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 33 | Partition each input into sets processed the same way, and cover every partition once — including every invalid one. | One case per partition is sufficient by the technique's own theory; the invalid partitions are the ones a writer skips. | T2 | [ISTQB CTFL v4.0 §4.2.1](https://istqb.org/?sdm_process_download=1&download_id=3345) ("one test for each partition is sufficient"; "test cases must exercise all identified partitions (including invalid partitions)") | asserted (Reid 1997's detection probabilities are **unconfirmed**, §11) | all tests | Every case in the test lies in one partition; no case exercises a rejected input | Yes — add one invalid case and stop. Reviewer names the partitions from the signature and the specification. | Add the missing partition; state the partitions in the test's name or its cases | D |
| 34 | A second case inside a partition already covered is redundant; a case on a boundary is not. | Redundant cases cost runtime and hide the missing partition behind a high case count. | T2 | ISTQB §4.2.1, §4.2.2 | asserted | parameterized tests | Two cases with the same classification and the same expected outcome, neither on a boundary | Yes — case count is not coverage | Delete the duplicate; add the boundary | D |
| 35 | For every ordered partition, test the boundary and its neighbour on the other side; add the neighbour inside the partition when the comparison operator is the thing that changed. | 2-value BVA misses an operator changed from `≤` to `=`; ISTQB gives that exact example. | T2 | ISTQB §4.2.2 (2-value and 3-value BVA, with the `if (x ≤ 10)` → `if (x = 10)` example) | asserted | tests over ordered inputs | A comparison in the diff whose boundary appears in no test case | Yes — a writer picks a value near the boundary but not on it | Add the boundary value and its neighbours | D |
| 36 | When the outcome depends on a combination of conditions, enumerate the feasible combinations as a decision table and cover each one. | Combinations are the cases a per-condition test set silently skips. | T2 | ISTQB §4.2.3 ("the coverage items are the columns containing feasible combinations of conditions") | asserted | changes to multi-condition logic | Two or more boolean guards in the changed code, and tests covering fewer than the feasible combinations | Yes — the full table is exponential; a risk-based subset is legitimate but must be stated | Add the missing columns, or state the reduction | D |
| 37 | When the outcome depends on what happened before, test sequences of events, not single calls, and cover the invalid transitions. | A stateful subject has defects only reachable through a sequence; single-call tests cannot reach them. | T2 | ISTQB §4.2.4 (all-states, valid-transitions/0-switch, all-transitions coverage; "the state table explicitly shows invalid transitions") | asserted | tests over a stateful subject | The subject holds state across calls and every test calls it once | Yes | Add a sequence test and one invalid transition | D |
| 38 | A property-based test must print the shrunk counterexample and a replay handle, and the replay handle must be recorded when a failure is triaged. | Without the seed or the blob, T1 holds a failure that may not recur. | T1 | [Hypothesis](https://hypothesis.readthedocs.io/en/latest/reference/api.html) (`@reproduce_failure`, `@seed`, the example database); **measured** for jetCheck (`rechecking("8Kaash…")`, `withSeed(…)`) | asserted (tool contracts) + measured; [Goldstein ICSE 2024](https://harrisongoldste.in/papers/icse24-pbt-in-practice.pdf) studied the practice, not the report | property tests | A property test with `print_blob` disabled, or a triage note with no seed | Yes — the blob is present but the shrunk example is unreadable | Record the blob in the issue; add the shrunk case as an explicit example test | D |
| 39 | Use a property test in addition to the examples, not instead of them, when the property is easier to state than the outputs are to enumerate. | The T1 cost of a property test is a case nobody wrote down; a named example test keeps the documentation value. | T4 | Goldstein ICSE 2024 (participants applied PBT opportunistically, where "the properties are sort of obvious"; they struggled to judge generator effectiveness) | **studied** (31 participants, 30 interviews, one firm) | property tests | A property test with no example test beside it for the case the change was about | Yes — a vacuous property passes everything | Add the example test; check the generator reaches the changed branch | D |

### Determinism

| # | Rule | Rationale | Reader | Source | Basis | Applies to | Detection | Gaming | Repair | Bucket |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 40 | Wait for the condition, with a timeout whose message names what was waited for; never sleep for a fixed duration and never let a bare timeout be the failure. | Async wait is the largest single cause of flakiness, and a bare timeout is the least informative failure there is. | T1 | [Luo FSE 2014](https://petertsehsun.github.io/soen7481/papers/flakyTests.pdf) (Async Wait 74/161 = 45%, the largest category; 54% of those fixed with `waitFor`); Kubernetes ("Timeout" is not a useful error message) | **studied** (Luo) + asserted (Kubernetes) | tests with asynchrony | `sleep`, `Thread.sleep`, `setTimeout`, or a fixed retry count in the test | Yes — a longer sleep passes more often. Reviewer treats any sleep as the violation. | Poll a condition with a bounded wait and a descriptive timeout message | D |
| 41 | A test must not read the wall clock, an unseeded random source, the locale, the timezone, the hostname, a real network address, or the file system outside a per-test temporary directory. | Each is a documented flake cause and a documented spurious-diff cause. | T3 | Luo (Randomness 4, Time 5, Network 10, IO 4, Floating Point 3, Resource Leak 11 of 161); [Parry](https://eprints.whiterose.ac.uk/id/eprint/230095/1/parry2021.pdf) (Platform Dependency 34% of sampled flaky bug reports); [PostgreSQL](https://www.postgresql.org/docs/devel/regress-evaluation.html) | **studied** (Luo, Parry) + asserted (PostgreSQL) | all tests | `now()`, `Random()` without a seed, a hardcoded port, a fixed `/tmp` path, a locale-dependent format in the test | No — grep-visible | Inject a clock and a seeded source; use an ephemeral port and a unique temporary directory | D |
| 42 | Do not assume the iteration order of an unordered collection or of a query with no ordering clause, and do not assume the execution order of tests. | Order dependence is the one flake cause the file does not show; it needs the random-order run. | T3 | Luo (Unordered Collections 1, Test Order Dependency 19 of 161); Parry (order-dependent tests up to 16% of flaky bug reports; 76% depend on exactly one other test); [pytest-randomly](https://github.com/pytest-dev/pytest-randomly); [MethodOrderer.Random](https://docs.junit.org/current/api/org.junit.jupiter.api/org/junit/jupiter/api/MethodOrderer.Random.html) | **studied** (Luo, Parry) + asserted (runner docs) | all tests | Partly from the file (an unsorted map iterated and compared to a list); otherwise, a random-order run with the seed printed | Yes — a writer sorts in the test but leaves the shared state. The random-order run catches it. | Sort before comparing, or compare as a set; move shared state into the test | S / D |
| 43 | Assert a range that admits every valid result; a tolerance narrower than the specification is a flake. | "Too restrictive range" is a top-three cause in the one developer survey that asked. | T3 | Parry, quoting Eck et al. (Too Restrictive Range 17% of 200 flaky tests classified by 21 Mozilla developers, behind Concurrency 26% and Async Wait 22%) | **studied** | tests over floats, timings, sizes | An exact float comparison, or a duration/size assertion with no stated tolerance | Yes — a writer widens the range until nothing fails, which violates rule 9 | Assert with the tolerance the specification allows, and say why | D |
| 44 | When a test is flaky, decide whether the defect is in the test or in the code under test before changing either. | A quarter of the time the flake is a real product bug, and almost every one of those was a genuine defect. | T2 | Luo FSE 2014, Finding F.12 ("Some fixes to flaky tests (24%) modify the CUT, and most of these cases (94%) fix a bug in the CUT") | **studied** | flaky tests | Whole-suite judgment; a fix that only widens a wait or adds a retry, with no reasoning recorded | Yes — a retry makes the symptom go away. Reviewer rejects an unexplained retry. | Reproduce, decide, and record the decision | H |

## 4. The framework table

Cells are **[M]** measured (`framework_output.md`, 2026-09-06/07) or **[D]** documented, with the URL in the source
column of §3. Where they disagree, the row says so.

| Framework | Prints both operands | Prints only a boolean / the expression | Where the message goes | Adds or replaces | Documented operand order | Parameterized case name | What the runner prints around it |
| --- | --- | --- | --- | --- | --- | --- | --- |
| JUnit Jupiter 6.1.3 | `assertEquals`, `assertArrayEquals` (names the index), `assertIterableEquals`, `assertThrows` **[M]** | `assertTrue`/`assertFalse` → `expected: <true> but was: <false>`; `assertNotNull` → `expected: not <null>` **[M]** | last parameter, `String` or `Supplier<String>` **[D]** | **adds**, joined with ` ==> ` **[M]** | `assertEquals(expected, actual)` **[D]** | `@ParameterizedTest(name = …)` with `{index} {arguments} {argumentsWithNames} {argumentSetName} {0}…`; project default via `junit.jupiter.params.displayname.default` **[D]** | test name, then the message; `assertAll` → `Multiple Failures (2 failures)` with one indented line per failure **[M]** |
| JUnit 4.13.2 | `assertEquals`; `ComparisonFailure` marks the differing region `expected:<Hello[] world>` **[M]** | `assertTrue`, `assertNotNull`, `fail()` raise an `AssertionError` **with a null message** — the report shows the class name and nothing else **[M]** | **first** parameter **[M]** | adds, space-joined **[M]** | `assertEquals(expected, actual)` **[D]** | `@Parameterized` default `refused[0]`; `@Parameters(name = "…")` **[M]** | `ErrorCollector` → `Multiple Failures` **[M]** |
| AssertJ 3.27.7 | `isEqualTo` → `expected: 0 / but was: -1`; collection assertions print the collection and the missing elements **[M]** | `assertThat(bool).isTrue()` → `Expecting value to be true but was false` **[M]** | `as(...)`/`describedAs(...)`, prefixed in brackets **[M]**; `withFailMessage`/`overridingErrorMessage` **[D]** | `as` **adds** (bracket prefix) **[M]**; `withFailMessage` **replaces** **[D]** | `assertThat(actual).isEqualTo(expected)` **[D]** | n/a (uses the host runner) | both must be called **before** the assertion; a failing assertion breaks the chain **[D]** |
| Google Truth 1.4.5 | `isEqualTo` → `expected: 0 / but was : -1`; `contains` prints the subject **[M]** | `assertThat(bool).isTrue()` → `expected to be true` **[M]** | `assertWithMessage(...).that(...)`, on its own first line **[M]** | **adds** **[M]** | `assertThat(actual).isEqualTo(expected)` **[D]** | n/a | doc claims a `value of:` line and unified diffs **[D]**; not observed for a bare `int` subject **[M]** |
| Hamcrest 3.0 | `assertThat(actual, is(expected))` → `Expected: is <0> / but: was <-1>` **[M]** | `assertThat(reason, boolean)` prints the reason **and nothing else** **[M]** | **first** parameter **[M]** | adds **[M]** | actual first, matcher second **[D]** | n/a | the reason line precedes `Expected:`/`but:` **[M]** |
| Go 1.27.1 `testing` | nothing automatic — the format string is the author's **[M]** | `t.Fail()` prints the test name and nothing **[M]** | the format string itself **[M]** | n/a — there is no generated text **[M]** | **got before want**: `t.Errorf("YourFunc(%v) = %v, want %v", in, got, want)` **[D]** | subtest name after `/`; spaces become underscores **[M]** | `--- FAIL: Test/sub (0.00s)` then `file:line: message` **[M]** |
| testify 1.12.1 | `assert.Equal` → `Not equal: expected: 0 / actual: -1` plus a `Diff:` block for strings and structs **[M]** | `assert.True` → `Should be true` **[M]** | variadic `msgAndArgs`, printed under `Messages:` **[M]** | adds **[M]** | `assert.Equal(t, expected, actual)` — the **reverse** of the Go wiki's convention, which the Go wiki tells you to avoid the library for **[D]** | n/a | `Error Trace:` with the absolute path, `Test:` with the name; `require` stops the test, `assert` continues **[M]** |
| pytest 8.4.2 | bare `assert` rewriting → `assert -1 == 0` plus `+ where -1 = ensure_bytes(-1)` **[M]** | binding the comparison first (`ok = a == b; assert ok`) → `assert False` **[M]** | `assert expr, "msg"` **[M]** | **adds**, above the introspection **[D][M]** | none prescribed | node-id suffix from the values, `ids=`, or `pytest.param(id=)`: `test_eval[6*9-42]` **[D][M]** | short summary `FAILED test_m.py::test_x - assert False` **[M]**; rewriting applies only to collected test modules **[D]** |
| Rust 1.98.0 | `assert_eq!` → ``assertion `left == right` failed`` with `left:`/`right:` in `Debug` **[M]** | `assert!` → `assertion failed: <expression text>` **[M]** | trailing format arguments **[M]** | `assert_eq!` **adds**; `assert!` with a message **replaces** the expression text **[M]** — the documentation does not state this **[D gap]** | none prescribed; the labels are `left`/`right` **[D]** | n/a (no built-in parameterization) | `#[should_panic(expected=)]` prints `panic message:` and `expected substring:` **[M]** |
| Jest 30.5.0 | `toBe`/`toEqual` → `Expected: 0 / Received: -1`, with a line diff for objects **[M]** | `expect(a === b).toBe(true)` → `Expected: true / Received: false`; `toBeTruthy()` → `Received: false` **[M]** | **no message argument**; only `expect.extend` **[D][M]** | n/a | `expect(received).toMatcher(expected)` **[D]** | `%s %d %i %f %j %o %p %# %$ %%`, or a tagged template with `$var` **[D]** | header `● describe › it`, then a code frame **[M]** |
| Vitest 5.0.0 | `toBe` → `expected -1 to be +0` plus a `- Expected / + Received` diff **[M]** | `toBe(true)` → `expected false to be true`; `toBeTruthy()` → `expected false to be truthy` **[M]** | `expect(value, message)` second argument **[D][M]** | **adds**, prefixed before the generated text **[M]** | `expect(actual).toMatcher(expected)` **[D]** | `it.each` with `%d`/`$var`, rendered as `file > describe > it` **[M]** | `expect.soft` → all failures reported, one FAIL block each **[D][M]** |
| node:test 26.8.1 | `assert.strictEqual` → `Expected values to be strictly equal: -1 !== 0`; `deepStrictEqual` → `+ actual - expected` diff **[M]** | `assert.ok` → `The expression evaluated to a falsy value:` plus the source text **[M]** | last argument of the assert call **[M]** | **replaces** for `assert.ok`; **adds** for `strictEqual` **[M]** | `assert.strictEqual(actual, expected)` **[D]** | none built in — name each case yourself **[D]** | `describe > it` names and `test at file:line:col` **[M]**. **Disagreement:** the docs' `t.plan` example counts a bare `assert.strictEqual`; measurement shows `t.plan` counts only `t.assert.*` **[M vs D]** |
| KUnit | `KUNIT_EXPECT_EQ` prints both values **[D]** | `KUNIT_EXPECT_TRUE` prints the expression **[D]** | the `_MSG` variants take a format string **[D]** | adds **[D]** | `KUNIT_EXPECT_EQ(test, left, right)` **[D]** | `KUNIT_CASE_PARAM` with a generator; the tips page documents neither the naming nor parameterization **[D gap]** | `KUNIT_EXPECT_*` marks failed and continues; `KUNIT_ASSERT_*` exits the test **[D]** — not measured |

Nothing else in `framework_output.md` contradicts the documentation. Two documentation gaps are worth recording: the
JUnit 5 docs list the display-name placeholders but the current page does not print the `DEFAULT_DISPLAY_NAME`
constant, and the Rust documentation does not say that a message on `assert!` discards the expression text.

## 5. The level rule and its test — **derived**

No source states which level a change owes a test at. The rule below is assembled from four criteria that *are*
sourced, and it is derived, not sourced.

> **The level rule.** Test at the innermost level from which the change is observable through an interface someone
> outside the change depends on. Add a second level only where one of Google's four named gaps applies — an
> unfaithful double, a configuration, behaviour under load, or emergent behaviour outside the unit's scope
> ([ch. 14](https://abseil.io/resources/swe-book/html/ch14.html)) — or where the change alters what an *unmanaged*
> dependency observes (Khorikov), which is a contract someone else can break.

Its inputs: "observable through the public API" (Khorikov, Google ch. 12); Google's four gaps (ch. 14); Google's
sizes defined by constraints, not by counts (ch. 11); and the policy that every package owes unit tests (Kubernetes).

**Reviewer's check that the author chose rather than defaulted:** the test's location and its entry point must
follow from the change. A test at a level the change is not observable from — or a test at the same level as every
other test in the branch regardless of what changed — is a default, not a choice.

| Change | Level owed | Second level? | What the reviewer checks |
| --- | --- | --- | --- |
| Bug fix in a private helper | Unit, through the public entry point that reaches the helper | No | The test calls the exported function, not the helper. A test that widens the helper's visibility, or reaches it reflectively, is the violation (rule 14). If no public entry point reaches the helper, the helper is unreachable and the fix is unverifiable — raise it. |
| New public method | Unit, through the new method | Only if the method's outcome depends on a real collaborator that the unit test doubles | The test constructs the subject the way a caller would, and covers the partitions of the new signature including the invalid ones (rule 33). A second level is owed exactly when a double stands in for something whose fidelity is in question (Google's "unfaithful doubles"). |
| Change in a protocol reader parsing bytes from a socket | **Two levels.** Unit: the reader against recorded bytes, including truncated, oversized, and malformed frames. Integration: the reader against a real peer or a recorded session at the contract boundary. | Yes — always | The unit test's inputs are byte arrays, not objects the encoder produced (that would be rule 2). The second level exists because the byte format is an unmanaged dependency: another application produces it, so its shape is observable behaviour (Khorikov), and Spotify's honeycomb puts the test at exactly that contract. A round-trip encode-then-decode test alone is the violation. |
| Change in a configuration default | **Not a unit test.** The level is whatever loads the configuration for real. | Yes, and the unit level is often owed nothing | Google names configuration as a gap unit tests cannot close, and says configuration changes are the leading cause of its major outages. A test that asserts the constant equals its new value is a change-detector (rule 20) and is worth nothing. The reviewer looks for a test that boots the component with the shipped configuration and asserts the behaviour the default produces. |

**What stays open.** Whether a second level is *worth its cost* is a human judgment in every row above except the
protocol reader, where a source (Spotify, Google) names the case. The agent may state the case and ask.

## 6. The sensitivity list

Complete list of shapes that cannot fail, or fail only for the wrong reason.

| Shape | Named by | Detection from the diff | Repair | Oracle |
| --- | --- | --- | --- | --- |
| No assertion | Panichella §5.3 "Absence of Assertions"; Zhang & Mesbah | No assertion call in the body | Assert the produced value | mutation: every mutant on the covered line survives |
| Assertion on a value the test supplied | superpowers | The asserted expression is the arrange block's input, unchanged | Assert the output | mutation |
| Expected value computed by the code under test | superpowers "Mirror Assertion" | The expected side calls the subject | Write the literal | mutation |
| Expected value from a helper that duplicates the subject | superpowers | The helper reimplements the algorithm under test | Write the literal | mutation |
| Mock of the unit under test | superpowers "Partial Mock"; Google ch. 13 | The mocked type is the subject | Construct the real subject | none — read the diff |
| Assertion on the mock | superpowers "Mock Assertion"; Google "Test State, Not Interactions" | The assertion's subject is the double | Assert the state | none |
| Interaction verification on a query | Google ch. 13 ("only for functions that are state-changing") | `verify` on a method that returns and mutates nothing | Delete it | none |
| Passes only because nothing was thrown | superpowers; Panichella footnote 8 | Call with no assertion, or only a non-null assertion | Assert the value or the raised type | mutation |
| Change-detector test | Google, ToT 2015; superpowers | Asserts a private field, a log line, an exact error string, or source text | Assert the promise | mutation (fires on *every* mutant, including unrelated ones) |
| Text/grep assertion on source | superpowers "Text Assertion" | The test reads a source file | Run the artifact and assert its effect | none |
| Framework test | superpowers "Framework Test" | Asserts behaviour the framework owns, not the change | Delete | mutation on changed lines: nothing is covered |
| Trivial coverage | superpowers | Asserts a constructor, a getter, or a constant | Delete, or assert the validation it performs | mutation: no viable mutant exists |
| Reads back the same object it wrote | superpowers ("setup and assertion share the same object") | The assertion's subject is the object the arrange block constructed, not one the subject returned | Assert the returned or persisted value | mutation |
| Assertion weakened until it passes | superpowers; Google ch. 12 | The assertion changed in the loosening direction in the same commit as the code | Fix the code | git history |
| Snapshot accepted without reading | Google change-detector; PostgreSQL spurious diffs | A snapshot file regenerated wholesale in the fix commit | Read the diff, or assert on the fields that matter | none — the reviewer reads it |
| Too-restrictive range that widened to pass | Parry / Eck et al. | The tolerance widened in the same commit | Assert the specification's tolerance | random-order and repeat runs |

**The two-run rule.** Django asks "Is there a proper regression test (the test should fail before the fix is
applied)?"; the rustc dev guide says the test "should fail in `main` but pass after the PR"; pytest says a
demonstration test that "currently fails but should pass" is a useful commit on its own. All three state it as a
policy and none proposes a check. **What a pull request can carry:** the failure output of the new test against the
pre-fix tree, pasted in the description; or the fix and the test in separate commits, so a reviewer can check out the
test-only commit and run it. Both are cheap and both are verifiable by a reviewer without the author. The skill
should require one of the two for any change described as a bug fix.

**What a scoped mutation run establishes.** Run the tool over the changed lines only, as Google does. *Survived* means
"all tests passed while this mutant was active" — the test suite does not distinguish the change from a defect on
that line. *No coverage* means the mutant "isn't covered by one of your tests", a strictly worse finding: the line
never ran. *Unviable* (cargo-mutants) or *compile error* (Stryker) is "inconclusive about test coverage and no action
is needed". A missed mutant "may be indistinguishable from the correct code" — cargo-mutants states the caveat
itself, so equivalence is a live possibility on every survivor and belongs to a human (rule 13). What the run does
*not* establish: that the test is readable, that its failure report is usable, that it tests the right behaviour, or
that a missing partition exists. Petrović's evidence is about the *practice*, not the individual verdict: developers
whose changed lines were mutated wrote more tests, and their suites detected more mutants over time.

## 7. Worked examples

Eight rules whose violation is hardest to recognize.

1. **Rule 2, mirror assertion.** *Before:* `assertEquals(formatter.format(order), formatter.format(order))`, or the
   subtler `assertEquals(new Money(a.cents + b.cents), a.plus(b))` where `plus` is the method under test. *After:*
   `assertEquals(new Money(750), Money.of(500).plus(Money.of(250)))`. superpowers names the shape but ships no code
   example; this one is constructed.
2. **Rule 32, semantic coherence.** *Before* (Panichella's own Figure 9, from Weka): one test calls `tokenize` on two
   unrelated inputs and asserts both — two scenarios, no state relation. *After:* two tests, or one parameterized
   test with one case per input. Compare Panichella's Figure 8, from freemind: a test that creates a `Counter` via a
   helper and asserts several of its fields is "eager" by the mechanical rule and correct by the semantic one,
   because every assertion describes the state after one operation. The example is the paper's own.
3. **Rule 16, interaction on a query.** *Before:* `verify(repository).findById(7)` beside an assertion on the
   returned object. *After:* delete the `verify`; the state assertion already fails if the lookup did not happen.
   Google's ch. 13 states the rule; the example is constructed from its wording.
4. **Rule 23, boolean assertion.** *Before:* `assertTrue(ensureBytes(-1) == 0)` → the report reads `expected: <true>
   but was: <false>`, and on JUnit 4 reads nothing at all. *After:* `assertEquals(0, ensureBytes(-1))` → `expected:
   <0> but was: <-1>`. Both outputs are measured, not inferred.
5. **Rule 28, message that replaces.** *Before:* `assertThat(actual).withFailMessage("size mismatch").isEqualTo(3)`
   → the report says `size mismatch` and the operands are gone. *After:* `assertThat(actual).as("size of %s",
   input).isEqualTo(3)` → `[size of [a, b]] expected: 3 but was: 2`. AssertJ's own documentation states the
   difference; the outputs are measured.
6. **Rule 10, snapshot accepted blind.** *Before:* a golden file regenerated in the same commit that changed the
   renderer, with no diff reviewed. *After:* the golden diff quoted in the description, or the four fields the change
   touched asserted directly. PostgreSQL's test-evaluation page is the closest source, and it is about spurious
   diffs, not about accepting them; it has no example of this shape.
7. **Rule 22, shared mutable fixture.** Meszaros's own Interacting Tests text names the mechanism precisely: "anything
   that outlives the lifetime of the test can lead to interactions; static variables … should therefore be avoided in
   both the SUT and the Test Automation Framework". *Before:* a `static Map<String, User> USERS` populated in
   `@BeforeAll`. *After:* build the map in the test. Parry supplies the number: static fields facilitated 61% of
   Java order-dependent tests.
8. **Rule 41, ambient state.** *Before:* `assertEquals("2026-09-07", formatDate(new Date()))` — passes today, fails
   tomorrow and in another timezone. *After:* inject a fixed clock. PostgreSQL's page catalogues exactly this class
   of spurious diff (locale, timezone, float formatting, row order without `ORDER BY`); the code example is
   constructed.

## 8. Conflicts and how they were decided

**One assertion per test vs. one behaviour per test.** Positions: the baseline says one assertion per method;
Google, superpowers, and "Keep Tests Focused" say one behaviour; `assertAll`, `SoftAssertions`, `expect.soft` and
`KUNIT_EXPECT_*` exist precisely to put several assertions on one behaviour. **Decided for the behaviour position, with
Panichella's criterion as the reviewer's test.** Panichella measured the mechanical rule and it failed: 39 of 49
developer-written suites were "eager" by the detector, only 4 were semantically incoherent, and eagerness predicted
incoherence in 10% of cases — "no evidence that the Eager Test smell is a useful discriminator." The test a reviewer
applies: *do all the assertions describe the state after one operation, and does the test's own name name that
operation?* If yes, the assertion count is irrelevant. If they describe two independent scenarios, split, or
parameterize. T2 wins. **T1 is harmed** in one narrow case: several assertions in one test on a framework with no
soft-assertion support means one failure per run. The mitigation is rule 29 (prefer the non-fatal form), not a lower
assertion count.

**Mocks vs. fakes vs. real dependencies.** Positions: Google prefers real, then fake, then stub, then interaction
test, and gates each step on fast/deterministic/simple-to-construct; Khorikov mocks only unmanaged out-of-process
dependencies and never intra-system communication; superpowers says no mocks unless unavoidable; the over-mocking
study finds agents add mocks in 36% of their test commits against 26% for people. **Decided as one order with one
criterion per step** (rules 17, 18, 19). They are not in conflict: Google's order says *how far down to step*,
Khorikov's criterion says *which dependency is even a candidate*, and superpowers is Google's order stated as a
prohibition. **Three shapes are rejected outright regardless of position:** a mock of the unit under test (rule 4),
an assertion on the mock (rule 5), an interaction verification on a query (rule 16). T3 wins. Nobody is harmed: the
losing formulation ("no mocks") is stricter than the order and is subsumed by it.

**Pyramid vs. honeycomb.** Both asserted; Dodds disclaims scientific grounding for his own trophy. **Replaced by
Google's size taxonomy**, which is defined by constraints and therefore checkable: a **small** test runs in one
process and may not sleep, perform I/O, or touch the network or disk; a **medium** test may span processes, use
threads, and make blocking calls to `localhost` only; a **large** test may reach other machines. Size is orthogonal
to scope (how much code is validated). The counts (Google's rough 80/15/5) are a target, not a rule, and the skill
should not carry them. This sidesteps the shape argument entirely: the question "is this a unit test" becomes "which
constraints does it violate", which an agent can answer from the file.

**Test smells: Bavota and Spadini vs. Panichella.** Positions: Bavota measured comprehension 30% better without
smells and 86% of JUnit classes smelly; Panichella hand-annotated hundreds of suites and found the vocabulary
"highly mismatched to real concerns". **Decided for Panichella on the per-smell question**, because it is the only
study that annotated by hand rather than trusting a detector, and it explicitly re-examines the earlier work's ground
truth. The surviving list is short:

| Smell | Verdict | Basis |
| --- | --- | --- |
| **Eager Test** | **Do not flag.** Replace with semantic coherence (rule 32). | studied: 80% prevalence, 10% predictive |
| **Assertion Roulette** | **Do not flag.** "Generally obsolete": modern runners name the failing assertion, and `assertNull`/`assertNotNull` need no message. Panichella extends this to `unittest` and every modern framework. | studied: 60% prevalence, the confound it addressed no longer exists |
| **Indirect Testing** | **Flag**, exempting calls to the standard library. 20% in developer suites against 32–47% in generated ones — "a concern that developers do seek to avoid". | studied |
| **Mystery Guest** | **Flag** — a fixture the test does not show. Panichella did not annotate it for generated tests; it is unrefuted, not confirmed. | asserted (Meszaros), unrefuted |
| **Resource Optimism** | **Flag** — assumptions about the file system, the OS, or available processing power. Overlaps rule 41. | studied: 5/49, and every instance was a real assumption |
| **Sensitive Equality** | **Flag weakly** — asserting through `toString`. 10% in developer suites, and two of the five were tests *of* `toString`. | studied, with a high false-positive rate |
| **Conditional Test Logic** | **Flag** (rule 21). Not in Panichella's six; Google states it independently. | asserted, two sources |

**Bavota is not discarded:** its 30% comprehension result stands as evidence that *some* smells harm comprehension.
Panichella limits *which*. **T2 wins**, and the harm is to nobody: dropping two ubiquitous smells removes false
positives, and the tool ("current test smell detection strategies … misclassified over 70% of test smells" on
generated suites) is demoted from checker to hint.

**Operand order: `got, want` vs. `expected, actual`.** Not a conflict in substance — a convention per framework —
but it becomes one inside a repository that uses both `testify` (`assert.Equal(t, expected, actual)`) and the
standard Go convention (`got, want`). §4 carries the mapping; rule 27 forbids mixing them in one repository.

**Go's "avoid assert libraries" vs. every other framework.** The Go wiki says assertion libraries "either stop the
test early … or omit interesting information" and force "a whole new sub-language". Every other ecosystem in §4
ships or recommends one. **Not resolved as a universal rule**: it is a Go-specific convention, and the skill must
present it as such. The generalizable part is the *reason*, which is rules 23 and 29.

## 9. The detectability matrix

| Bucket | Rules | Source per bucket |
| --- | --- | --- |
| **Agent, from the diff and the test file** (30) | 1–7, 9–11, 14–28, 30, 31, 32, 33–37, 39, 40, 41, 43 | superpowers (gate functions); Google ch. 12–13; Go wiki; ISTQB §4.2; framework docs + `framework_output.md`; Luo's cause list read as file patterns |
| **Needs the suite run** (5) | 8 (two-run regression evidence), 30 (the rendered case name), 27 (what the runner actually prints), 42 (random order), 44 (flake reproduction) | Django / rustc / pytest contribution policies; pytest-randomly and `MethodOrderer.Random`, both of which print a seed; measured runner output |
| **Needs a tool** (5) | 12 (mutation, scoped to changed lines), 11 (a coverage report read only as a negative signal), 38 (the shrinker's blob), 42 (the random-order runner), and the three surviving smells from §8 as hints | Stryker / cargo-mutants / PIT / mutmut; Petrović; Hypothesis and jetCheck; tsDetect demoted per Panichella |
| **Human** (4) | 13 (is a surviving mutant equivalent), 33 (is a partition missing — no oracle knows the specification), 44 (is the flake in the test or in the code under test), and the second-level question in §5 | cargo-mutants states the equivalence caveat; ISTQB requires a specification; Luo F.12; no source decides the level question |

Rules 27, 30 and 42 appear in two buckets: each has a diff-visible form and a run-only confirmation. That is not an
overlap between rules; it is the same rule with a cheap check and an expensive one.

## 10. Baseline audit

**Part 1, "a failing test is a bug report".** **Survives, and is the right frame.** It is exactly the T1 reader, and
four sources support it independently: the Go wiki's whole rationale, Kubernetes's "Timeout is not a useful error
message", Beck's *Specific* ("if a test fails, the cause of the failure should be obvious"), and Google's "Write
Clear Failure Messages". It should be stated more sharply: the reader holds *only* the report, so the report must
carry the function, the input, the expected value, and the actual value (rules 23–28). **Caveat to state honestly:**
no study measures time from a red build to a diagnosis as a function of the name, the assertion, or the message.
Every Part 1 rule is asserted, and the skill must not imply otherwise.

**"One assertion per method."** **Needs restating**, as Pass 1 flagged, and now with a measured reason. Replace with
rule 32 and the semantic-coherence test. Panichella's numbers are the argument: the mechanical version fires on 80%
of well-written developer tests and predicts a real problem in 10% of them.

**"Avoid `assertTrue`."** **Survives, but the rationale must change.** The baseline's reason is presumably
effectiveness; the evidence points the other way. Zhang and Mesbah found that "assertions with method type
assertTrue/False are more effective than those with type assertEquals/Not and assertNull/Not". The rule survives
purely on the failure report (rule 23), which is measured: `assertTrue(a == b)` prints `true`/`false`, and on JUnit 4
prints nothing at all. State the reason as T1's, never as effectiveness.

**"Cover the equivalence classes and the boundaries."** **Survives as stated**, with ISTQB's precision added: valid
*and invalid* partitions, one case per partition, 2-value versus 3-value BVA, and the coverage measure per technique
(rules 33–35). **The evidence claim must be dropped**: Reid's 0.79 and 0.33 are not confirmed (§11).

**"Choose the level."** **Survives only as a question, not as a rule**, until §5's derivation is accepted. No source
states a level rule. The skill should ship §5's derivation, labelled derived, with the four worked changes.

**What the baseline is missing entirely.** Six things, in descending order of cost:

1. **Sensitivity.** Nothing in the baseline asks whether the test can fail. This is the largest gap and §6 fills it.
2. **The gaming frame.** The baseline addresses an author who wants a good test. The consumer is an author rewarded
   for a green suite. Every rule needs a Gaming column.
3. **Doubles.** No rule about mocks at all, in a skill whose consumer adds them in 36% of its test commits.
4. **Determinism.** No rule about sleeps, clocks, seeds, order, or ranges — five studied flake causes.
5. **The regression-test two-run guarantee**, stated as policy by three major projects.
6. **The framework mapping.** The baseline states failure-report rules universally; §4 shows they are per-framework,
   and a rule stated universally is wrong in at least three of the twelve frameworks.

## 11. Evidence map

**Measured.** `framework_output.md`, 2026-09-06/07, versions as named in it. This is the only evidence in the report
generated for it, and it underwrites rules 23, 25–30, and the whole of §4.

**Studied, with the sample and the figure checked against the paper text:**

- **Inozemtseva & Holmes, ICSE 2014.** 31,000 suites, five Java systems up to 724,000 lines; statement, decision, and
  modified-condition coverage against mutation score. Kendall τ **0.94, 0.95, 0.81, 0.91, 0.85** with size ignored,
  falling to **0.75, 0.83, −0.35, 0.50, 0.80** (statement coverage, normalized effectiveness) with size controlled.
  Conclusion in the paper's own words: coverage "should not be used as a quality target because it is not a good
  indicator of test suite effectiveness." Pass 1 was correct; the numbers are added here.
- **Just et al., FSE 2014.** 357 real faults, five open-source programs totalling 321,000 lines, 230,000 mutants.
  **73%** of real faults coupled to mutants from commonly used operators; **27%** not coupled to those; of those,
  **17%** "are not coupled to any mutants", mostly algorithmic changes or code deletion. **Correction to Pass 1:**
  Pass 1 gave "73% coupled, 17% not coupled", which reads as a complement and is not one. The complement of 73% is
  27%; 17% is the subset that no operator can reach, and the remaining 10% is the argument for stronger operators.
- **Zhang & Mesbah, FSE 2015.** 6,700 suites, 5,892 test cases, **24,701** assertions, five Java projects. Very strong
  correlation between assertion count and effectiveness with and without controlling for the number of test methods;
  very strong correlation for assertion coverage. Pass 1 correct. **Added, and it matters for the baseline audit:**
  `assertTrue`/`assertFalse` were found *more* effective than `assertEquals` and `assertNull`.
- **Petrović et al., ICSE 2021 and TSE 2021.** ~15 million mutants over six years at Google; the code-review
  deployment served **more than 24,000 developers on more than 1,000 projects**. Mutation is incremental — only
  changed code, during code review — with filtering and per-line limits. Developers exposed to mutants write more
  tests and their suites detect more mutants over time. Pass 1 correct.
- **Luo et al., FSE 2014.** 1,129 candidate commits from Apache, 855 likely about flaky tests, 486 likely distinct
  fixes, **201 inspected**, **161 classified**. Counts out of 161: Async Wait 74 (45%), Concurrency 32 (20%), Test
  Order Dependency 19 (12%), Resource Leak 11, Network 10, Time 5, IO 4, Randomness 4, Floating Point 3, Unordered
  Collections 1, hard to classify 40. 126 of 161 (**78%**) were flaky from the first time they were written. **24%**
  of fixes modify the code under test, and **94%** of those fix a real bug. 54% of Async Wait cases fixed with
  `waitFor`. **Correction to Pass 1:** the denominator is 161, not 201; Pass 1 wrote "74/201".
- **Parry et al., TOSEM 2021.** A survey of the flaky-test literature. Platform dependency **34%** of sampled bug
  reports; order-dependent tests up to **16%** of flaky bug reports and **9%** of repairs; **76%** of order-dependent
  tests depend on exactly one other test; static fields facilitated **61%** of Java order-dependent tests. The
  "26% / 22% / 17%" triple Pass 1 quoted is **Eck et al., reported by Parry**: 21 Mozilla developers classifying 200
  flaky tests they had fixed — Concurrency 26%, Async Wait 22%, Too Restrictive Range 17%, Test Order Dependency 9%.
  Pass 1 attributed it to "a later study" without naming it.
- **Panichella et al., EMSE 2022.** Hundreds of test suites, hand-annotated in a multi-stage cross-validated manual
  analysis; six smell types; 49 developer-written suites in the manual sub-study; developer tests plus EvoSuite and
  JTExpert output. Per-smell numbers in §8. **Correction to Pass 1:** the "over 70%" misclassification is the
  **older tool's** rate on **automatically generated** test suites, counting both false negatives and false
  positives — not a general detector error rate. The vocabulary quote is exact: "the current vocabulary of test smells
  is highly mismatched to real concerns."
- **Bavota et al., EMSE 2015.** 86% of JUnit classes smelly; comprehension 30% better without smells. **Not
  confirmed from the paper.** Every route (the publisher, the authors' pages, three institutional mirrors) returned a
  paywall or a 404; the figures here come from the publisher's abstract and citing summaries. Carry them as
  second-hand.
- **Over-mocking, arXiv 2602.00409.** Over 1.2 million 2025 commits across 2,168 TypeScript, JavaScript and Python
  repositories, including 48,563 agent commits. **Correction to Pass 1's phrasing:** the figure is not "36% of agent
  commits add mocks"; it is "**36% of test commits** made by coding agents add mocks to tests, compared with **26%**
  of test commits made by non-agents". Within repositories that have both kinds of activity, the paired comparison is
  36% against 28%.
- **Rethinking agent-generated tests, arXiv 2602.07900.** Six models on SWE-bench Verified. Test writing is common
  but weakly aligned with success: Claude Opus 4.5 writes a test artifact in ~83% of tasks and resolves 74.4%; GPT-5.2
  writes one in 0.6% of tasks and resolves 71.8%. When tests are written they are "an observational feedback channel,
  with value-revealing prints dominating assert-based checks."
- **Building to the test, arXiv 2606.28430.** Two production agents, 18 runs, three oracle-availability conditions, a
  hidden 222-test Playwright oracle. With the oracle in the loop, the score is near-perfect but the agents satisfy it
  "by inlining the tested state into a throwaway demo while leaving the requested library dead or absent." Small
  sample; the authors say prevalence is open.
- **SWT-Bench, arXiv 2406.12952.** Generated tests used as a filter on proposed fixes "doubl[e] the precision of
  SWE-AGENT".
- **Test overfitting, arXiv 2511.16858.** First empirical study of test overfitting in repository-level issue
  resolution: code that passes the generated tests and fails held-out tests; mitigations help only partly.
- **Schäfer et al., TSE 2023.** 25 npm packages, 1,684 API functions, gpt-3.5-turbo. Of *failing* generated tests, a
  median **19.2%** fail on assertion errors, 22.7% on timeouts, 20.0% on correctness errors.
- **Siddiq et al., 2023.** 160 HumanEval-Java classes and 194 classes from 47 SF110 projects. Between **52% and 81%**
  of generated test suites were fully correct; 81%–92% had at least one passing method. Most common smells: Magic
  Number Test, Assertion Roulette, Eager Test, plus Empty Test and Duplicate Assert. **Correction to Pass 1: the
  62.4% figure is a misattribution.** It appears nowhere in Siddiq. The string "62.4%" occurs in Schäfer et al. as
  the share of non-trivial tests generated for the `rsvp` package, which has nothing to do with assertion
  correctness. Drop the figure.
- **Ouédraogo et al., TOSEM 2025.** Assertion Roulette is the dominant smell in LLM-generated suites, exceeding 90%
  prevalence at method level. Read alongside Panichella's finding that Assertion Roulette is obsolete: what this
  measures is that LLMs omit assertion messages, which §8 says is no longer a defect on a modern runner.
- **Goldstein et al., ICSE 2024.** 31 participants recruited, 30 interviews, all at Jane Street. Qualitative;
  single-firm; no measured outcome.

**Stated policy, not measured.** Django, rustc-dev-guide, and pytest on the regression-test guarantee; Kubernetes on
hermeticity, parallel safety, and failure-message quality; PostgreSQL's spurious-diff catalogue; the mutation tools'
outcome definitions; every framework documentation claim in §4 marked **[D]**.

**Inference from mechanics (derived).** The level rule (§5); the choice of bucket per rule (§9); the claim that a
scoped mutation run is affordable *because* Petrović's deployment scopes it that way; the reading of Luo's cause
taxonomy as a set of file-visible patterns.

**Asserted.** Everything from Google's book and the Testing on the Toilet series; the Go wiki; superpowers; Beck;
Khorikov; Meszaros; Spotify; ISTQB.

**Not confirmed, and must not be cited as if it were.** **Reid 1997**, "An empirical analysis of equivalence
partitioning, boundary value analysis and random testing." The paper is behind IEEE Xplore's paywall; the DOI page,
ResearchGate, and Semantic Scholar all returned metadata or a bot challenge. The BVA 0.79 and EP 0.33 mean detection
probabilities, and the ~20,000-line Ada avionics program they come from, appear only in citing summaries. **Do not
state these figures in the skill.** The technique rules (33–37) rest on ISTQB and stand without them.

## 12. What the skill-writing session should be told

**Ship these, load-bearing.** §6, the sensitivity list, is the skill's reason to exist and must come first — it is
the only part addressing the fact that the writer is rewarded for green. Rules 1–13 with their Gaming columns. Rules
14–22, because they are what makes a suite survive T3. §4 as a lookup table. §5's level derivation, labelled derived,
with all four worked changes. Rules 40–44, because determinism is five studied causes and the baseline has none.

**Drop these first under compression.** Rules 34, 36, 37, 39 (redundant cases, decision tables, state transitions,
property tests beside examples) — real, but they apply to a minority of changes and ISTQB is one click away. Rules 26
and 31 (diff direction, test naming) — the wording skill and the doc-comment skill already sit next to them. §2's
candidate table entirely. The bucket count in §1.

**Do not do these.**

- **No wording rules.** Whether a name reads well, whether a message hedges, tense, dialect, article usage: all
  `english-developer-style`'s. The rules here decide what a name and a message must *contain*, never how it is
  phrased. Rule 31 is a content rule; the phrasing of the name is not.
- **No re-derived doc-comment rules.** The comment above a test belongs to `javadoc-authoring`, `godoc-authoring`,
  `pythondoc-authoring`, `rustdoc-authoring`, or `jsdoc-authoring`. The skill may say a regression test names the
  defect it guards; it may not say how the comment is written.
- **No commit or description rules.** The two-run evidence in a pull request (rule 8) is a *content* requirement;
  where it goes in the description is `change-description-authoring`'s.
- **Never promote an asserted row to studied.** Google's book, the Go wiki, and superpowers are unmeasured, however
  authoritative. The studied claims are exactly seven: coverage does not establish effectiveness; mutants correlate
  with real faults; assertions correlate with effectiveness; surfacing mutants in review changes what developers
  write; the flake cause proportions; the smell prevalence-versus-harm gap; the agent mock ratio. Nothing else.
- **Never present a framework convention as a universal rule.** `got, want` is Go's. `expected, actual` is JUnit's.
  `assertThat(actual)` is the fluent libraries'. `assert_eq!` labels its operands `left` and `right` and prescribes
  nothing. A message adds in JUnit, pytest, Vitest and `assert_eq!`, and replaces in AssertJ's `withFailMessage`,
  Rust's `assert!`, and node's `assert.ok`. Ship §4; do not average it.
- **No research provenance in the skill body.** No sample sizes, no paper titles, no percentages in the rules
  themselves. "Coverage is not evidence a test can fail" is the rule. That 31,000 suites were measured to establish
  it belongs in a references file or nowhere.
- **Do not ship the smell catalog.** Three smells survived (§8). Shipping Meszaros's eleven, or tsDetect's nineteen,
  imports a detector that misclassified over 70% of what it looked at.
- **Do not ship a test-count target.** Not the pyramid, not the honeycomb, not Google's 80/15/5. Ship the size
  constraints instead, which an agent can check from the file.
