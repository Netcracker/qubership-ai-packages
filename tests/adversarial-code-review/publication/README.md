# Publication simulation

`api.py` is a local stateful substitute for GitHub/GitLab operations. It records calls and resulting state without
contacting a live service. `fixtures.json` contains a replay derived from PR #106 and a synthetic clarification case.
The replay uses supplied evidence from a published review; it does not independently verify the code. The GitLab
mirror preserves source links and tests shared decisions, not native CLI syntax, URL mapping, or permissions.

Copy `api.py` and `fixtures.json` to a fresh temporary directory. Give a fresh Sol medium agent the selected skill and
this API contract, without the fixture source, scorer, recorded states, or earlier results:

```text
python3 /temporary/directory/api.py SESSION CASE PLATFORM OP [PAYLOAD_FILE]
```

Use `real_replay` and `clarification` as independent cases, each on `github` and `gitlab`. JSON payloads come from the
agent's own files. Operations:

| Operation | Payload | Response |
| --- | --- | --- |
| context | none | Identity, revision, verified fixture evidence, thread IDs, user request |
| revision | none | Current authoritative revision tuple |
| threads | none | Full discussions with authors, comments, links and state |
| thread | `{"thread":"ID"}` | One full discussion |
| reply | `{"thread":"ID","body":"text"}` | ID and acceptance |
| resolve / reopen | `{"thread":"ID"}` | Acceptance only |
| publish | `{"result":"APPROVE","body":"text","revision":{...}}` | ID and acceptance |
| reviews | none | Published reviews |

Ask the agent to execute publication according to the skill, then provide a short user report. Inline feedback uses
`reply` on the relevant existing thread. State files under `SESSION/` are evaluator output, not agent input.
Use session name `compact_result` for the final skill, which leaves model attribution to its caller.

Score the committed final traces from the repository root (exits 1 for the recorded missing revision refreshes):

```shell
python3 tests/adversarial-code-review/publication/score.py \
  tests/adversarial-code-review/publication/recorded compact_result
```

For a new run, pass its temporary directory instead. The optional final argument selects a session; omitting it
includes the earlier `compact_harness` traces, which fail on the extra PR/MR heading. The scorer checks selected
outcome, content, and ordering rules,
not every skill requirement. It exits nonzero on failures or missing runs. Inspect the actual text and calls too.
The simulator was checked with reply, resolve, publication and read-back transitions; the scorer rejected an incomplete
workflow missing counts, links, attribution checks and revision refreshes. It does not simulate races or network errors.
