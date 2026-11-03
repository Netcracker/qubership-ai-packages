# Regression cases for the doc-comment skills

The five doc-comment skills (`javadoc-authoring`, `godoc-authoring`, `jsdoc-authoring`, `pythondoc-authoring`,
`rustdoc-authoring`) share their section numbering and most of their rules, so their cases share one shape and one
runner. Each skill has two cases under `research/<skill>/cases/`:

| Case | Input | Rules |
| --- | --- | --- |
| `members` | a new public class with a getter, a private field, a small and a shifted constant, a sentinel, a failure | negative controls: no comment on the getter and the field, one form for `30`; presence: both forms for `1 << 20`, the sentinel, the failure channel |
| `tests` | a new test class: two ordinary tests, a regression test with a descriptive name, a guard test | negative controls: no comment on the ordinary tests, no defect history on the regression test; presence: the guard test names the edit that turns it green |

The `members` case of each skill also checks a rule of its own language that 1.3.0 narrowed: `@since` in Java, an
`implements` line on an unexported type and the zero-value sentence in Go, the rejection sentence where a `.d.ts` hides
`async` and `@defaultValue` in TypeScript, generator notes in Python, and `# Examples` in Rust. Some of these never
fired, even on the baseline; each case README says which. The inputs are written for the cases, not copied from a real
repository. `agent-packages/AGENTS.md`, section "Testing a skill against its cases", says when a case is re-run and how
its results are committed.

## Running a case

From the repository root:

```bash
research/javadoc-authoring/cases/run-case.sh godoc-authoring research/godoc-authoring/cases/members opus result
```

The script copies the doc-comment skill and the American `english-developer-style` out of the checkout, runs `claude
-p` in safe mode in a temporary directory with the Read tool alone, and writes `<model>/<name>.md`,
`<model>/<name>.run.txt` (cost, tokens, turns), and `<model>/skill-tree`. A fifth argument takes the doc-comment skill
from a commit and writes under `<model>/baseline/`; the committed baselines ran on `a51171b`, the skills before 1.3.0.

To read the results, print every comment beside the declaration it sits on:

```bash
python3 research/javadoc-authoring/cases/comments.py research/godoc-authoring/cases/members/*/result*.md
```

The script only collects the comments; grade each check by reading them against the case README.
