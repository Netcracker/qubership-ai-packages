# Axis: runtime verification

Finding prefix: `RUN`. Runs late, in the `synthesis` phase, because its subject is the findings the other axes
already produced.

This axis does not look for defects. It takes the findings that a running system could settle and settles them —
turning arguments into demonstrations, and occasionally proving one wrong. It exists because the rest of the review
reasons about a system it has never seen running, and because a simulator (a fake client, a mock, an in-memory
double) differs from the real thing in exactly the places where careful reasoning goes wrong.

## Select before you execute

Read `findings.jsonl` and the reports, and choose. A finding is worth an execution when a runtime would change what
the reader does about it:

- it is `PLAUSIBLE` **and** a runtime would settle it;
- it is `CONFIRMED` by code reading alone, and it is severe enough that the maintainers will argue — a demonstration
  ends the argument in one command;
- its verification used a simulator: a fake clientset, a mock server, a stubbed transport. Those verdicts are the
  least trustworthy in the whole report, in both directions;
- it concerns behavior a simulator structurally cannot model: validation and admission, defaulting, immutability,
  garbage collection and cascade, leader election, restart and requeue, resource limits.

Skip what a runtime cannot answer: CI configuration, documentation, licensing, naming, anything about the source
tree. Say what you skipped and why — a reader must be able to tell "not runtime-settleable" from "not attempted".

Budget the selection: ten to fifteen executions, chosen by severity and by how much doubt each removes. Report the
list you chose and the list you dropped.

## The environment contract

**Create your own disposable environment and destroy it.** Never use an existing cluster, database, or broker unless
the focus file explicitly grants it: what looks like a test environment is routinely somebody's working one, and an
axis with write access will install a CRD into it without noticing.

For Kubernetes:

```bash
export KUBECONFIG=<dossier>/work/runtime/kubeconfig
kind create cluster --name dr-verify --kubeconfig "$KUBECONFIG"
kubectl --kubeconfig "$KUBECONFIG" get nodes
# ... work ...
kind delete cluster --name dr-verify --kubeconfig "$KUBECONFIG"
```

**Use a separate kubeconfig file, not `--context`.** A bare `kind create cluster` writes into `$HOME/.kube/config`
and switches `current-context` — so an instruction that says "never touch the user's cluster" while prescribing that
command contradicts itself, and every later unqualified `kubectl` becomes a coin flip. With `--kubeconfig` pointing
inside the dossier, the user's config is never opened, their current context never moves, and a command that forgets
the flag fails loudly instead of landing somewhere real. Set `KUBECONFIG` for the shell as well, as a second layer.

The same discipline applies to any other runtime: an explicit connection string to a database you created, never an
ambient default that might resolve to something in use.

Delete the environment even when the axis fails, and verify the deletion. Report the teardown as part of your
evidence.

## Method

1. Stand the environment up and record how: image build, CRDs installed, chart values used, versions of everything.
   Somebody must be able to repeat it, and it belongs in your report as a runnable block.
2. Reproduce the **normal path first**. Before demonstrating a defect, show the system doing its job — otherwise a
   failure you produce may be your setup rather than the code. If the normal path does not work, that is the most
   important thing this axis can report, and everything after it is suspect.
3. Then execute the selected findings, one at a time, capturing the command and the decisive output.
4. Where a demonstration needs a destructive action — deleting a CRD, killing a pod mid-write, scaling to two
   replicas — do it. That is what a disposable environment is for.

## Verdicts

For every selected finding return one of:

- `demonstrated` — reproduced. Quote the commands and the output that shows it. The finding stays, and its
  confidence becomes `CONFIRMED` on your evidence rather than on someone's tracing.
- `refuted` — the runtime shows the claim is wrong. Say what actually happens. This is the most valuable outcome
  this axis produces and it must not be softened.
- `narrowed` — real, but the trigger is tighter or the consequence milder than claimed. Give the new severity.
- `widened` — worse than claimed, or reproducible more easily. Say so and raise the severity.
- `not-reproducible` — you tried and could not, and you cannot say whether that is the finding or your setup. State
  which parts of the environment you doubt. Do not report this as a refutation.

New defects found while demonstrating something else are ordinary findings with a `RUN-` id; keep them separate from
the verdicts above.

## Report additions

On top of the standard format:

**Environment** — a runnable block reproducing the setup, with versions.

**Normal path** — what working looks like, or the fact that it does not work.

**Verdict table:**

| Finding | Selected because | Verdict | Evidence |
| --- | --- | --- | --- |

**Not attempted** — the findings a runtime could have settled but you had no budget for, and the ones a runtime
cannot settle at all, kept apart.

**Teardown** — the environment is gone, and how you know.
