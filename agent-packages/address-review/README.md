# address-review

A user-invoked skill for the author of a pull or merge request: take the review findings (a `review.json` or a ledger
from a review skill, a pasted report, or the open review threads), decide for each whether it is valid, already fixed,
disputed, or out of scope, group the valid ones by root cause, and fix each group once, at the layer where the cause
lives. Each finding is stated as the rule the code broke, and the fix covers its cousins: the other cases of that rule
the request's code reaches, with a test at the boundary where the rule stops. The fixes then go through an independent
review (up to five rounds) and `final-review`, which receives the ledger and checks that every finding is fixed,
deferred with a follow-up, or disputed with evidence.

The independent review is `cross-review` where that skill and the Codex CLI it runs are installed. Without them, the
skill runs the review in a fresh subagent or agent session that gets the diff, the task statement, and the ledger, and
none of the fixing session's reasoning. Neither `cross-review` nor `review-delivery` is a dependency; `final-review`
is.

It does not push or reply to reviewers unless asked in the session. Where `review-delivery` is installed, replies follow
its authorization rules; otherwise the user approves each draft before it is posted.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/address-review
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/address-review#<ref>
```

Replace `<ref>` with the release tag, branch, or commit SHA you want to pin.

Then run `apm install` and `apm compile`.
