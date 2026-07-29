# Data lifecycle

## Lifecycle model

Map the persisted state transitions changed by the diff before choosing checks. Include schema or format migration,
write-ahead logs (WALs) or segments, sealing, upload, compaction, cleanup, deletion, and reader-visible state. Identify
the owner, trigger, durable marker, retry behavior, and observable evidence for each transition.

Check normal progress and interrupted progress at every affected boundary:

- Verify retention boundaries, expiration comparisons, grace periods, and clock or time-zone assumptions.
- Verify late arrivals, reopened or overlapping windows, and hot/cold overlap without losing or duplicating reads.
- Verify failed and partial upload, sealing, compaction, cleanup, and deletion recovery.
- Verify retries are idempotent and do not orphan objects, duplicate manifests, or repeat irreversible work.
- Verify readers remain safe while writers migrate, seal, upload, compact, replace, or delete data.
- Verify migration and restart behavior with old, new, partial, empty, and already-migrated state.

Use unit or integration tests, fixtures, object inventories, manifests, logs, metrics, and safe read-only observations
as evidence. Do not infer lifecycle completion from a scheduled job or success log when durable state can be inspected.

## Destructive experiment gate

Run retention, cleanup, compaction, deletion, corruption, forced recovery, or similar destructive lifecycle experiments
only in an isolated disposable environment or with explicit permission for the named environment and data. Record the
expected effects, rollback or cleanup, and evidence unlocked before the experiment. When permission or isolation is
unavailable, use the strongest safe evidence and record the missing failure-path or timing coverage and its impact.
