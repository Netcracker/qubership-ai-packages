# blackbox-test-design

An APM package that governs **which questions to send a system whose behavior you learn by querying it**: a legacy
service you are porting, a vendor binary or API without source, a reference stand that answers a parity or golden
suite. You hold a model of that system (an executable spec, a port, a mock) and a pile of recorded answers, every new
answer costs a run, and the expected value of a new question is unknown. The skill spends those answers on the
questions most likely to show that the model is wrong.

The package exists because the usual measures of a test set are taken from the model under test. A port with a 97%
mutation score, complete pairwise coverage, and every golden green can still lack a rule nobody wrote down, and none
of those measures can notice it. Agents asked "what else should we test before cutover?" tend to answer with more of
the same.

## What it covers

- The model's decisions listed with the answer behind each, the goal settled as parity or as intended behavior, and
  the reference version recorded with every batch of answers.
- The self-measurement trap: mutation score, coverage, pairwise coverage, fuzzer saturation, and metamorphic relations
  whose dimensions came from the model, and an independent source for each.
- Oracle strength: outcomes a probe must tell apart, the comparator's merged classes, which answers pin which
  decisions, and the side channels the reference exposes.
- Evaluation order and laziness, mapped with sentinels and poison at positions taken from the input format.
- Metamorphic relations over the structure of the input, identity collisions, and a negative control for the
  relation generator.
- Hand-written exception lists treated as the footprint of one mechanism, with candidate general rules scored against
  the answers.
- The idioms of the reference's platform as standing alternatives at every handling point, with a reference table
  per platform.
- Boundaries on representation rather than on meaning, combinations over raw input features, and an independent
  second model with a differential harness.
- Choosing a round: questions scored by what their answers separate, weighted by the cost of being wrong, tiered for
  a budget cut, bracketed by control replays, safe for a shared environment, and a stopping rule stated in terms of
  questions and answers.
- Findings labeled observed, inferred, or hypothesis, with the mechanism kept apart from the observation.

Not covered: tests of code whose expected values you can state from a specification or from source you can read.
Those belong to [`test-authoring`](../test-authoring/).

## Contents

- `.apm/skills/blackbox-test-design/SKILL.md`: the techniques, a checklist, and a worked example.
- `.apm/skills/blackbox-test-design/references/idioms.md`: the common alternatives per area (trimming, number parsing,
  case, collections, templating, errors) and per platform (JVM, .NET, Python, Go, JavaScript, JSON binding, SQL, web
  frameworks).

The package ships no instructions file, so nothing is added to `AGENTS.md` or `CLAUDE.md`. The task is rare, and the
skill loads from its description or by name.

## Pairs with

- [`test-authoring`](../test-authoring/) governs each test that carries a question: its level, its assertion, and its
  failure report, and the harness or comparator once its behavior is decided. Install both.

## Research

The trigger eval set, the harness that measures the description against every other skill in this repository, its
results, and five behavioral cases with and without the skill are in
[`research/blackbox-test-design/`](../../research/blackbox-test-design/README.md).

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/blackbox-test-design
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/blackbox-test-design@<ref>
```

Replace `<ref>` with the release tag, branch, or commit SHA you want to pin.
