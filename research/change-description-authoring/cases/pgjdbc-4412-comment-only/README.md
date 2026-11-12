# Case: pgjdbc#4412, a change to comments and test names only

The input is the description of [pgjdbc/pgjdbc#4412](https://github.com/pgjdbc/pgjdbc/pull/4412) as first written, 561
words, with its two commit messages, the diff, and the task to rewrite it. The change corrects XA comments left stale
by the 42.7.13 `autoCommit` change and renames two tests; nothing changes at run time. Under the skill at 1.6.0 the
rewrite (`controls/pipeline-final.md`) came to 260 words, and much of that quoted the old wording of each stale
comment, which the diff shows. The case records an open problem: no rule in the skill keeps that wording out yet. A
widening of the translation rule to a comment the diff removes or rewrites was tried and left out of the skill,
because it changed no output (see Results). The checks also guard the facts a future rule must not cost: the code
each wrong comment contradicted, which the comment hunk does not show.

## Skill parts

- `SKILL.md`: §2 (Pull request description: What each paragraph must earn, show it, translation, length;
  Verification, a claim about the code names its check), §7, §7a
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **No removed wording quoted** (`no_old_comment_quoted_4412`). Neither `autoCommit is false on a connection returned
   by getConnection`, nor `2nd phase commit must be issued using an idle connection`, nor the old assertion message
   `should have restored connection autocommit mode` appears.
2. **Contradictions kept** (`contradictions_kept_4412`). `pg_has_role` and `64000` are still there: the `recover()`
   query and `MAX_BUFFERED_RECV_BYTES` are what makes those two comments wrong, and neither is in the comment's hunk.
   This is the guard against the rule cutting a fact the diff does not show.
3. **Renames named** (`renames_named_4412`). Both new test names appear.
4. **No run-time change, with its check** (`runtime_noop_checked_4412`, read). One sentence says nothing changes at run
   time and how that was checked (the files compared with comments stripped).
5. **Short** (`prose_at_most_150_words`). At most 150 words outside fenced blocks.

## Running it

The diff in `prompt.md` is the pull request's, except that the e-mail address in the `@author` context line is
removed.

As in [the cases README](../README.md). `controls/as-posted.md` is the description as first written.
`controls/pipeline-final.md` is the rewrite under the skill at 1.6.0. `controls/short.md` is a hand-written rewrite
of about 100 words that passes every check; `controls/cut-too-far.md` is the same with the two contradictions and the
renames replaced by a sentence each that names neither, and fails checks 2 and 3.

## Results

Runs of 2026-11-01, graded by reading; Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`.
`opus/` ran on tree `c99e1c77`, a draft of 1.7.0 from Netcracker/qubership-ai-packages#226 that carried that
widening; `opus/baseline/` ran on the skill at b247f44c (1.6.0), whose translation rule 1.7.0 keeps.

| Run | Not quoted (1) | Contradictions (2) | Renames (3) | Run time (4) | Words (5) |
| --- | --- | --- | --- | --- | --- |
| Opus r1 | fails: both comments quoted | passes | passes | passes | fails: 386 |
| Opus r2 | fails: both comments quoted | passes | fails: old names only | passes | fails: 306 |
| Opus baseline r1 | fails: both comments quoted | passes | fails: old names only | passes | fails: 404 |
| Opus baseline r2 | fails: both comments quoted | passes | passes | passes | fails: 400 |
| `controls/as-posted.md` | fails | passes | passes | passes | fails: 538 |
| `controls/pipeline-final.md` | fails | passes | passes | passes | fails: 260 |
| `controls/short.md` | passes | passes | passes | passes | passes: 104 |
| `controls/cut-too-far.md` | passes | fails | fails | passes | passes |

The widened translation rule does not change the output: under the draft, as under 1.6.0, every run quotes the stale
`State.ACTIVE` comment and the removed `2nd phase commit must be issued using an idle connection` message, and keeps
the two left-alone items as a Scope list. Two Haiku runs (effort `high`, not committed) under a stronger sentence,
"named by its place and by the code it contradicts, not by its old wording", quoted them too. The likely reason is
§2's rule that a literal, an error text among them, is never traded for a description: the removed message is one a
released driver emitted. The widening was left out after these runs, and the case stays failing until a rule fixes it.

Tree `9fe02a7c` (2026-11-06) marks the outcome block with `**User-visible changes.**` and `**Not changed.**`, keeps each
outcome on one line that is not wrapped, says a lead-in opens its paragraph, and says what a description that becomes a
commit body keeps. This case was not re-run on it: its Opus results carry no outcome block, any `**Scope.**` lead-in in
them already opens its paragraph, and no check reads either. The rows stand for the trees they ran on.
