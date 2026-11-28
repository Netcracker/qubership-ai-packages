# Sharded correctness pass over internal/regogen (experiment)

Merged from the seven answers in ../sharding/. Paths relative to the repo root in shard-wt.

| Shard | Files (non-test) | Lines |
| --- | --- | --- |
| s1-assembly | regogen/gen.go, expr.go, comment.go, failures.go, iterate.go, report.go, tables.go, groups.go lines 1-212 (generation half) | ~2.7k |
| s2-leaf | regogen/leaf.go, template.go, rel.go, subset.go, eqtokens.go, operand.go, deep.go | ~3.4k |
| s3-projection | regogen/project.go, request.go, bulk.go, subject.go, local.go, mapping.go, jsonpath.go, groups.go lines 213-end (Go runtime evaluator EvalGroups) | ~2.8k |
| s4-sources | regogen/pipcall.go, entitlements.go, scope.go, pipreplay.go, networkpip.go, internal/regobuiltins/httpsend.go, builtins.go | ~2.2k |
| s5-filter-algebra | regogen/filter.go, filteralg.go, filterrows.go | ~1.3k |
| s6-filter-text | regogen/filtertext.go, filtersub.go, rsql.go (+ filterrows.go as overlap) | ~1.5k |
| seams | the cross-shard contracts listed below | — |

Not covered (lowest risk per all planners): spectables/, agent-tables.json, cmd/.

Seams for the seam reviewer:
1. check vs filter on the same tree: the filter must never return a row the check denies, and must not drop a row the check allows where the contract says exact.
2. Rego emission vs the Go evaluator in groups.go (EvalGroups, test.holds, deepHolds): both must decide the same.
3. Input keys: what project.go/request.go/bulk.go write into input (input.class, element keys, Record fields) vs what the generated rules read.
4. PIP result flow: pipResolve / setCalls / Values into records, leaf states (ERR, ABSENT, PIP_NULL) and filter text substitution (filtersub callGeneral).
5. Snapshot reuse: components/authz-agent/internal/snapshot reuses a snapshot when the hash of policyir Tree.Dump() is unchanged; every IR field the generator reads must be in Dump.
6. Refusals: RejectedError / Failure from the generator into refusal reasons and health in snapshot/server.
