# Axis: documentation and onboarding

Finding prefix: `DOC`.

Judge the documentation as a product with two users: a developer who has never seen this repository, and an AI agent
with no access to its source. Both should reach a first working result without reading the implementation.

Do not review prose style. Review whether the reader can act.

## The drill

Run it, do not reason about it. Starting from the `README` alone, and without reading any source:

1. Work out what this thing is for and whether it fits your problem. How many lines does that take?
2. Install or depend on it, using only what the docs say. Record every step that did not work.
3. Get the simplest useful result — one message sent, one query run, one resource created. Copy the documented
   example verbatim and run it. Does it compile? Does it run? Is it complete, or does it assume setup nobody wrote
   down?
4. Do the second most common thing (configure a timeout, handle an error, close cleanly). Is it documented at all?
5. Break something on purpose and look up the resulting error message in the docs. Does it appear?

The transcript of that drill, with the exact failure points, is the core of the report. Each point where you had to
read the source, guess, or search elsewhere is a finding.

## Then check

- **Accuracy.** Documented behavior against actual behavior: defaults, units, option names, output formats, exit
  codes. Documentation that is wrong is worse than documentation that is missing, and rates higher.
- **Coverage of the contract.** Every public entry point: what it does, what it requires, what it returns, what it
  throws, what it retains, what thread it runs on. Gaps here are `api-ux` when they concern naming and this axis when
  they concern the missing sentence.
- **Reference completeness.** Every configuration option, environment variable, and error code the code can produce
  appears somewhere a reader would look. Produce the gap list mechanically: grep the code for the identifiers, grep
  the docs for each. That list is the single most useful artifact this axis can produce.
- **Operations material** for services: a symptom-to-cause-to-action table, and a recovery procedure for every
  terminal state the code can reach.
- **Currency.** Docs describing a version that no longer exists, examples using removed APIs, dead links, a changelog
  that stops before the last release.
- **Machine readability.** Can an agent parse the reference material — stable headings, tables, enumerated values —
  or is the contract buried in prose?

## Rules

Every finding names the document and the reader's blocked action. "The README is thin" is not a finding; "the README
never says which artifact coordinate to depend on, so step 2 of the drill required reading `pom.xml`" is.
