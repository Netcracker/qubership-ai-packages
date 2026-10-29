# State an earlier version left behind

Evidence for the rule in `SKILL.md` §3 and §4 that a change to how the system reads or replaces what an earlier
version created owes a test or a run that starts from that state, not only from a fresh install.

## The incident

In `Netcracker/qubership-authz-agent` PR #122, a kind test harness moved from manifests applied with `kubectl apply` to
a Helm chart. The author ran it, and so did two independent automated review passes: `final-review` and a cross-review
by Codex and a Claude subagent. Every run started from a fresh cluster, and none of them met the failure below.

A human reviewer ran the new chart on a cluster that the earlier harness had set up. The install failed, because the
objects `kubectl apply` had created carry no Helm ownership labels or annotations, and Helm refuses to adopt them. The
error names each such object as one that `exists and cannot be imported into the current release`, with the reason
`invalid ownership metadata`. Both strings come from helm v4.3.1, `pkg/action/validate.go:96` and `:192`, checked
against the tag.

One incident, one kind of state (deployed objects). The rule generalizes it to the other things an earlier version
leaves behind: a configuration file, keys or certificates, a persisted format or schema, a cache, a lock file. None of
those has a measured incident in this folder yet.

## What the review passes missed, and why

The fresh cluster is one partition of the state the system starts from, and every run sampled only that partition.
Neither the skill's §3 table nor its §11 checklist asked about the other partition, and `final-review`'s item on
partitions and `adversarial-code-review`'s compatibility area did not name it as a question to ask. The change adds
the rule to §3 and §4, a row to §3's table, a bucket entry to §10, a checklist item to §11, and one question to each
of the two review skills.
