# Finding rules

## What a finding is

A finding is a defect in the change, or a question whose answer decides whether there is one, that the author can act
on. It is about the change: a defect the change introduces, a path the change should have reached and did not, or a
claim the change makes that the code does not keep. Record a defect where the changed code reaches it or your axis's
checks name it, without deciding whether the change made it: the verifier decides that, once for every finding, and a
defect older than the change neither decides the result nor asks the author for a fix the change does not owe. A
defect in code you read only for context is not recorded.

Not a finding:

- missing evidence (a context gap goes to `open_questions`, not to `findings`);
- the size of a change on its own;
- a preference with no reader or user cost;
- something an earlier thread already settled, unless new evidence reopens it;
- something that contradicts an agreement the author and a reviewer reached in the discussion, unless the finding quotes
  the agreement and shows a consequence it did not consider;
- something an open thread on the request already raises, whoever opened it: the verifier attaches it to that thread
  instead (`prior_thread`) only where this review adds evidence;
- anything the request put out of scope.

## Severity

Ask: **if the author does not fix this, what does the reviewer do?**

| Severity | If the author does not fix it |
| --- | --- |
| `major` | the change does not merge |
| `minor` | the reviewer fixes it, before or after the merge |
| `nit` | it stays |

A wrong result, a broken caller, a data loss, a security hole, a claim the code does not keep, or a test that cannot
fail is `major`. A comment that misleads, a missing example a reader needs, a missing test for a secondary path, or a
name a reader will misread is usually `minor`. A `nit` is a small change the reviewer would still accept gladly.

Grade every finding as if this change introduced it, whatever the verifier later decides about its origin: the severity
tells the reader of a follow-up issue, or of another request, how much the defect matters.

## Confidence and kind

`high` when the evidence establishes the problem directly, `medium` when one small inference remains. A finding whose
truth depends on context you could not get is a `question` (`kind: question`), not a `low` finding: ask what decides it.
Drop a finding you cannot raise to `medium` and cannot phrase as a question the author can answer.

## Gate

`gate: code_settled` marks a request about the branch rather than the code: squash or reorder commits, rebase, reword a
commit message. Everything else is `gate: none`.

## Location

The smallest useful range in the new file (`side: new`), or the removed line (`side: old`). Set `in_diff: false` when
the line is outside every hunk. Use `location: null` only for a finding with no line, such as a missing changelog entry.

## Content

- `title`: the claim, one sentence that states the defect (not the topic) or asks the question. It is the first line of
  the published comment, and often the only line a reader sees, so it stands alone.
- `problem`: the condition and the concrete impact, without restating `title`.
- `evidence`: the decisive facts only, each marked `fact` (read or run) or `inference` (derived). Quote code and text
  exactly, with `path:line`.
- `proposed_solution`: the smallest outcome that resolves the problem, without prescribing a rewrite a local change
  avoids.
- `prior_thread`: the URL of an earlier thread this finding continues.
- Leave out `origin`, `introduced_by`, `disposition`, and `follow_up_url`: the verifier sets the first three, and
  delivery sets the last once an issue tracks the defect.

Write in English, whatever the language of the request: `review-delivery` translates when it renders.
