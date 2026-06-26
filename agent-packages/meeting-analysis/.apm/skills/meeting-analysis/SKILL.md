---
name: meeting-analysis
description: >-
  Turn a meeting recording or transcript into a structured report through
  multi-axis analysis. Trigger when the user hands you a call transcript, a
  meeting recording, or diarized conversation text (Speaker 1 / Speaker 2,
  timecodes) and asks to "analyze the meeting", "break down the call", "summarize
  the call", "what did we decide", "pull the tasks out of this conversation", or
  "lay out who argued for what". Works for any conversation type and in any
  language — the report is written in the transcript's own language. NOT for
  transcribing audio to text (that is the input, not the job) and NOT for short
  chat threads.
---

# Meeting analysis

Turn a meeting transcript into a dense, verifiable report. Not a play-by-play
retelling, but a **multi-axis breakdown**: you pass over the text several times,
each time through a single lens, and pull out only what that lens is about.

## Output language

**Write the entire report in the same language as the transcript.** A German
transcript gets a German report, a Japanese transcript a Japanese report — match the
transcript, not this skill's language and not the language the request was written in.
The reader works in the source language, so switching it would force them to translate
back. Headings, axis names, and prose all stay in the transcript's language; quotes are
verbatim regardless.

## Why this, not "summarize in order"

After a conversation a person holds the whole context at once — they see the meeting
from every side simultaneously. A linear summary cannot reproduce that: it follows
the chronology and smears the meaning. One narrow pass per axis catches what a broad
retelling blurs. An argument stretched across 40 minutes with back-and-forth
collapses into one clear fork; tasks scattered through the whole conversation
converge into a single list. Several targeted passes almost always beat one wide one.

## Input

The skill takes either a single transcript file or a **folder**. If a folder holds
several transcript files, it is almost always one meeting or a close span of time
split into parts (several back-to-back calls, or one meeting across several files).
In that case:

- Load **all** the files and analyze them **as one large transcript** under the same
  rules — one report, one set of axes, deduplication across the whole. Do not produce
  a separate breakdown per file and do not split the report by file.
- The only difference is in the verification apparatus: a timecode must point to
  **both the source file and the minute**, or the reference is ambiguous (see below).
  Give each file a short label and cite it by that label.

If the folder clearly holds something other than a transcript (screenshots, notes,
attachments), use it as context, but the conversation stays the axis of the report.

**Transcript file name.** A transcript is usually named after the meeting — the date
and a title, e.g. `2026-06-01 Sprint Planning.md`. Use the name to tell transcripts
apart from other files in the folder, and take the source label for timecodes from the
title (`Sprint Planning` → `SP`).

## Process

### 1. Holistic read

Read the transcript end to end (and for a folder, all files in sequence) without
writing anything down. The goal is to catch the overall context and identify the
**conversation type(s)**: was it feature planning? an argument? a run through a list
of problems? a cross-check against theory? One meeting usually carries several types
at once. Note the timecode format and who is who (Speaker 1 / Speaker 2 → names and
roles).

### 2. Choosing axes

The conversation type gives rise to **axes** — the lenses you want to pull
information under. Take the fitting ones from the catalog below and **invent your
own** if the conversation does not fit the catalog (see "How to invent an axis").
Fix the list of axes for yourself and give one line per axis on why it is there. This
choice is the heart of the breakdown; do not stamp one template onto every meeting.

### 3. One pass per axis

One axis at a time, go through the transcript again and pull out **only** what
belongs to that lens. Each item is the semantic core of a thought: enough to
understand it, but compressed. Place the verification apparatus (timecodes, quotes)
by the rules below.

### 4. Deduplication

One thought lives on one axis. If a fact touches two axes, put it where it is **most
actionable** (a decision → "Decisions", the work that follows from it → "Tasks") and
cross-reference it from the other axis instead of repeating the text.

### 5. Compression

Go over the draft with fresh eyes and cut the filler. Each item should read as a
verifiable claim, not a paragraph of reasoning. The denser it is, the more useful.

### 6. Writing the file

Save the report (see "Output").

## Verification apparatus

A claim must be verifiable against the transcript — but not at the cost of the report
swelling. The rule on the "weight" of the apparatus:

- **Timecode required** on conclusions/decisions, tasks/next steps, and arguments.
  These are what people act on and cite later, so navigation to the source must always
  be there. Format it as in the transcript: `[11:49–12:50]` or `[1:37:30]`. A timecode
  is a real reference: give the exact one, or the nearest one you know. **Never write a
  placeholder like `[20:xx]`** — the timecode of the whole block beats a made-up
  minute. If the transcript is assembled from several files (a folder), give both the
  file and the minute: `[<file label> 11:49–12:50]`, otherwise it is unclear which
  source to search.
- **Verbatim quote required on arguments** — on each side's original position. An
  argument is easy to reword after the fact into a convenient form; to keep the
  original, unaltered position visible, quote it exactly (`"…"`) rather than paraphrase.
- **Otherwise a quote is optional, and only if it carries meaning.** A quote earns its
  place when it reveals the substance: an argument, a position, a vivid phrasing, the
  content of a decision itself. A quote that merely confirms a claim already stated adds
  length without value — drop it and keep the timecode. You can always add a timecode;
  a quote, not always.

  Bad (the quote duplicates the claim and reveals nothing):

  > - The "manager works the floor themselves" case is already handled. [07:06–07:31]
  >   Denis [07:28]: "There's no problem here. I've already accounted for it, nothing to do."

  Good (no sharp quote → claim plus timecode, no quote):

  > - The "manager works the floor themselves" case is already handled in the model,
  >   nothing left to build. [07:06–07:31]

## Priorities and importance

Rank and mark importance **only if it was stated explicitly in the meeting**: someone
said "this is a blocker", "super important", "first thing", "P0", "let's defer it".
Then reflect it (with a weight marker, ordering, or a separate line) tied to the
source.

**Do not invent priorities or rank by your own sense of things.** If there was no
weighting in the conversation, the order of items = the order they came up in, or a
logical grouping, with no evaluative markers.

## What to drop

Small talk and tangents — cars, family, weather, idle chatter about nothing — leave
out. Exception: if a decision, signal, or context that affects the work slipped into
the small talk, pull that out and discard the rest of the wrapping.

## Axis catalog

A starting palette. Take the fitting ones; do not drag in all of them. The order of
axes in the report runs from most actionable to reference; "what you might have
missed" always comes last.

1. **Tasks / next steps** — almost always present. An actionable list of what you came
   out with. If tasks have different owners, split by person (Denis / Anton / joint).
   Timecode required.
2. **Decisions made / confirmed hypotheses** — what was fixed as an agreement. Timecode
   required.
3. **Open questions** — raised but not resolved; needs a next step. State the question
   itself clearly, not the discussion around it.
4. **Arguments / trade-offs** — where positions differed. Set the positions side by side
   and show the outcome. Template below.
5. **Product hypotheses / ideas** — for generative meetings: a structured description of
   the idea you can work with afterward.
6. **Pains / problems** — what hurts for the other person and what solution they are
   looking for.
7. **Problem run-through** — when you ran through a pile of unrelated problems (UI,
   bugs): a flat list, each one a problem plus the decision taken on it.
8. **Feature planning** — a structural description: why, how it works, edge cases, what
   is in scope / what is deferred. Should be usable as input to a task or tech design.
9. **Cross-check against a concept/theory** — if the conversation fell under a framework
   (Goldratt / TOC, Lean, an industry standard): a mapping of the conversation onto the
   theory. Highlight **both matches and divergences** — divergences are worth more.
10. **What you might have missed / ask separately** — the closing axis. Gaps, things
    raised-but-unresolved, ambiguities, what is worth coming back to.

## How to invent an axis

If the conversation does not fit the catalog, ask yourself: "on which single question
do I want a distillation of this conversation, so I can act on it afterward?" Each such
question is a candidate axis. A good axis: (a) answers one coherent question, (b)
gathers material scattered through the text into one place, (c) yields items that are
verifiable against the transcript. Name the axis so the heading makes clear what is
inside.

## Item templates

**Argument / trade-off** (positions side by side plus outcome):

```
### <short name of the fork>

> **Status: UNRESOLVED** — <where it was deferred>   (or drop this line if resolved)

| For <option A> (<who>) | For <option B> (<who>) |
|---|---|
| <compressed argument> | <compressed argument> |

- Original position A — <Name> [timecode]: "verbatim quote"
- Original position B — <Name> [timecode]: "verbatim quote"

**→ Decision:** <option> chosen [timecode]. <rationale, if any>
```

**Decision / task:**

```
### <name>
- <compressed core of the decision or task>. [timecode]
  (opt.) <Name> [timecode]: "quote — only if it reveals the substance, not a duplicate of the claim"
```

**Cross-check against theory:**

```
### Cross-check against <theory>
- **Matches:** <what from the conversation maps onto the theory>
- **Diverges:** <where the conversation departs from the theory and why>
```

## Output

Save the report next to the transcript, named after it (e.g.
`<transcript-name>-analysis.md`), so the breakdown sits beside its source. The report is
written in the transcript's language (see "Output language").

Report header. First comes the **"What the meeting was about"** paragraph — a triage
element: from it the reader understands the topic, the outcome, and whether to read on,
in 10 seconds. Do not hide it in a `>` block quote and do not collapse it into one line
with metadata — it is the first thing a person sees, and readability here matters more
than compression. Give participants as a list, not one line: the first impression of
the document matters more than saving lines.

```
# Meeting breakdown <with whom> — <date>

**What the meeting was about.** <one paragraph: the topic, why you met, and the main outcome.>

**Participants:**
- <Name> (<role>) — Speaker 1
- <Name> (<role>) — Speaker 2

**Analysis axes:** <list the chosen axes>.
**Transcript:** ~<length>.

---
```

If the breakdown is assembled from several files, add a **"Sources"** block to the
header with the labels you cite in the timecodes:

```
**Sources:**
- `SP` — 2026-06-01 Sprint Planning.md (~3 h)
- `BR` — 2026-06-02 AI Branding.md (~20 min)
```

Extended context, if needed, goes in a separate paragraph after; but the "What the
meeting was about" paragraph is required and comes first.

Next come the per-axis sections (`## 1. ...`, `## 2. ...`), with items inside as
`### N.M`. Keep the density and style of the templates above. Translate the section
labels shown above into the transcript's language when you write the report.
