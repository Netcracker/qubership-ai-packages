# Axis: change description and branch

What the change says about itself, and how its branch will land. The description, the title, and the commit messages in
`input.md` are the claim, and the diff is what was done. The axis has two parts, read in order: the description and the
branch. Each part has its own checks and severities; apply them one part at a time.

Load `change-description-authoring` and `english-developer-style`. Follow the repository's own rules from `input.md` for
the changelog and the pull request title.

A defect that both parts see is one finding: a commit message that claims something its commit does not do is filed
under *Description*, with `gate: none`. *Branch* covers how the commits are split, and a message too vague to tell which
commit it describes. Whether a hunk is claimed at all belongs to `intent-scope`.

## Description

### Check

- The pull request title and description, and every commit message, against what the diff does: a claim the diff does
  not keep, a behavior change the description does not state, a missing `User-visible` outcome or break.
- Whether the change owes a changelog entry, by `change-description-authoring` and the repository's rules, and whether
  it has one in the right form.
- A break a user will meet on upgrade that the description does not lead with.
- The title, by the test of `change-description-authoring`: a reader of a list of thirty open requests, or of `git log
  --oneline` after a squash merge, can tell which change this is without opening the diff. A title built from internal
  identifiers a reader cannot place, or one that names the mechanism where the change has an effect a caller observes,
  fails it; propose a title that names the component and the change.
- The length. Every paragraph of the description answers a question one of the readers in `change-description-authoring`
  asks. A walk through the diff file by file, a list of the tests the diff shows, a verification CI already reports, the
  history of review rounds, and a fact stated twice answer none: name the paragraphs that can go, and the slots that are
  missing.

Title and length findings carry `gate: code_settled`, since the description changes with every round of fixes. A claim
the diff does not keep, a missing outcome or break, and a missing changelog entry carry `gate: none`.

### Not a finding

Wording that costs a reader nothing. A title or a description that makes a reader open the diff to learn what changed is
not such wording. Requests about how the commits are split or squashed belong to *Branch*.

### Severity

A description that claims something the diff does not do, or hides a break, is `major`. A missing changelog entry the
repository requires, a title a reader cannot place without the diff, and a description padded with what the diff already
shows are `minor`.

## Branch

Requests about the branch rather than the code. Every finding of this part has `gate: code_settled`.

### Check

- Commits that should be squashed: fixups, "address review" commits, a commit that reverts an earlier one in the branch.
  Skip this where the repository squash-merges every pull request (its `CONTRIBUTING.md`, its agent rules, or its merge
  settings say so).
- A branch that needs a rebase: it conflicts with the target, or it is based on a revision that lacks a change it
  depends on.
- A commit message that does not describe its commit, where the commits will survive the merge.

### Severity

`minor` at most.
