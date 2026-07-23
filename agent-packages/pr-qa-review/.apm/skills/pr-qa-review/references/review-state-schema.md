# Review state

`review-state.json` is the durable source of workflow state. The report presents this state for people; it does not
replace the ledger. Update the file after every transition and before delegating work.

Create a new package with the bundled `scripts/init-review-package.py`. The initializer refuses to overwrite an
existing package. Resume an existing ledger instead of reconstructing it from conversation history.

## Required structure

```json
{
  "schema_version": 1,
  "review_status": "complete",
  "workflow_state": "COMPLETE_OR_LIMITED",
  "capability_discovery": [],
  "target": {
    "initial_base_oid": "1111111111111111111111111111111111111111",
    "initial_head_oid": "2222222222222222222222222222222222222222",
    "final_head_oid": "2222222222222222222222222222222222222222",
    "status": "current"
  },
  "permissions": [],
  "actions": [],
  "coverage": [],
  "checks": []
}
```

Use `current` or `updated_and_delta_reviewed` for a final target. Use `complete` or `limited` only after fresh package
validation. A preliminary state may use `blocked` or `stale`, but those values cannot pass final validation.

Before the first permission question, set `workflow_state` to `AWAIT_ACCESS_PERMISSION` or
`AWAIT_CAPABILITY_INSTALL_PERMISSION` and run the validator with `--gate discovery`. The discovery gate requires one
planned check for every required evidence slot and one unresolved candidate permission for the concrete implementation
named by each check.

`capability_discovery` contains exactly one record for each source class: `repository-native`, `harness-tools`,
`local-executables`, and `local-runtimes`. Each record has `status: inspected` or `status: unavailable` and concise
non-secret `evidence`. This proves that implementation selection considered the active harness and machine rather than
assuming a fixed tool list.

A browser UI coverage row uses `evidence_profile: web-ui`. The validator requires `entry-wide`, `changed-wide`,
`entry-narrow`, `changed-narrow`, `console`, `network`, `accessibility`, and `keyboard` slots for this profile.

## Permission record

Each selected implementation and target has a separate record:

```json
{
  "id": "browser-read",
  "implementation": "browser-adapter-name",
  "target": "https://review.example.test",
  "access_mode": "read-only",
  "status": "approved",
  "decision_source": "user",
  "decision_evidence": "User approved browser access for this URL.",
  "allowed_actions": ["navigate", "inspect-console", "capture-screenshot"]
}
```

Use only `approved`, `denied`, or `unresolved`. For a terminal decision, set `decision_source` to `user` and retain a
concise `decision_evidence` record. Agent inference, local ownership, or tool availability is not permission. An action
references one approved permission and repeats its implementation, target, and access mode. The action name must
appear in `allowed_actions`.

## Coverage and checks

A coverage row declares its required evidence slots. A check satisfies one slot and records owner binding, permission,
implementation, status, and retained artifacts.

```json
{
  "coverage": [
    {
      "id": "web-ui",
      "required": true,
      "status": "complete",
      "impact": "none",
      "required_slots": ["entry-wide", "changed-wide", "entry-narrow", "changed-narrow", "console", "network"]
    }
  ],
  "checks": [
    {
      "id": "entry-wide",
      "coverage_id": "web-ui",
      "slot": "entry-wide",
      "required": true,
      "status": "satisfied",
      "permission_id": "browser-read",
      "implementation": "browser-adapter-name",
      "owner": "root",
      "owner_can_invoke": true,
      "artifacts": ["screenshots/entry-wide.png"]
    }
  ]
}
```

Use `planned`, `running`, `satisfied`, `denied`, `unavailable`, or `not_applicable` for checks. `denied` and
`unavailable` require an impact. `not_applicable` requires an observable reason. Artifact paths are non-empty,
review-package-relative files; never record `/tmp` or a parent-directory traversal.

Derive required coverage status from its checks:

- `complete`: every required check is `satisfied` or justified `not_applicable`;
- `limited`: at least one required check is `denied` or `unavailable`, and none is open; or
- `blocked`: at least one required check is `planned` or `running`.

A final review must contain at least one required coverage row. An empty coverage ledger cannot validate as complete.
