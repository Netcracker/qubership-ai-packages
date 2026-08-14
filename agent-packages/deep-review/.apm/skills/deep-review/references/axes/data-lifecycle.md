# Axis: data lifecycle, durability, and recovery

Finding prefix: `DATA`.

Everything the system persists and everything it can lose. Run this axis wherever state outlives a process: a
database, a file, a cache that is trusted, a queue, an external system the code registers things in.

## Ownership and truth

- For each piece of state: who owns it, who caches it, and what happens when the copies disagree. State with two
  writers and no arbitration is the highest-severity pattern on this axis.
- Is divergence detectable at all? A cache that cannot be compared against its source will be wrong silently and
  indefinitely.
- Is there a repair path — a resync, a reconcile, a rebuild — and does anything trigger it, or does it require a human
  who knows it exists?

## Schema and migration

- How does a schema change reach existing data? Forward migration, backward compatibility of the reader, and what
  happens to a rolling deployment where both versions run.
- Are migrations idempotent, and what does a migration killed halfway leave behind?
- Is there a down path, and if not, is that stated? An irreversible migration shipped without a note is a finding.
- Does anything validate that the code's model and the stored schema still agree, or is drift discovered by a
  production failure?

## Durability

- Write ordering and atomicity: an operation that updates two stores, or a store and an external system, with no
  transaction. Enumerate what a crash between them leaves, and what fixes it.
- Fsync and acknowledgement semantics: when the code reports success, what has actually been made durable?
- Deletion: is it a tombstone, a cascade, or a hard delete? What else does the cascade reach — this is where
  accidental data loss lives. Trace every ownership reference that can cascade.
- Retention and cleanup: what grows forever, what deletes on a schedule, and can a cleanup job delete live data
  because of a clock skew, an empty query result, or a filter that matched nothing?

## Recovery

Trace these explicitly and report what the system does:

1. Restore the datastore from a backup taken an hour ago while the rest of the system keeps running. What is now
   inconsistent, and what repairs it?
2. Replay or re-apply the declarative inputs from scratch against live state. Is that safe?
3. Lose an entire component and rebuild it empty. What can it recover from its peers, and what is gone?
4. Delete the top-level object a user owns. What survives in the external systems, and who cleans it up?

## Rules

Any path where the system can lose or silently corrupt user data under normal operation, with no attacker involved, is
`CRITICAL` regardless of how unlikely it looks. Trace it completely and say what would settle the remaining doubt.
