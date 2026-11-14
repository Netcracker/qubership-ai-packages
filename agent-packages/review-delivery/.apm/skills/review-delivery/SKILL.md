---
name: review-delivery
description: Render a finished code review (a review.json file) as a chat report, a ledger file, an email, a GitHub pull request review, or GitLab merge request discussions, and publish it with the user's authorization. Use when a review skill hands over its review.json, or when the user asks to post, draft, email, or write out the findings of a review that already ran.
---

# Deliver a code review

This skill turns a finished review into the form the user asked for. It does not review: it never adds, drops, or
re-grades a finding, and it never reads the code to decide whether a finding holds. The one field of `review.json` it
writes is `follow_up_url` (see *Follow-up issues*). Its input is a `review.json` that
follows [the schema](schema/review.schema.json), written by `adversarial-code-review` or by another review skill.

Read the file and check it against the schema before rendering. A file that does not validate goes back to whoever wrote
it, with the failing field; do not repair it here.

## Choose the renderer

Render what the request names. With no request, render the chat report. The ledger is written whenever the chat report
is: the chat report points at it.

| Renderer | Output | Writes outside the machine |
| --- | --- | --- |
| chat | the report in the conversation | no |
| ledger | `ledger.md`, every finding, grouped by class | no |
| email | `email.md`: a subject line and a plain body the user sends | no |
| GitHub | a pending or submitted review on the pull request | yes |
| GitLab | Draft Notes or published notes on the merge request | yes |

Only the last two need authorization (see *Publish to a platform*).

## Rules for every renderer

**Language.** The chat report uses the language of the user's request. The ledger is in English, the language of
`review.json`, because a script renders it. An email and a platform publication are in English unless the user names
another language. Translate headings and labels; keep identifiers,
paths, severities, and result labels as they are.

**Every finding is rendered.** There is no cap on the number of findings: the user reads the draft and deletes what is
not worth sending. The exceptions are held findings (next paragraph), findings an earlier round already settled, which
appear only under *Previous findings*, and the findings *Findings the change did not make* keeps off the platform.

**Held findings.** A finding with `gate: code_settled` asks for something about the branch rather than the code: squash
the commits, rebase, reword a commit message. While any other `major` or `minor` finding (one with `gate: none`) is
open, do not publish it: the next round rewrites the history anyway. A finding counts here where it has `origin: change`
(or no `origin`), or `disposition: extend_scope` and no `follow_up_url`; only a `change` finding is ever held. An
earlier thread that `previous_findings` lists as `fix_not_accepted` counts at the severity of the finding its
`finding_id` names, and as open where it names none in this file. Held findings are not counted in the result line of
an email or a GitLab publication, which shows only what it publishes. The ledger lists them in their own section, so
nothing is lost, and the chat report counts them on its own line.

**Order.** Major before minor before nit; within a severity, by id, which the verifier assigns in severity order. In the
ledger, by class first, and the classes, with the findings without a class as one more group, by their highest severity.

**Result line.** The same in every renderer that shows it, with every severity counted, zeros included. It counts only
findings with `origin: change` (or no `origin`): the others do not decide the result. A GitHub review
shows it only for `REVIEW_INCOMPLETE` (see *Content*):

```markdown
Result: REQUEST_CHANGES (1 major, 2 minor, 3 nit)
Result: APPROVE (0 major, 1 minor, 0 nit)
Result: REVIEW_INCOMPLETE
```

`REVIEW_INCOMPLETE` has no counts, because the totals may be incomplete, and is followed by `Coverage: <coverage_gap>`.
Never write `Coverage: complete`.

**One finding**, in an email and on a platform: the first line, then each part below that is not empty.

```markdown
**F36 minor** The no-usable-key error copies every skipped key's reason, unbounded and unescaped, into each failed load.

Problem: a 1 MiB JWKS gives a 26.8 MB error; a raw newline from `kty` reaches the log as is; the warning already listed the same keys.

Proposed solution: cap the list at N reasons with "and M more", quote each with %q, and drop the list from the error or from the warning.
```

- The first line is the tag and the claim. A collapsed thread and a notification email show only that line, so the
  claim, from `title`, is a sentence that stands alone. There is no separate title line.
- The tag is `**F<id> <severity>**`: the id, the severity in lowercase, and nothing else in bold. `confidence: medium`
  adds `, medium confidence` inside the bold; `high` adds nothing. `kind: question` adds `, question`, and the claim is
  worded as a question: `**F1 minor, medium confidence, question**`. The tag stays in English whatever the language of
  the rest, so that an agent can match a comment to its finding with `^\*\*F(\d+) (major|minor|nit)\b`.
- `Problem:` is from `problem` and the decisive `evidence`: the evidence and the impact, never a restatement of the
  first line. Where `problem` is empty, the paragraph is absent.
- A `reproducer` follows as a code block tagged with its `language`. One of more than 10 lines goes in a collapsed
  block, so the comment still reads in a few lines:

  ````markdown
  <details><summary>Reproducer</summary>

  ```java
  …
  ```

  </details>
  ````

  An email has no collapsed blocks: there it is `Reproducer:` and the code block.
- `Proposed solution:` is from `proposed_solution`, and may be one phrase where the fix is obvious. Where it is empty,
  the paragraph is absent.
- A `suggestion` follows `Proposed solution:`. In an inline comment that is not a reply to an earlier thread it is the
  platform's suggestion block, which the author applies with one click (each platform reference says how); anywhere
  else, a code block tagged with the file's language. A nit about a comment is usually the first line and this block:

  ````markdown
  **F28 nit** "A lambda's declared return type" reads as the returned lambda's, but the type meant is that of the functional interface method the `return` is in.

  ```suggestion
        // Lambda parameter checking needs the target's nested annotations in the cache. Inside a
        // lambda, the functional interface method may declare a type variable such as R as its
        // return type, so recover the instantiated type from the parent context before caching
        // the returned lambda.
  ```
  ````
- `retest` is not rendered here: the ledger and the next round read it from `review.json`.
- The lead-ins `Problem:` and `Proposed solution:` are plain text, not bold.
- Each paragraph is one line, with no hard wraps: the platform wraps it.
- A finding with `origin: preexisting` adds `, pre-existing` to the tag, after the severity, and changes its last
  paragraph (see *Findings the change did not make*).
- An inline comment carries no location: the platform shows it. Anywhere else, the location follows the tag:
  ``**F50 nit** `internal/x.go:122`, outside the diff: …``. A finding with no location names what it is about in the
  claim (the description, a commit message).

Word an `evidence` item with `basis: inference` conditionally (`can`, `may`, or the condition it depends on). Add
nothing to `problem` and `proposed_solution` beyond the decisive evidence: their length is the review's decision. The
tone is direct and neutral: no praise, thanks, apology, greeting, or closer, and no softening of a defect.

**Scope.** Where `scope_exclusions` is not empty, state it once, near the result: the reader must know what was not
reviewed.

## Findings the change did not make

A finding's `origin` says whose defect it is. The author of this change owes a fix only for `change` findings, so a
comment on any other has to say so, and the comment for a defect that is older than the change points at the issue
that tracks it rather than asking for a fix here.

| `origin` and `disposition` | Email and platform |
| --- | --- |
| `stack` | Not published on this request. |
| `preexisting`, `extend_scope` | Published, with the last paragraph below. |
| `preexisting`, `follow_up`, with `follow_up_url` | Published, with the last paragraph below. |
| `preexisting`, `follow_up`, no `follow_up_url` | Not published. |

The last paragraph of a published `preexisting` finding, in place of `Proposed solution:` and the suggestion:

```markdown
Follow-up: this fails before this change too, so I filed <follow_up_url> to fix it separately.
```

- Write `filed` where this delivery filed the issue, and `it is tracked in <follow_up_url>` where it already existed.
- For `extend_scope`, keep `Proposed solution:` and the suggestion, and add the alternative after them: `Follow-up: this fails before this
  change too. If you would rather keep the change narrow, say so, and it moves to a follow-up issue.` Where
  `follow_up_url` is set, the author already chose the follow-up: render it as `follow_up`.

### Follow-up issues

Before the first email or platform write, and in the chat report when nothing is published, ask once about every
`preexisting` finding with `disposition: follow_up` and no `follow_up_url`:

> F7 and F9 are older than this change. File a follow-up issue for each, and link it from the review?

Filing writes to the tracker, so it needs this answer even where publication is already authorized; a draft mode
authorizes no issue. Where the user agrees, for each finding:

1. Load `problem-report-authoring`, and the developer-style skill of the language the issue is written in
   (`english-developer-style` for English). It searches for a report that already exists and writes the issue from the
   finding's `problem`, `evidence`, `reproducer`, `introduced_by.commit`, `proposed_solution`, `suggestion`, and
   `retest`, at the reviewed head's revision.
2. File the issue in the repository that `problem-report-authoring` finds owns the defect, or link the report its
   search found.
3. Set the finding's `follow_up_url` in `review.json`, and render the ledger again.

Where the user declines, the finding stays in the chat report and the ledger, and is not published: a comment that
names an old defect with no issue to track it asks the author for a fix the change does not owe.

A `stack` finding belongs to the request its `introduced_by.request` names. The chat report lists it under that
request and offers to review that request together with this one, as a stack: the stack review moves the finding to
that request.

## Chat report

```markdown
# Review: <title>

Result: REQUEST_CHANGES (1 major, 2 minor, 0 nit)
Revision: <GitHub: base...head | GitLab: base=<sha>, start=<sha>, head=<sha>>
Out of scope: <scope_exclusions, when present>
Held until the code is settled: <n> findings (in the ledger)

## Previous findings

Fixed since the previous round: <n>.

- [<short reference>](<thread_url>): <status>; <reason, with the decisive replies linked; for a disputed `major`,
  the assessment of each counterargument>.

## Main problems

1. <class title> (<highest severity>): <root cause>. Findings F1, F4, F9.
2. ...

## Findings

- **F1 major** `path/to/file:42`: <claim>
- **F2 minor, medium confidence** ...
- **F8 minor, pre-existing** `path/to/file:120`: <claim>

## Older than this change

- **F7 minor, pre-existing** `path/to/file:88`: <claim>. Follow-up issue: <follow_up_url, or "not filed">.

## Made by other requests

- <introduced_by.request>: **F9 major** `path/to/file:17`: <claim>.

## Needed to complete the review

- <open question and why it can change the result>
```

*Previous findings* counts the `fix_accepted` threads and lists every other one with its reason. The ledger links the
`fix_accepted` threads on one line, and `review.json` keeps their reasons.

*Main problems* lists the classes, ordered by the highest severity among their findings, so the author sees the few
causes before the many symptoms; it is absent when no class has two findings. *Findings* gives each finding one line:
its tag as in *One finding*, its location, and its claim in the request's language. The problem and the proposed
solution are in the ledger, which the chat report does not repeat. *Findings* holds the findings the author is asked
to fix in this change: `change` findings, and `preexisting` findings with `disposition: extend_scope` and no
`follow_up_url`. The other `preexisting` findings go to *Older than this change*, the `stack` findings to *Made by
other requests*, and the question from *Follow-up issues* follows them.
Omit an empty section. End with the path of `review.json`, and of every file this delivery wrote.

## Ledger

The ledger is the input of whoever fixes the findings, and it keeps everything the chat report folds: the class of each
finding, its axis, its evidence, its `retest`, and the held findings. Render it with the script; do not write or edit
it yourself:

```bash
<skill dir>/scripts/render-ledger.py <review.json>
```

It writes `ledger.md` next to `review.json` and prints the path. Its classes hold the same findings as the chat
report's *Findings*, and its *Older than this change* and *Made by other requests* sections the rest. Where it exits
with status 2, `review.json` lacks a field the ledger reads; send the file back with the message, as for a file that
does not validate.

## Email

`email.md` holds a `Subject:` line (`Review of <title>: <result line>`), a blank line, and a plain-text body: the
result, the revision, the out-of-scope line, then the findings in the order above, in the *One finding* form without
the bold markers. Each location is a link to the line at the reviewed head
(`https://github.com/<repo>/blob/<head>/<path>#L<line>`, or the GitLab `/-/blob/<head>/<path>#L<line>` form).
Held findings, and those *Findings the change did not make* keeps off a platform, are left out, as on a platform.
Sending is the user's step.

## Publish to a platform

### Authorization and attribution

Select the mode once. "Publish", "post", or "submit" authorizes immediate publication; "draft" or "prepare comments"
authorizes an unpublished draft. Other replies authorize no write. If no mode was selected, ask after a completed
`APPROVE` or `REQUEST_CHANGES` result:

> Publish now or prepare a draft? To include `Assessed by`, explicitly confirm that you personally reviewed the report
> and agree with its findings.

Do not ask after `REVIEW_INCOMPLETE`, repeat an answered question, or follow up on an ambiguous answer. Once authorized,
proceed without further confirmation.

Include `Assessed by: <publishing account display name, or exact login>` only with explicit confirmation of both
personal review and agreement. Publication authorization, generic approval, or agreement alone is insufficient; omit
the line without asking again. Resolve the publishing account on the target host and never attribute the review to
the user without that confirmation.

### Synchronize discussion state

Only resolve or reopen discussions whose first comment was authored by the publishing account on the same host
(`thread_author`); prefer account IDs. Human or model origin and signatures do not matter. Later replies do not
transfer ownership. Unknown or other original authors mean no state change, even when platform permissions allow it.

Follow-up publication authorizes these operations. In chat, ledger, email, and draft modes, leave published discussions
untouched. Resolution neither approves the request nor dismisses a review.

| `previous_findings` status | Action on an owned discussion |
| --- | --- |
| `fix_accepted` | Resolve without a courtesy reply. |
| `withdrawn`, `resolved_by_clarification` | Explain the reason when retracting a claim or the reason is unclear; then resolve. |
| `fix_not_accepted` | Reply with the condition, impact, and counterargument assessment; keep open or reopen after verifying the reply. |
| `scope_deferred` | Explain and link `follow_up_url`, then resolve without claiming a fix. |
| `unable_to_verify` | Preserve state; request evidence only when the author can supply it. |

A finding with `prior_thread` set is a reply in that thread, not a new comment. In draft mode the reply goes into the
draft too, as each platform reference describes, never as an immediate reply. With no new evidence, skip equivalent
replies and state changes already satisfied.

### Content

Publish each finding once, inline at its `location`. A finding with no location, or with `in_diff: false`, goes into the
general comment.

On GitLab, start the general comment with the result line. On GitHub, leave it out for `APPROVE` and `REQUEST_CHANGES`:
the state of the submitted review (changes requested, or commented) shows the decision. Keep it for
`REVIEW_INCOMPLETE`, which no review state shows. The rest of the general comment is only these parts, in this order:

```markdown
Out of scope: rules of ADR-0091 to ADR-0096 that #202 and #232 implement.

Two things block the merge for me. A key that fails to parse now drops every key of its realm (F31), and no test reloads a realm whose source fails (F33).

F35 and F47 are one change: build the realm summary line in a fixed order, and pin the whole line in its test. The rest are small.

**Not inline**

**F40 minor** Two log texts quoted in the description and the top commit differ from what the code emits.

Problem: …

**F50 nit** `internal/token/keys/timing_test.go:122`, outside the diff: the comment on publish says it sets "the JWKS of every source", which no longer holds for realms.

Reviewed at [`0c8d9fd3`](https://github.com/<owner>/<repo>/compare/3c85f644...0c8d9fd3).
```

The parts are paragraphs with no headings, except the lead-in of *Not inline*, and each is absent when it would be
empty:

- *Out of scope*: one line, first.
- *Previous findings*: only the earlier threads the publishing account does not own, with a status other than
  `fix_accepted`, one line each: `- [F6](<thread_url>): <status>; <reason>`. A `fix_accepted` thread is resolved, the
  other statuses are answered in their own thread (*Synchronize discussion state*), and a remaining defect is a finding
  of this round, so the general comment does not repeat them.
- *What blocks the merge*: one clause for each published `major` finding of this change, saying what goes wrong for
  which input in the author's terms, with its id in parentheses. A commit hash or the inner workings of a method do not
  belong here; the inline comment carries them.
- *Shared fixes*: one sentence per class with at least two published findings, saying which one change resolves them,
  with their ids as plain text. A class left with one published finding is dropped, because that finding already
  stands on its own; a held finding, or one whose comment the user deleted from a draft, is not published. Where
  findings remain that block nothing, a short sentence says so instead of listing them.
- *Not inline*: the findings that cannot be placed inline, each in the *One finding* form, with the location and the
  reason after the tag, and nothing between them.
- *Reviewed at*, last, with `Assessed by` and `Coverage` (for `REVIEW_INCOMPLETE` only) on lines before it: the head as
  a link to the reviewed range. On GitHub that is `https://github.com/<owner>/<repo>/compare/<base>...<head>`: the
  pull request's files view accepts only its own commits, and the base is not one. On GitLab it is
  `<project web_url>/-/compare/<base>...<head>`.

Write the general comment to `review-body.md` next to `ledger.md`, and give the user its path with the review's URL:
GitHub does not show the body of a pending review in its web UI.

The general comment carries what the inline comments cannot: what blocks the merge, the findings that are not inline,
and the fixes that several inline findings share. Do not copy inline findings, their problems, or pointers such as
"See inline comment".

The user may delete inline comments from a draft before submitting it. When they ask for the general comment again,
read the draft's comments back from the platform first (each platform reference says how), match each to its finding
by the tag, and render the general comment from the findings whose comments are still there.

### Write protocol

Write each request body and JSON payload to a file with the agent's file-writing tool, or build the JSON with a script
that serializes the strings, never through a shell heredoc or a quoted command-line argument. A finding's text carries
backticks, `$`, and quotes: an unquoted heredoc runs the backticks as commands and expands the `$`, and the published
comment loses its code spans.

For every platform write:

1. Reread the platform revision. If the head moved past `revision.head`, stop: the findings describe code that is gone,
   and the review has to run again. For a discussion write, also reread the thread and skip a duplicate action.
2. Treat a reply and a resolve or reopen as separate writes. After posting a required explanation, restart at step 1
   before changing the thread's state. Keep drafts unpublished unless submission was explicitly authorized.
3. Read back each write: the exact review, note, or discussion ID, content, state, revision, path, side, and line
   range.
   Report created IDs and inspection URLs; never claim a closure without the confirmed state.
4. On failure or an uncertain outcome, inspect before retrying; stop writing if ambiguity remains. Report limitations,
   such as a missing permission, and partial completion. Do not undo earlier writes. Delete created entries only with
   explicit cleanup authorization; never change review or note bodies that existed before. The one exception is the
   general comment of the publishing account's unsubmitted review or draft, rewritten when the user asks for it again.

At the end, report what was written, the number of earlier findings accepted as fixed, and, separately, every thread
state change the table above called for that was not performed, with the reason.

Use only the target platform's mechanics: a GitHub review is never written with GitLab's commands or field names, and
the reverse.

### GitHub

Read [the GitHub reference](references/github.md) for the pending-review and reply mechanics.

### GitLab

Read [the GitLab reference](references/gitlab.md) for Draft Notes, published notes, replies, and resolve or reopen.
