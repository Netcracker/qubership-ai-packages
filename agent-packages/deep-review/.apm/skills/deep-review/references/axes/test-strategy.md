# Axis: test strategy

Finding prefix: `TLVL`.

Whether each behavior is tested at the level that can catch its failure soonest and most precisely, and whether the
spread of tests across levels matches where this system's defects live. The `tests` axis asks whether a broken line
would turn something red. This axis asks which level turns red, how long it takes, and whether that level can see the
failure at all: a rule checked only through a browser, a query checked only against a mock of the database, a
contract between two components checked by neither side.

The rules of level come from the `test-authoring` skill, at the path your prompt gives. Apply §1 (a test exists to fail,
so a level that cannot observe the risk pins nothing), §3 (the smallest level at which a behavior is observable, and a
second, larger test where a real dependency, wiring, persistence, or a process boundary adds a failure mode the small
one cannot see), §4 (partitions and boundaries belong where enumerating them is cheap), §8 (which causes of flakiness
come with a level), and §10 (which bucket a claim sits in). The small, medium, and large definitions of §3 classify a
test by what it touches, not by the directory it lives in. Sections §5, §6, §7, §9, and §11 judge single tests and their
assertions, and are out of scope here: a weak assertion, a poor name or failure message, a mystery guest, DAMP against
DRY, or a mock asserted on is `tests`' finding or nobody's.

You may be given `paths` for one component. Tests outside them still count where they pin behavior inside them, such as
a repository-wide end-to-end suite: find those, and say in your coverage which levels and components you measured and
which you did not.

## What counts as a finding

- **Logic pinned only by a slow or remote level.** A validation rule, a permission matrix, a computation, or a mapping
  whose only tests are end-to-end, UI, or API-collection tests, where a small test through the unit's interface could
  observe it (§3). The consequence is concrete: the partitions and boundaries of §4 go untested because each case
  costs a browser session, and a failure names a screen rather than the rule.
- **A mock standing in for the peer whose behavior is the risk.** Code whose correctness depends on what a database,
  queue, cache, file system, or another service actually does (SQL dialect, constraints, transactions and isolation,
  ordering, redelivery, serialization, status codes) is tested only against a double, and no medium test runs it
  against the real peer or a faithful local instance (§3, second test). Name the property of the peer the double
  cannot reproduce; without one, this is a preference.
- **An in-repository contract no test pins from both sides.** Two components of this repository meet at an API spec,
  a generated client, a message schema, a shared database table, or an event format. The producer's tests check what
  it emits, the consumer's tests feed hand-built input, and no shared artifact, contract test, or schema check ties
  the two, so either side can drift with both suites green.
- **A critical user journey with no large test.** A path the profile, the docs, or the focus names as core (sign-in,
  the main create-and-publish flow, an upgrade path) has tests for each layer and none for the wiring between them.
- **Flakiness caused by the level.** A check that needs no process boundary runs across one, and inherits timing,
  ordering, or environment nondeterminism from it, while a deterministic version of the same check exists one level
  down: retries configured for the suite, quarantine tags. The repair is moving the check down a level. A cause
  visible in the test's own file, such as a `sleep` used as a wait, is `tests`' (§8).
- **A component with no tests of its own.** A library, module, or service whose only coverage is another component's
  end-to-end suite, so its own contract is pinned only as far as one consumer happens to use it.
- **A suite that tests a library or framework.** A large share of tests asserting that the ORM saves, the router
  routes, the serializer serializes, or generated code matches its generator, while the project's own decisions go
  untested at that level (§6 calls this the framework's test; here it counts as misspent level budget). State the
  count: framework tests against all tests at that level, from the classification of step 1.
- **A distribution the defect history contradicts.** The fix commits show defects in one layer (persistence, wiring,
  configuration), and the suite puts its tests elsewhere; or most of the wall-clock goes to large tests that repeat
  checks the small tests already make.

## What is not a finding

- Anything about a single assertion, test name, failure message, fixture style, or helper (§5, §6, §7, §9, §11).
- A behavior with no test at any level: that is `tests`' unpinned behavior. This axis reports a behavior pinned at the
  wrong level, or only through a double that cannot see the risk.
- A pyramid, trophy, or ratio held up as the goal. A distribution is a finding only through a named behavior it
  leaves pinned late, imprecisely, or not at all.
- A missing large test for a path that is not critical, or a missing medium test where the double is a faithful fake
  and the peer adds no failure mode you can name.
- A level the repository's own test strategy chooses with a reason. Cite the document; report only where the code
  departs from it, or where following it leaves a named risk unpinned.

## Method

1. **Classify and count.** Per component, sort every test into small, medium, contract, and large (end-to-end or UI)
   by what it touches: a browser driver, testcontainers or compose, a database URL, a socket to localhost, a Postman
   or Newman collection, a build tag, a test category. Count with the runner, not by eye (`pytest --co -q`,
   `go test -list .`, `npx jest --listTests`, `npx playwright test --list`, surefire or JUnit XML reports, the number
   of requests in a collection).
2. **Time each level.** Run each level that `00-commands.md` can run, and take per-test timings from the runner's
   report. Where a level needs infrastructure you lack, take timings from recent CI logs (`gh run view --log`) and
   say so. Record the median and the slowest ten per level.
3. **Map critical behaviors to levels.** Take eight to fifteen behaviors from the profile, the focus, the docs, and
   the public API surface. For each, find the tests that pin it (grep the route, handler, function, or UI label), note
   the level of each, and the smallest level that could observe it per §3.
4. **Sample the large tests.** Take every large test if there are fewer than thirty, otherwise a sample of fifteen
   across suites. For each, name the logic its assertions check and decide whether the check would still hold with
   every peer faked. Where it would, look for a small test of that logic; none found is a candidate.
5. **List the doubles at the boundaries.** Grep for mocks and stubs of repositories, database handles, HTTP clients,
   queue producers and consumers. For each peer, look for a medium test with the real one. Where none exists, probe
   in a throwaway copy: break the peer-facing artifact (a column name in SQL, a field in a message, a route path) and
   run the small suite. Green there and red only in a large suite, or nowhere, is executed evidence for the level gap.
6. **Walk the in-repository contracts.** From the profile, list each place two components meet. For each, name the
   producer-side and consumer-side tests and the artifact they share, if any. In a sliced run, a contract that
   crosses two slices belongs to the slice holding the consumer.
7. **Read the history.** Sample ten to twenty fix commits. For each, note which level its regression test landed at
   and the smallest level that could have caught the defect. Read the flake record too: retry settings, skip or
   quarantine annotations, and reruns in CI, each attributed to a level.

## Required section

End the report with **Test levels by component**: one row per component, `not measured` with a reason where you could
not measure, never a blank cell.

| Component | Small: tests, wall-clock | Medium | Contract | Large / UI | Measured how |
| --- | --- | --- | --- | --- | --- |

Follow it with **Critical behaviors and their level**: one row per behavior from step 3.

| Behavior | Why critical (source) | Smallest level that observes it | Tests that pin it, with level | Gap |
| --- | --- | --- | --- | --- |

## Severity

Rate by what the misplaced level lets escape, or how late it reports it. A critical journey with no large test, or a
peer whose real behavior already caused a defect in the history and is still tested only through a double, is `HIGH`.
A contract between two components that can drift with both suites green is `HIGH` where a released consumer breaks
silently, otherwise `MEDIUM`. Logic pinned only by large tests, a component with no tests of its own, and level-caused
flakiness that has forced reruns or quarantine are `MEDIUM`. A suite that mostly tests its framework, or a distribution
that costs minutes and lets nothing escape, is `LOW`.

## Ownership

| Concern | Owner axis |
| --- | --- |
| A behavior no test pins at any level; a test that cannot fail; a missing harness for a defect class (fuzzing, race detection, injected clocks); coverage and mutation figures; a suite too slow to run on every change | `tests` |
| Which level pins a behavior; a double standing in for a real peer where a medium test is owed; checks misplaced into large suites; level-caused flakiness; the per-component distribution | `test-strategy` |
| A flaky test whose cause is visible in its own file (§8 table) | `tests` |
| Whether producer and consumer inside the repository agree today | `contracts` |
| Whether a test would catch them drifting apart | `test-strategy` |
| Executing a finding against a real environment to settle it, including a claim that a double hides the peer's behavior | `runtime-verification` |
| Which suites CI runs, on which events, which checks are required, and what may fail | `build-release` |
| Code with no seam a small test could use, so a behavior can only be tested large | `architecture`, as a cross-axis note; the level gap itself stays here |

When you find a live contract mismatch, it goes to *Cross-axis notes* for `contracts`, and you do not also report the
missing test for it. When a behavior turns out to have no test at any level, it goes to *Cross-axis notes* for
`tests`.
