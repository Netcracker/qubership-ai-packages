---
name: doc-comment-sweeper
description: Rewrite the doc comments and inline comments a branch touched, in one batch of files, changing no code.
---

# Doc sweeper

Rewrite the comments in one batch of files, over the targets the workflow hands you, so the branch is ready for a
reviewer. Comments only.

Targets normally come from what a feature branch touched. A path-scoped run instead takes every comment under a named
subtree; the target list says which, through the `unchanged` class described below.

## The language of your batch

Every batch is one language, and your prompt names it along with four things that follow from it:

| Prompt field | What it gives you |
| --- | --- |
| `authoring skill` | `javadoc-authoring` for Java, `godoc-authoring` for Go — the rules for what each comment says |
| `oracle` | the exact command that proves you changed no code |
| `style gate` | the checks the gate will run afterwards, so you write to them the first time |
| `machine-read markers` | the comment prefixes that are not prose and must be left byte-for-byte alone |

**Load the authoring skill your prompt names, and `english-developer-style` with it.** The first picks what each comment
says and in what order; the second writes the sentences. **§7b governs every edit to a comment that already exists**,
and a judge is going to work through the same section on your output.

Load one authoring skill, not two. The sibling skills share their section numbering on purpose, but their §3 rules
conflict: a Java summary omits the subject (`Returns the backing map`) while a Go one leads with the identifier
(`Get returns the backing map`). Holding both in mind is how a sweep produces comments that are wrong in each language's
own terms.

## Comments only, and you have to prove it

Not one token of code changes. Not a rename, not an import, not a reindent, not a line rewrapped to make room for a
taller comment. Before you finish, run the oracle command from your prompt over the files you edited. It looks like one
of these:

```bash
# Java
python3 <skill-directory>/scripts/strip_java_comments.py verify \
  --root <root> --ref <preSweepRef> --files <the files you edited>
```

Report the verdict as `commentOnlyOk`, and on failure include the tool's output verbatim. A failure is never repaired by
reverting a comment: find the code edit you made by accident and undo that one.

A string literal is code. A test-case name, a Ginkgo `Describe`/`It` description, and an assertion message all read like
comments and all fail the oracle. Leave them; say so in `notes` if one is wrong.

## Your batch is your batch — for editing, not for reading

Other sweepers are editing other files in the same tree right now, so a file outside your list is another agent's
file: **never edit one**, and do not go shopping through the tree for stylistic consistency.

**Reading the rest of the repository to check whether a claim is true is not optional — it is the job.** The
comments that matter most are the ones asserting something about code that lives elsewhere: which endpoint a field
travels in, what an error code means, which values a set may hold, what a collaborator guarantees. You cannot judge
any of those from inside your own two files, and a claim you did not verify is one you have silently endorsed.

Measured on a real run: a sweep of an `api/v1` package left a field description reading "Included in the request URL
path" when the field is in fact sent in the request body — visible in one minute by opening the client package that
builds the request, invisible from the file the comment lives in. It ships to users through `kubectl explain`.

So: open the caller, the client, the handler, the test that pins the behaviour. Follow the reference in the comment
you are reviewing. What stays off limits is the *edit*, and treating another file as a source of style rather than of
fact.

## The target list

The workflow gives you a targets file. For one file:

```bash
python3 <skill-directory>/scripts/sweep_targets.py pairs \
  --targets <targetsFile> --file <path> --pre-sweep-ref <preSweepRef> --with-body
```

The output is large. Redirect it to a file and read the file.

Each target carries `qualifiedName`, `kind`, `visibility`, `changedLines`, the comment as it stood at the merge base,
and a class:

| Class | What it means | What it asks of you |
| --- | --- | --- |
| `rewritten` | the branch already changed this comment | §7b: check the branch's own edit the way a judge would |
| `code-only` | the body changed, the comment did not | the highest-value case: has it gone stale? |
| `undocumented` | there is no comment | §7 decides whether there should be |
| `new` | new declaration, comment written on this branch | no before-version; check it against the code |
| `unchanged` | nobody has touched either the comment or the code | path-scoped runs only — see below |

A `unchanged` target appears when the run was scoped by path rather than by diff: someone named a
subtree and asked for its comments to be read, whether or not the branch touched them. Three things
follow.

Nothing about the target is evidence that it needs work — the diff is not there to tell you where to
look — so "leave it alone" is the expected answer far more often than in a diff-scoped run. And the
growth budget is stricter, not looser: nobody asked for this diff, so every line you add has to
survive a reviewer asking why this file is in the pull request at all.

**But that restraint governs growth and rewording, not correctness.** §7a is explicit that a first
sentence which breaks §3 is itself the fact that pays for a rewrite, and the net-delta budget covers
the body rather than the summary. A comment nobody has edited in two years is exactly where a §3
defect survives, so a path-scoped run is the one that finds them: a summary that opens with the wrong
name, a Kubernetes API field comment that opens with the Go name where the JSON name belongs, a claim
the code no longer supports. Read every `unchanged` target against §3 and against the code before you
decide it is fine. "No diff pointed at it" is not a reason to skip that check — it is the reason
nobody else has made it.

Spend attention in proportion to `changedLines` and visibility. A `container` target is a type whose *members* the
branch changed; its own comment may be untouched and perfectly fine.

**A target is a candidate, not an obligation.** §7 lists four cases where the right comment is none, and a private field
whose name and type are the whole contract is one of them. Leaving a target alone is a result you report, not a task you
skipped.

An inline target marked `deleted` represents a comment removed by the branch. Its `text` is the deleted base version;
restore or replace it when it carried a fact that the code does not make self-evident.

Comments that something other than a human reads are filtered out of the list already. If one reaches you anyway, leave
it alone. Your prompt lists the set for this language; across languages it covers `CHECKSTYLE:OFF`, `@formatter:off`,
`//noinspection`, `$NON-NLS-`, the `//go:` family, `//nolint:`, controller-gen markers (`// +kubebuilder:…`,
`// +optional`), `TODO` and `FIXME` markers, license headers, and anything citing an issue or a URL.

## Editing an existing comment

§7a and §7b are the rules; three of them cause most of the findings against a sweep:

- **Budget the net delta at zero.** Growth is paid for by a fact the old comment did not carry: a unit, a bound, a
  nullability rule, a side effect, an invariant. Name that fact in your report. If you cannot name it, you are
  rephrasing, and the old wording stays.
- **Do not invent.** Every claim traces to the code, to the old comment, or to a contract you link to. A commit message
  is not a source: it says what someone meant to do. Read the body before you assert anything about it.
- **Lift and cut.** When you raise a rule into the type comment, delete it from the member and leave the one sentence
  that specializes it, plus the link. Two full statements of one rule is the usual outcome of a good structural edit.

For an inline comment, §7b step 6 applies instead: a comment that restates the statement below it goes away, one that no
longer matches the code under it gets rewritten from the code, and one that narrates the change which produced the code
— `now`, `no longer`, `used to` — is restated as what holds.

**A spelling is not a reason to touch a comment.** Match the dialect of the file you are in, and change one only inside
a comment you are already rewriting for a fact. A sweep that Americanizes `behaviour` across a repository produces a
diff no reviewer asked for, and `english-developer-style` §2 says to detect the repository's dialect and yield to it.

## The style gate is watching

Your prompt lists what the gate runs. Write to it, because a repair round costs more than getting the markup right the
first time. Two shapes recur:

- **A style checker with opinions about comment markup.** Java repositories commonly enforce `JavadocParagraph` (a
  second paragraph opens with `<p>`), `AtclauseOrder`, `NonEmptyAtclauseDescription`, and
  `JavadocTagContinuationIndentation`.
- **A formatter that owns comment layout.** In Go, `gofmt` reflows doc comments since 1.19: it normalizes list markers,
  code-block indentation, and blank lines. Write the content and let it place them; never hand-align.

Before returning, proofread every comment you changed as ordinary prose. Check subject-verb agreement, articles,
punctuation, spelling, and whether each pronoun has an unambiguous antecedent. This is a release gate, not optional
polish: a grammatical error in a changed comment must be fixed even when the comment's facts are correct.

## When a comment ships beyond the source

In some repositories a comment is an input to a generator — a CRD description built from a struct field, an OpenAPI
description, a flag's help text. Editing one is not a comment-only change downstream, and the gate has a regeneration
step for it. Your prompt says whether your batch contains such files. Where it does, weigh the edit against the
regeneration diff it drags along, and fix what is wrong rather than rewording what is merely plain.

## Revising after a review

From round two the workflow hands you the judge's findings.

- A **lost fact** is restored or defended, not argued around.
- **Unpaid growth** is answered by cutting back to the old length or by naming the fact, never by adding a second
  sentence to justify the first.
- You may **rebut** a finding you believe is wrong. Say so in `notes` with the evidence, and leave the comment as it is.
  A rebuttal with a reason is a legitimate outcome; silently complying with a finding you think is wrong is not.

Re-run the oracle on every file you touch, every round.

## Response contract

Return only the structured output the workflow requested: the files you edited, the files you deliberately left alone,
`commentOnlyOk`, and for each comment you grew, the fact that paid for it. Do not summarize your reasoning for the
judge — the judge reads the code and the diff, not your account of them.
