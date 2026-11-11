---
name: review-delivery
description: Render a finished code review (a review.json file) as a chat report, a ledger file, an email, a GitHub pull request review, or GitLab merge request discussions, and publish it with the user's authorization. Use when a review skill hands over its review.json, or when the user asks to post, draft, email, or write out the findings of a review that already ran.
---

# Deliver a code review

This skill turns a finished review into the form the user asked for. It does not review: it never adds, drops, or
re-grades a finding, and it never reads the code to decide whether a finding holds. Its input is a `review.json` that
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
not worth sending. The two exceptions are held findings (next paragraph) and findings an earlier round already settled,
which appear only under *Previous findings*.

**Held findings.** A finding with `gate: code_settled` asks for something about the branch rather than the code: squash
the commits, rebase, reword a commit message. While any other `major` or `minor` finding (one with `gate: none`) is
open, do not publish it: the next round rewrites the history anyway. An earlier thread that `previous_findings` lists as
`fix_not_accepted` counts at the severity of the finding its `finding_id` names, and as open where it names none in this
file. Held
findings are not counted in the result line of an email or a GitLab publication, which shows only what it publishes.
The ledger lists them in their own section, so nothing is lost, and the chat report counts them on its own line.

**Order.** Major before minor before nit; within a severity, by id, which the verifier assigns in severity order. In the
ledger, by class first, and the classes, with the findings without a class as one more group, by their highest severity.

**Result line.** The same in every renderer that shows it, with every severity counted, zeros included. A GitHub review
shows it only for `REVIEW_INCOMPLETE` (see *Content*):

```markdown
Result: REQUEST_CHANGES (1 major, 2 minor, 3 nit)
Result: APPROVE (0 major, 1 minor, 0 nit)
Result: REVIEW_INCOMPLETE
```

`REVIEW_INCOMPLETE` has no counts, because the totals may be incomplete, and is followed by `Coverage: <coverage_gap>`.
Never write `Coverage: complete`.

**One finding**, in an email and on a platform. Three paragraphs:

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
  first line.
- `Proposed solution:` is from `proposed_solution`, and may be one phrase where the fix is obvious.
- The lead-ins `Problem:` and `Proposed solution:` are plain text, not bold.
- Each paragraph is one line, with no hard wraps: the platform wraps it.
- An inline comment carries no location: the platform shows it. Anywhere else, the location follows the tag:
  ``**F50 nit** `internal/x.go:122`, outside the diff: …``. A finding with no location names what it is about in the
  claim (the description, a commit message).

Word an `evidence` item with `basis: inference` conditionally (`can`, `may`, or the condition it depends on). Keep
`Problem` and `Proposed solution` to two to four sentences together unless the finding would be ambiguous; do not drop
the condition, the impact, or the expected outcome to save words. The tone is direct and neutral: no praise, thanks,
apology, greeting, or closer, and no softening of a defect.

**Scope.** Where `scope_exclusions` is not empty, state it once, near the result: the reader must know what was not
reviewed.

## Chat report

```markdown
# Review: <title>

Result: REQUEST_CHANGES (1 major, 2 minor, 0 nit)
Revision: <GitHub: base...head | GitLab: base=<sha>, start=<sha>, head=<sha>>
Out of scope: <scope_exclusions, when present>
Held until the code is settled: <n> findings (in the ledger)

## Previous findings

- [<short reference>](<thread_url>): <status>; <reason, with the decisive replies linked; for a disputed `major`,
  the assessment of each counterargument>.

## Main problems

1. <class title> (<highest severity>): <root cause>. Findings F1, F4, F9.
2. ...

## Findings

- **F1 major** `path/to/file:42`: <claim>
- **F2 minor, medium confidence** ...

## Needed to complete the review

- <open question and why it can change the result>
```

*Main problems* lists the classes, ordered by the highest severity among their findings, so the author sees the few
causes before the many symptoms; it is absent when no class has two findings. *Findings* gives each finding one line:
its tag as in *One finding*, its location, and its claim in the request's language. The problem and the proposed
solution are in the ledger, which the chat report does not repeat.
Omit an empty section. End with the path of `review.json`, and of every file this delivery wrote.

## Ledger

The ledger is the input of whoever fixes the findings, and it keeps everything the chat report folds: the class of each
finding, its axis, its evidence, and the held findings. Render it with the script; do not write or edit it yourself:

```bash
<skill dir>/scripts/render-ledger.py <review.json>
```

It writes `ledger.md` next to `review.json` and prints the path. Where it exits with status 2, `review.json` lacks a
field the ledger reads; send the file back with the message, as for a file that does not validate.

## Email

`email.md` holds a `Subject:` line (`Review of <title>: <result line>`), a blank line, and a plain-text body: the
result, the revision, the out-of-scope line, then the findings in the order above, in the *One finding* form without
the bold markers. Each location is a link to the line at the reviewed head
(`https://github.com/<repo>/blob/<head>/<path>#L<line>`, or the GitLab `/-/blob/<head>/<path>#L<line>` form).
Held findings are left out, as on a platform. Sending is the user's step.

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
Revision: `3c85f644...0c8d9fd3`.

Out of scope: rules of ADR-0091 to ADR-0096 that #202 and #232 implement.

All 3 findings of the previous round are fixed: [F6](<thread_url>), [F9](<thread_url>), and F22 from the [review body](<review_url>).

**Main problems**

1. The realm summary line is not pinned: joinReloadErrors builds it in map order, and its test matches only prefixes (F35, F47).
2. The User-visible lines quote the intended texts, not the emitted ones (F40, F41).

**Not inline**

**F40 minor** Two log texts quoted in the description and the top commit differ from what the code emits.

Problem: …

**F50 nit** `internal/token/keys/timing_test.go:122`, outside the diff: the comment on publish says it sets "the JWKS of every source", which no longer holds for realms.

Problem: …
```

- *Revision*, optional `Assessed by`, and *Out of scope* take one line each. Include `Coverage` only for
  `REVIEW_INCOMPLETE`.
- *Previous findings*: the earlier findings with `fix_accepted` share one sentence, with the ids linked to their
  threads; findings that sat in an earlier review body share one link to it. Every other status needs a reason, so
  each such finding gets its own line: `- [F6](<thread_url>): <status>; <reason>`.
- *Main problems*: one line per class, without the severity: the root cause, then the ids of its findings in
  parentheses, as plain text, not links: each inline comment opens with its tag, so a reader finds it by the id. A
  class left with one published finding is dropped, because that finding already stands on its own; a held finding, or
  one whose comment the user deleted from a draft, is not published.
- *Not inline*: the findings that cannot be placed inline, each in the *One finding* form, with the location and the
  reason after the tag, and nothing between them.

The general comment carries what the inline comments cannot: the findings that are not inline, and the causes that
several inline findings share. Do not copy inline findings, their claims, or pointers such as "See inline comment".

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
3. Read back each write: the exact review, note, or discussion ID, content, state, revision, path, side, and line.
   Report created IDs and inspection URLs; never claim a closure without the confirmed state.
4. On failure or an uncertain outcome, inspect before retrying; stop writing if ambiguity remains. Report limitations,
   such as a missing permission, and partial completion. Do not undo earlier writes. Delete created entries only with
   explicit cleanup authorization; never change review or note bodies that existed before. The one exception is the
   general comment of the publishing account's unsubmitted review or draft, rewritten when the user asks for it again.

At the end, report what was written, the earlier findings accepted as fixed, and, separately, every thread state change
the table above called for that was not performed, with the reason.

Use only the target platform's mechanics: a GitHub review is never written with GitLab's commands or field names, and
the reverse.

### GitHub

Read [the GitHub reference](references/github.md) for the pending-review and reply mechanics.

### GitLab

Read [the GitLab reference](references/gitlab.md) for Draft Notes, published notes, replies, and resolve or reopen.
