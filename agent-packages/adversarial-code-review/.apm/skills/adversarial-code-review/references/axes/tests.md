# Axis: tests

Load `test-authoring`, and read its references for the project's test engine and assertion library. Follow the
repository's own test rules from `input.md` (for example, how cases are grouped into files).

## Check

- Which tests the change owes, by `test-authoring`: every case the description, the commit messages, and the changed
  comments claim, the boundaries and invalid partitions of each, and the negative control. A claimed case with no test
  is a finding; name the case.
- Each new test can fail: it asserts the behavior the change adds, and would fail without the change or with a plausible
  wrong implementation. A test that asserts nothing meaningful, asserts the mock, or passes on the old code is a
  finding. Where you can run the test cheaply against the base revision, do it in your own worktree at the base and
  record the result as a `fact`.
- Every new or changed test against `test-authoring`'s review checklist, item by item, including its name, how its
  expected values are produced, what its assertions print, whether each case fails on its own under its own name, and
  its shape beside its neighbors. Where the neighbors' shape breaks the skill's rule on separate cases (independent
  cases chained in one act that stops at the first mismatch), the skill wins for the new test, and the neighbors are not
  a finding. A shape the repository's rules name wins over both.
- CI status is supporting evidence, not the review result.

## Measurements

Do not rerun the measurement. Where the reports come from cribro, load the `cribro` skill if it is installed: it says
what each line of its reports means.

Start from `<work>/measure/README.md`, which says what ran. Where the reviewed head does not build, or a test the change
touches fails on it, that is a `major` finding, with the output from `<work>/measure/` as `fact`.

Where `<work>/measure/` holds reports, read them before the tests. Every changed line no test executes, every changed
branch the report lists as not taken, and every live mutant on a changed line (one that survived, or that no test
reached) either goes into a finding or is set aside with its reason:

- It goes into a finding when the line carries behavior the change adds or claims: no test would fail if that behavior
  broke. Group by behavior, not by line: five mutants on one predicate that no test asserts are one finding, and its
  evidence lists the lines and the mutants, quoted from the report as `fact`.
- It is set aside when the mutant is equivalent (say why), when the line only logs, or when the line carries a
  `diff-coverage: ignore` marker whose reason holds. A marker whose reason does not hold is a finding.
- It is set aside as well when a test the tools did not run (`<work>/measure/README.md` lists them) executes the line or
  would kill the mutant; name that test.

A killed mutant shows that some test fails on that single mutation. It does not show that the test written for a claimed
case checks that case, so the check above still applies to every claimed case.

## Not a finding

An extra test beyond what the change owes, or a test the reviewer would have structured differently with no cost to a
reader. Do not ask to split a source file that holds many cases of one rule.

## Severity

A claimed behavior with no test, or a test that cannot fail, is `major`; so is an unexecuted line, an untaken branch, or
a live mutant on a path the change claims. A missing boundary or negative case is `minor`, and so is an unexecuted line,
an untaken branch, or a live mutant on a path the change does not claim. A checklist item a new test fails (cases that
mask each other, an expected value built from the input, an assertion that prints nothing) is `minor`, unless it leaves
the test unable to fail, which is `major`.
