# Case: pgjdbc#4412, a change to comments and test names only

The input is the description of [pgjdbc/pgjdbc#4412](https://github.com/pgjdbc/pgjdbc/pull/4412) as first written, 561
words, with its two commit messages, the diff, and the task to rewrite it. The change corrects XA comments left stale
by the 42.7.13 `autoCommit` change and renames two tests; nothing changes at run time. Under the skill at 1.6.0 the
rewrite (`controls/pipeline-final.md`) came to 260 words, and much of that quoted the old wording of each stale
comment, which the diff shows. The case records an open problem: no rule in the skill keeps that wording out yet. A
widening of the translation rule to a comment the diff removes or rewrites was tried and left out of the skill,
because it changed no output (see Results). The checks also guard what a future rule must not cost: the description
still says where the two comments that contradicted the code are, the `recover()` comment and the batch test. The
values that show each contradiction, `pg_has_role` and `64000`, are in the same hunk as the comment, so the checks
leave them to the diff.

## Skill parts

- `SKILL.md`: §2 (Pull request description: What each paragraph must earn, show it, translation, length;
  Verification, a claim about the code names its check), §7, §7a
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **No removed wording quoted** (`no_old_comment_quoted_4412`). Is each stale comment named by its place and by the
   code it contradicts, not by its old wording? The script counts two strings of the old wording, `autoCommit is false
   on a connection returned by getConnection` and `2nd phase commit must be issued using an idle connection`; a
   paraphrase of either fails the check on reading.
2. **Contradictions located** (`contradictions_located_4412`). The description names the `recover()` comment and the
   batch test as the two comments that contradicted the code. The script looks for `recover` next to the word
   `comment`, because every run also names `recover()` in another comment's bullet; a description that names either
   comment without saying it contradicted the code fails the check on reading. The description need not quote
   `pg_has_role` or `64000`: the hunk of each comment shows the value, and §2 calls a sentence that restates it
   translation.
3. **No run-time change, with its check** (`runtime_noop_checked_4412`, read). The description says once that nothing
   changes at run time and how that was checked (the files compared with comments stripped).
4. **Short** (`prose_at_most_150_words`). At most 150 words outside fenced blocks.

## Running it

The diff in `prompt.md` is the pull request's, except that the e-mail address in the `@author` context line is
removed.

As in [the cases README](../README.md). `controls/as-posted.md` is the description as first written.
`controls/pipeline-final.md` is the rewrite under the skill at 1.6.0, and `controls/opus-1.6.0-r1.md` and
`controls/opus-1.6.0-r2.md` are two Opus runs of the case on the skill at b247f44c (1.6.0). `controls/short.md` is a
hand-written rewrite of about 100 words that passes every check. `controls/cut-too-far.md` is the same with the two
contradictions and the renames replaced by a sentence each that names neither, and fails check 2.
`controls/no-check.md` is `controls/short.md` with its last paragraph cut to "Nothing changes at run time.", and fails
check 3.

## Results

Runs of 2026-11-03, graded by reading; Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`. `opus/`
ran on tree `ee45a03a`, the skill at 1.7.0 as Netcracker/qubership-ai-packages#226 merged it.
`controls/opus-1.6.0-r1.md` and `controls/opus-1.6.0-r2.md` ran on the skill at b247f44c (1.6.0, tree `a0bc4f58`) on
2026-11-01.

| Run | Not quoted (1) | Contradictions (2) | Run time (3) | Words (4) |
| --- | --- | --- | --- | --- |
| Opus r1 | fails: both comments quoted | passes | passes | fails: 411 |
| Opus r2 | fails: both comments quoted | passes | passes | fails: 383 |
| `controls/opus-1.6.0-r1.md` | fails: both comments quoted | passes | passes | fails: 404 |
| `controls/opus-1.6.0-r2.md` | fails: both comments quoted | passes | passes | fails: 400 |
| `controls/as-posted.md` | fails | passes | passes | fails: 538 |
| `controls/pipeline-final.md` | fails | passes | passes | fails: 260 |
| `controls/short.md` | passes | passes | passes | passes: 97 |
| `controls/cut-too-far.md` | passes | fails | passes | passes: 77 |
| `controls/no-check.md` | passes | passes | fails: no check named | passes: 78 |

Every run quotes the stale `State.ACTIVE` comment and the removed `2nd phase commit must be issued using an idle
connection` message, and lists the two items it left alone. Two Opus runs on 2026-11-01 under a draft of 1.7.0
(tree `c99e1c77`, which no commit has; the outputs are `opus/result*.md` at 5b90d2e8), which widened the translation
rule to a comment the diff removes or rewrites, quoted both too, at 386 and 306 words. Two Haiku runs (effort `high`,
not committed) under a stronger sentence, "named by its place and by the code it contradicts, not by its old
wording", quoted them as well. The widening was left out of 1.7.0 after these runs, and the case stays failing until
a rule fixes it.

Two sentences of §2 likely keep the quotes in. One is the rule that a literal, an error text among them, is never
traded for a description: the removed message is one a released driver emitted. The other is "The Why slot is where
the old code gets retold; where the old lines show the defect, show them instead": in a comment-only change the stale
comment is the defect, and every run quotes it where it gives the reason for the change. A rule that fixes this case
has to exempt a comment from that sentence, and [`pgjdbc-4388-contract-fix`](../pgjdbc-4388-contract-fix/README.md),
whose check 1 requires the old lines in a fenced block, has to keep passing.
