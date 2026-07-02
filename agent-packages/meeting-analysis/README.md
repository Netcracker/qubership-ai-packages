# meeting-analysis

A skill that turns a meeting transcript or recording into a dense, verifiable report. Instead of a chronological
retelling, it runs a multi-axis breakdown: several narrow passes over the text, each through a single lens, pulling out
only what that lens is about. Decisions, tasks, open questions, arguments, and trade-offs each land in their own
section, with timecodes and verbatim quotes that point back to the source.

The skill is user-invoked: hand the agent a transcript and ask it to analyze the meeting, break down the call, pull out
the tasks, or lay out who argued for what.

## What it does

1. Reads the transcript end to end to catch the overall context and identify the conversation type — feature planning,
   an argument over a trade-off, a run through UI problems, a review, a cross-check against a methodology.
2. Chooses the analysis axes that fit the conversation, from a catalog or invented for the case at hand.
3. Makes one pass per axis, pulling out only what belongs to that lens, then deduplicates so each thought lives in one
   place and compresses the draft into verifiable claims.
4. Writes the report next to the transcript, in the transcript's own language.

The report carries its own verification apparatus: timecodes on every decision, task, and argument, and verbatim quotes
on each side of an argument. Priorities are marked only when the meeting stated them — the skill does not invent its own
ranking, and it drops small talk unless a decision slipped into it.

The report is written in the same language as the transcript, regardless of the language the request was made in: a
Russian transcript gets a Russian report, a German transcript a German one.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/meeting-analysis
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/meeting-analysis@<ref>
```

Replace `<ref>` with the release tag, branch, or commit SHA you want to pin, for example `v1.0.0`.

Then run `apm install`. The skill deploys to the location your agent reads (`.agents/skills/`, `.claude/skills/`,
`.cursor/`, ...).

## Requirements

- A meeting transcript or diarized conversation text (`Speaker 1` / `Speaker 2`, timecodes) as input — the skill
  analyzes text, it does not transcribe audio.
