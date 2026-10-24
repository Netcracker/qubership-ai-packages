# Axis: upgrade and migration

Finding prefix: `UPG`. An **evidence** axis, and one that has to *execute* — its whole subject is a transition
between two states of a live system, which no amount of reading establishes.

`api-compatibility` asks whether the contract changed. This axis asks whether the *transition* works: whether a
release running version N survives becoming version N+1, whether it can go back, and whether the operator's own
data and externally-managed state come through. Those are different questions, and the second one is routinely
answered by "we never tried".

If the repository has no released prior version to upgrade from, say so and stop — do not substitute a fresh
install for an upgrade.

## What you must actually run

A report on this axis that contains no executed upgrade is not a report. At minimum:

1. **N → HEAD.** Install the newest released version (tag, published chart, published image), then upgrade to
   the working tree. Not a fresh install of HEAD.
2. **Rollback.** `helm rollback` / the project's documented equivalent, back to N. Then check whether the system
   is actually at N — the workload version, the CRD schema, the data, and any state the controller wrote.
3. **Repeat upgrade.** Run the upgrade twice. The second one must be a no-op.
4. **Uninstall after upgrade.** Removal from an upgraded release exercises different owner references and
   finalizers than removal from a fresh one, and this is where the two disagree.

Record versions, commands, and wall-clock for each. Where a step is impossible, name what is missing.

## Questions

- **Does the upgrade converge, or does it stall?** A hook that waits forever, a workload whose new spec cannot
  schedule, a rolling update blocked by a PDB or a single-replica statefulset with `RWO` storage. Distinguish
  "slow" from "wedged" and give the evidence.
- **Immutable fields.** Selectors, `spec.volumeClaimTemplates`, `clusterIP`, job templates, and anything else
  the API server refuses to patch. Does the chart rename or reshape a resource across versions such that the
  upgrade fails with `field is immutable`? That failure is invisible in `helm template` and unmissable in
  `helm upgrade`.
- **Ownership transfer.** Server-side apply field managers, `meta.helm.sh/release-name` annotations, owner
  references pointing at an object the new version no longer creates. An object owned by nobody is leaked; an
  object owned by two managers flaps.
- **Finalizers.** Which objects carry them, who removes them, and what happens when the controller that would
  remove them is already gone. The classic failure is deleting a release whose CRDs or RBAC went first —
  the namespace then hangs in `Terminating` forever. Test the documented order *and* one wrong order, because
  operators get it wrong under pressure.
- **CRD schema transitions.** A field that becomes required, an enum that loses a member, a default that
  changes: all of them apply retroactively to objects already stored. Take an object authored under N and
  re-apply it under HEAD.
- **Data.** Whatever the system persists — volumes, databases, dashboards, recording rules — is it still there,
  still readable, and still correct after the round trip? Name what you checked, not "data was preserved".
- **The documented procedure.** If the project publishes an upgrade or migration runbook, follow it *literally*,
  including any staged sequence, and report where the text and the system disagree. A runbook that is wrong is a
  defect at the severity of the damage it causes.
- **Skipping a version.** If the project supports N-2 → HEAD, try it. If it does not say, that silence is itself
  a finding.

## Rejection rules

Drop these; they are someone else's axis or nobody's defect.

- A contract change with no transition problem — that is `api-compatibility`.
- Slowness caused by image pulls or a degraded network on the review machine. Re-run before you write it up.
- "The upgrade could fail if the user edits resources by hand." Unless the project documents that as supported,
  it is a preference.
- A defect that reproduces identically on a fresh install. That belongs to `deployment-config`; this axis owns
  what the *transition* adds.
- Cosmetic churn in the rendered diff (label reordering, annotation timestamps) with no observable consequence.

## Evidence

Prefer a transcript over a description. The decisive artifact for this axis is usually a small table:

| Step | Command | Result |
| --- | --- | --- |
| install N | ... | ... |
| upgrade → HEAD | ... | `field is immutable` on `Service/foo` |

Keep the full output under the dossier's `work/`. State plainly which of the four mandatory runs you completed;
an axis that ran only the first is a partial axis and must say so in its summary rather than in a footnote.
