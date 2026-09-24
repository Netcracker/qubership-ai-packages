# problem-report-authoring

An APM package that governs **what a problem report establishes before it is written, what each part
of it carries, and how a reviewer detects a bad one without the author present**. It covers the
artifacts that share one structure: a bug report, filed in any tracker or sent to a mailing list, in
someone else's project or your own, a feature or change request, a question when you are not sure
the behavior is a defect, a support ticket to a vendor, and a short problem message to a colleague.

The package exists because an agent that has just finished investigating something reaches for the
form it already has, the pull request description, and applies it to an issue. That form is written
for a reader who holds the diff and already knows something was wrong. A triager knows neither the
defect nor the reporter's code, and a report written in that shape opens with a theory about someone
else's internals.

## What it covers

- The five readers: the triager with a minute per item, the maintainer deciding whether to act, the
  contributor who picks the work up months later, the searcher who arrived with the same error string,
  and the colleague reading three lines of chat.
- The work that happens before any prose exists: isolating which project owns the defect and
  reproducing on a supported version; then reading that project's form, contribution guide, AI
  policy, security channel, markup and support window; searching the tracker or the list archive and
  recording the search, and what a comment on a report that exists already carries; deciding how
  many reports this is.
- The framing rules: symptom before mechanism, with a library's public API counted as the symptom's
  surface, a title that names the symptom rather than the fix, causal analysis marked with its
  confidence and the report standing without it, the goal as well as the step, and the project's own
  field order and field meaning winning over any preference in the skill.
- The expected-behavior test: seven questions covering what a machine could check, whether it
  separates acceptable from unacceptable behavior, identifiers that resolve by content rather than
  by position, the grounding and its strength with a compatibility promise counted as the project's
  own specification, whether every claim about today's behavior was observed or cited, one block
  per actionable problem with the requirement separated from the rendering, and, where the obvious
  shape is impossible, a block that says so.
- Length: the core written first, the reader deletion test that keeps a sentence only if some
  reader of the report loses an established answer without it, and the hand-over note as the place
  for what the investigation checked on the way.
- Evidence and the reproducer: who produced each transcript, the secrets removed in every channel
  and the private names substituted only where the channel leaves the organization, with the
  reproducer kept runnable, the observation set that replaces a reproducer for an incident, a flaky
  failure, or a crash on a user's device, the extract that stands in for evidence too large to
  attach, the conditions a measurement carries, what a reproducer must contain, the stop condition
  for reducing it, running what you ship, the form each channel accepts, text where the artifact is
  text and an image where the defect is visual, and the run link where the project runs reproducers.
- The section order where no form exists, and the obligations projects write for reports produced
  with a tool, with the consequences they attach.
- The reports that satisfy every rule and are still useless, each with the check that catches it.
- What the agent raises and the human decides, and the hand-over note that carries what the agent
  could not do.

## Contents

- `.apm/instructions/problem-report-authoring.instructions.md`: the trigger merged into `AGENTS.md` /
  `CLAUDE.md` by `apm compile`.
- `.apm/skills/problem-report-authoring/SKILL.md`: the rules, the expected-behavior test, the vacuous
  shapes, and a review checklist. It names no report and carries no sources or figures: the accepted
  reports and the drafts they replaced are in `references/worked-cases.md`, and the sources stay in
  the research directory below.
- `.apm/skills/problem-report-authoring/references/project-conventions.md`: what to establish
  before writing and where each platform keeps it: GitHub, GitLab, Jira and Bugzilla, mailing lists,
  and a team's own backlog, with the rules the backlog reduces.
- `.apm/skills/problem-report-authoring/references/request-genre.md`: the slots of a feature or change
  request, and why its opening is inverted.
- `.apm/skills/problem-report-authoring/references/question-and-support-ticket.md`: the question
  filed where the project takes questions when you are not sure it is a defect, and the support
  ticket to a vendor with no source and no public tracker.
- `.apm/skills/problem-report-authoring/references/colleague-message.md`: the short form, what carries
  over to it, and what lapses.
- `.apm/skills/problem-report-authoring/references/machine-authorship.md`: the disclosure and brevity
  obligations, and what they do not settle.
- `.apm/skills/problem-report-authoring/references/worked-cases.md`: six cases worked end to end,
  and published before-and-after pairs.

## Pairs with

- The developer-style skill of the language the report is written in, such as
  [`english-developer-style`](../english-developer-style/) or
  [`russian-developer-style`](../russian-developer-style/), owns wording, tense, sentence length, and
  dialect. This package decides what the report contains and in which order; that one writes the
  sentences. Install both.
- [`change-description-authoring`](../change-description-authoring/) governs the commit message, the
  pull request description, and the changelog entry: the artifacts whose readers already know what was
  wrong. This package governs the artifact that has to establish that in the first place.
- [`test-authoring`](../test-authoring/) governs the regression test a confirmed defect owes.

## Research

The rules come from a two-pass deep-research pipeline: project contribution guides and issue forms,
practitioner essays, enhancement-proposal processes, current project policy on machine-written
reports, and empirical work on what bug reports contain and which reports get fixed. Every figure was
verified against its primary source, and the corrections are recorded. The sources, the conflicts
between them, the rules that had to be derived rather than sourced, and the audit of the maintainer's
starting rules are in
[`research/problem-report-authoring/`](../../research/problem-report-authoring/README.md).

Tests: the reports the skill produces on known cases, per model, are in
[`research/problem-report-authoring/cases/`](../../research/problem-report-authoring/cases/).

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/problem-report-authoring
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/problem-report-authoring@<ref>
```

Replace `<ref>` with the release tag, branch, or commit SHA you want to pin.
