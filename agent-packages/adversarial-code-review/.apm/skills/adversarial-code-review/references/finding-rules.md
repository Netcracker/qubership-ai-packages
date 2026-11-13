# Finding rules

## What a finding is

A finding is a defect in the change, or a question whose answer decides whether there is one, that the author can act
on. It is about the change: a defect the change introduces, a path the change should have reached and did not, or a
claim the change makes that the code does not keep. A defect that was there before the change is recorded too, with the
origin that says so (next section), where the changed code reaches it or your axis's checks name it: it does not decide
the result, and the author is not asked to fix it in this change unless the change's own purpose reaches it. An old
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

## Origin

`input.md` names the branch the change merges into, and, under *Stack*, the other open requests whose commits the
reviewed range carries or builds on. Decide which commit made the defect, not which hunk shows it: a defect on a line
the change rewrote can still be older than the change.

1. Check whether the defect exists at `<base>`: run the probe there in your own worktree, or read the code at `<base>`
   where reading settles it. Where it does not exist at `<base>`, `git blame <head> -- <path>` over the defective lines
   names the commit that made it.
2. Where that commit is in the range under review and *Stack* lists it under another request, the origin is `stack`.
   Where `<base>` is another open request's head and the defect exists at `<base>`, check the branch the stack merges
   into the same way: a defect absent there is `stack` too, and blame at `<base>` names the commit and *Stack* the
   request. Where the defect is missing code, such as an unhandled case, blame has no line to name: probe the head of
   each request in *Stack*, from the bottom up, and take the first one where the defect appears. Set `introduced_by` to
   the commit, where one is known, and the URL of that request.
3. Where the defect exists on the branch the change merges into, the origin is `preexisting`, unless the change makes
   it worse, claims to fix it, or claims behavior the defect breaks; those are `change`. Set `introduced_by.commit`
   where blame names one, and choose a `disposition`:
   - `extend_scope`: the change's purpose reaches the defect. The code the change modifies meets a case it does not
     handle, handling the case takes a few lines in the files the change already touches, and it needs no decision the
     change has not already made. `proposed_solution` states the handling.
   - `follow_up`: everything else, such as a defect in code the reviewer read only for context, or a case whose
     handling needs a design decision, another component, or more code than the change itself. `proposed_solution`
     states the fix the follow-up issue asks for.
4. Otherwise the origin is `change`.

A case the change claims to handle, in its description, a commit message, or the issue it closes, is `change` however
old the code that breaks it: the claim is new. Where step 1 cannot settle whether the defect exists at `<base>`, record
`change` with `confidence: medium` and say in `problem` which part you could not check.

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

Grade a `stack` or `preexisting` finding as if this change introduced it: the severity tells the reader of the
follow-up issue, or of the other request, how much the defect matters. Only `change` findings decide the result.

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
- `origin`, `introduced_by`, and `disposition`: as *Origin* says. Leave `follow_up_url` out: delivery sets it once an
  issue tracks the defect.

Write in English, whatever the language of the request: `review-delivery` translates when it renders.
