# Case: a SHA pin that stops one call short

A regression case for `problem-report-authoring`. The input is the notes of a real investigation, the output is the
issue body a model drafted from them with the skill, and the checks below come from what the maintainers of the target
repository said about a report written from the same notes. Re-run the case when the skill or the model changes, commit
the new output over the old one, and read the diff.

## What happened

A review of qubership-ratelimit found that it pins
`Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml` by commit SHA, while that workflow calls
`docker-build.yaml` by the tag `v2.5.2`. The call that builds and pushes the images with `packages: write` therefore
resolves through a tag the caller's pin does not fix. A report was drafted with the skill as it stood after
[#108](https://github.com/Netcracker/qubership-ai-packages/pull/108) and shown to two maintainers of
qubership-core-infra before filing. The problem it describes is real; the report drew two objections.

- **The fix looked impossible.** The report asked for a SHA and left the mechanism to the project. The maintainers read
  it as a request to write the SHA of the release commit into the file that the release tags, which cannot be done,
  because that SHA exists only after the commit. The report named no shape that works. One is to pin to an earlier
  commit: `docker-build.yaml` is byte-identical in `v2.5.2`, `v2.6.0` and `v2.6.1`, so the release commit's parent
  already holds the file the release ships. Another is the `$/` same-repository syntax, which GitHub's changelog of
  2026-07-30 describes as resolving to the running commit with no SHA; it was not tried in a call from another
  repository. The notes carried the documentation sentence about `$/` and `./`, and the draft left it out.
- **Most of the text did not bear on the problem.** About 720 words of prose surrounded 130 words of evidence: the
  organization's pinning conventions, two GitHub documentation quotes, the list of search queries, a log of a push that
  succeeded, the empty rulesets and releases listings, a caller-side workaround nobody tried, and repositories nobody
  checked. The problem fits in three sentences.

## Files

| File | What it is |
| --- | --- |
| `prompt.md` | The investigation notes, frozen as of 2026-09-23, with the drafting task at the end. Contributors' names are removed. |
| `<model>/result.md` | The issue body the model wrote. |
| `<model>/result-note.md` | The hand-over note to the person filing, kept apart from the body. An output path the runner wrote into it is shortened to the path inside the case directory. |
| `<model>/skill-tree` | The git tree id of the skill the result was generated from, as `scripts/skill-tree.sh` prints it. |

One directory per model, named by its model ID, so results from different models sit side by side. Each directory
holds one run; the case measures a direction, not a distribution, so compare a new result against the old one rather
than against a threshold alone.

## How to run

Give a fresh session the following, with the three paths filled in, and nothing else. It needs no network: the notes
freeze the state of the repositories, so the case still runs after the tag moves or the run logs expire.

```text
You are drafting a GitHub issue. Read the skill at <skill>/SKILL.md in full, open its reference files under the
`references/` directory next to it where the skill says to, and follow it. Do not load any other copy of
problem-report-authoring. Your input is <case>/prompt.md. Do not use the network, a browser, gh, or curl, and do not
file anything. Write the issue body to <case>/<model>/result.md and the hand-over note to the person filing to
result-note.md in the same directory. Write only those two files.
```

`<skill>` is a copy of the skill at the revision under test, taken outside any checkout. From the repository root:

```bash
mkdir -p /tmp/skill-<rev>
git archive <rev> agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring \
  | tar -x -C /tmp/skill-<rev> --strip-components=5
```

After the run, write `scripts/skill-tree.sh <skill directory> <rev>` to `<case>/<model>/skill-tree`, or
`scripts/skill-tree.sh <skill directory>` where the skill under test is not committed yet. A result whose `skill-tree`
equals the tree id of the skill in the commit that holds it was generated from that skill, and a rebase or an amend
that leaves the skill unchanged does not need a new run.

Run the session from a directory outside the checkout too. A session that reads the skill inside the checkout also
loads the package's `CLAUDE.md`, and through it `AGENTS.md`, which are instructions for editing the skill, not for
using it.

## Checks

Each check names the objection it guards against. Read `result.md` against all of them.

1. **The first paragraph states the gap.** The caller pins `generic-go-build.yaml` by SHA, and the `docker-build.yaml`
   call inside that commit resolves through a tag.
1. **The evidence is the run's `referenced_workflows`.** The body pastes the two entries, one resolved by SHA and one
   with `ref=refs/tags/v2.5.2`.
1. **The fix is shown to be possible** (the first objection). The expected behavior names at least one shape that
   works, such as pinning to a commit that already exists or the `$/` syntax, so that a maintainer cannot answer that
   the SHA does not exist yet without contradicting a sentence in it. A shape offered as "my reading, not tested" does
   not pass.
1. **Nothing in the body is there only because it is true** (the second objection). The body carries none of: more
   than the one log line that shows the job pushed an image; the list of search queries; the caller-side `skip-docker`
   workaround, which nobody tried; a statement of what was not checked, such as how the 16 repositories pin the
   workflow. Each of these belongs in `result-note.md` if anywhere. A `./` shape marked as untested is allowed, as the
   skill allows any unverified shape that says so. The organization's pinning
   convention, the organization that owns the repository being bound by it, and the 16 repositories #367 names as
   users of the workflow, stated as the reach of the problem, are content the person filing accepts.
1. **The prose is short.** Words outside code blocks: the draft the maintainers read had about 720. The skill reads a
   report sentence by sentence past about 300, and so does a reviewer of a result over 300 before accepting it.

Checks 4 and 5 can be counted, from this directory, with the model's directory as the argument. Every marker should
print `False` and the log count at most 1; the number of groundings and any untested shape of the fix still need a
reading.

```bash
python3 - claude-opus-5-5 <<'EOF'
import re, sys
text = open(f'{sys.argv[1]}/result.md').read()
prose = re.sub(r'```.*?```', '', text, flags=re.S)
print('prose words:', len(prose.split()), '(read sentence by sentence past 300)')
print('search queries listed:', bool(re.search(r'[`"](unpinned|mutable tag|pinned by SHA)[`"]', text)))
print('log lines:', len(re.findall(r'^\S+Z #\d+ pushing manifest', text, flags=re.M)))
print('unchecked items stated:', bool(re.search(r'(not|never) checked|did not check|never tried', text)))
for marker in ['skip-docker']:
    print(f'{marker!r} present:', marker in text)
EOF
```
