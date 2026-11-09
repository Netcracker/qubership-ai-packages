## Change

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0010 R7 | Violated | A loaded key set stays in use until the process restarts, where R7 requires a reload on the first token that needs it after 5 minutes. |
| ADR-0010 R9 | Violated, deferred to issue #301 | `internal/keys` loads a key set on the first token that needs it, not at startup. The code did this before the change too, and the change leaves it as it was. |
| ADR-0020 R3 | Not in force | ADR-0020 has status Proposed, so R3 does not yet replace ADR-0010 R7. If ADR-0020 is accepted, the change also violates R3, because no token reloads a key set after 1 minute. |

The `Defers:` line in the commit message and the description names ADR-0020 R3 and ADR-0010 R9. It does not name ADR-0010 R7. R7 is the accepted rule that the change breaks, so the change neither meets it nor defers it. Deferring ADR-0020 R3 to issue #300 covers a rule that is not in force yet, and R7 is still the rule that applies to this change.

Issues #300 and #301 are both open. `docs/adr/` has no `README.md`, so the repository doesn't document what the Proposed status means or whether a `Defers:` line is an accepted way to postpone a rule. This check reads Proposed with its usual ADR meaning: proposed, not yet accepted.

The check walked every rule in both records.
