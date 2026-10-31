# Measuring AI agent autonomy in development

## 1. Goal

We measure how independently AI agents can complete development tasks, from receiving a task to delivering a verified
and accepted result. How often developers use AI is a separate measure of adoption.

The system must answer three questions:

1. Which tasks can agents complete without substantive human assistance?
2. What causes agents to stop and request help?
3. How quickly do we remove these limitations, and do the same blockers recur less often?

The data supports specific improvements: clearer requirements, better documentation, tools and access, test
environments, agent instructions, and approval policies.

A mandatory approval is part of a correct process. An agent that prepares a change and waits for authorization
required by policy has followed that process. Approval waiting time still counts because it affects delivery time.

Success means a growing share of accepted results delivered without a human correcting or completing the work,
while maintaining quality. It also means fewer recurring blockers and less time spent removing them.

### Assumption and scope

Collection of statistics about which tasks were performed and how they were executed is outside the scope of this
design. This design assumes that the required task and execution data is available from a separate collection process.
It defines stop reason labels, recording rules, and measures for identifying and removing limitations on autonomy.

## 2. Stop reason labels

Use the `needs-human:*` namespace.

Each label identifies why an agent cannot continue independently. It describes a current blocker; it does not assess
result quality or automatically determine the autonomy of the whole task.

| Label | When to apply | Example |
| --- | --- | --- |
| `needs-human:approval-required` | The next action requires an explicitly defined approval. | Plan approval, deployment authorization, or mandatory review. |
| `needs-human:risk-found` | The agent identifies a significant risk, and existing rules do not establish whether it may proceed. | An irreversible data migration without a defined approval process. |
| `needs-human:decision-required` | A choice between alternatives or a resolution of conflicting requirements is needed. | Choosing between incompatible API behaviors. |
| `needs-human:context-missing` | Required facts, documentation, or system knowledge are missing. | The required namespace and the reason for using it are undocumented. |
| `needs-human:access-missing` | Required permissions, credentials, tools, or connections are unavailable. | The agent cannot read logs or run a command in staging. |
| `needs-human:verification-blocked` | The agent can prepare the result but cannot adequately verify its correctness. | No test environment, benchmark, or way to check the UI is available. |
| `needs-human:environment-blocked` | An environment failure unrelated to the current change blocks execution. | A service is unavailable, the default branch is broken, or CI capacity is exhausted. |
| `needs-human:external-dependency` | Progress depends on a result outside the current task and the agent's control. | Data from the bug reporter or an upstream fix is pending. |
| `needs-human:conflict-unresolved` | The work overlaps with another change, and the agent cannot resolve the overlap independently. | An unresolved merge conflict or competing pull requests. |
| `needs-human:scope-review-required` | Completing the task requires changing its boundaries or decomposition. | A change in another repository is required but was outside the task's scope. |
| `needs-human:invalid` | The agent finds grounds for not performing the original task and waits for confirmation. | The task is a duplicate, is already fixed, or describes intended behavior. |
| `needs-human:stuck` | The agent cannot find a workable next step after reasonable attempts. | Repeated fixes fail to resolve a test failure. |
| `needs-human:disagreement` | Participants in an automated process cannot resolve a substantive disagreement. | Implementation and review agents repeat their arguments without progress. |
| `needs-human:budget-exhausted` | A defined time, cost, token, or iteration limit has been reached. | The allowed number of fix and review cycles is exhausted. |

### Selection rules

Apply these distinctions consistently:

- Use `needs-human:approval-required` when an approval rule exists. Use `needs-human:risk-found` when the risk is identified
  but the rule is missing or
  ambiguous.
- Use `needs-human:decision-required` when someone must choose. Use `needs-human:context-missing` when a fact must be
  established.
- Use `needs-human:access-missing` when the agent cannot perform a required action. Use `needs-human:verification-blocked` when
  it cannot establish that
  the result is correct.
- Use `needs-human:environment-blocked` when an available environment fails. Use `needs-human:external-dependency` when a
  result from an external participant
  or system is required.
- Use `needs-human:scope-review-required` when the task boundaries need revision. A large amount of work alone is not a
  stop reason.
- Use `needs-human:stuck` when there is no workable path forward. Use `needs-human:budget-exhausted` when a configured limit
  stops further work.

Apply a label only when the agent actually stops. If it resolves a conflict, restores the environment, or finds the
documentation independently and continues, no stop label is required.

## 3. Recording a stop

When the agent stops, it:

1. Applies the primary reason label to the issue or pull request where action is required.
2. Posts a structured comment.
3. Specifies what enables work to resume.

Example:

```text
Reason: needs-human:access-missing

Blocker:
I cannot retrieve application logs from staging to test the hypothesis.

Work completed:
The error is partially reproduced locally. The service and time interval are identified.

Required action:
Grant read access to the logs or attach the logs for the specified interval.

Resume condition:
The logs are available to the agent.

Related issue for removing the limitation:
<issue reference>
```

Choose one primary reason for each stop episode. Describe independent additional blockers in the comment. Create
separate stop records if they require separate actions.

A human can correct the classification. Preserve both the original record and the correction in the event history.

Remove the label after the blocker is resolved and work resumes. Labels show current blockers; the event history
preserves every stop, including repeated stops.

If an issue and a pull request represent the same task, record the stop in one place and link to it from the other.
Count that stop once.

## 4. Measuring how limitations are removed

Record the following for each stop:

- The task and execution attempt.
- The reason and a short description of the specific limitation.
- The times when work stopped and resumed.
- The action a human actually performed.
- The related issue for removing the limitation, if it can recur.

Distinguish unblocking one task from removing a recurring limitation. A human who runs a command manually unblocks
the task. Giving the agent the required tool with appropriate permissions can prevent future stops for that reason.

| Metric | What it shows |
| --- | --- |
| Share of tasks accepted without substantive human assistance | The agent's ability to complete work independently. |
| Share of attempts with stops, by reason | The most common limitations. |
| Stops per 100 comparable attempts | Whether blocker frequency changes relative to the volume of work. |
| Median and 90th percentile time to resume | How quickly tasks are unblocked. |
| Time from identifying a recurring limitation to a verified fix | How quickly systemic improvements are delivered. |
| Recurrence of a specific limitation after a fix | Whether the cause was actually removed. |
| Human time spent providing assistance | The actual need for manual involvement. |
| Reverts and reopened tasks | Whether result quality is maintained. |

Compare metrics within similar task types and sizes. AI usage frequency provides context about adoption, but it is
not a measure of autonomy.

## 5. Interpretation limits

A stop reason alone does not determine the outcome. After `needs-human:access-missing`, a human might grant access, perform
  the
action, or take over the task entirely. These are three different outcomes.

Determine the final degree of autonomy from the assistance actually provided, rather than a fixed mapping from
stop reason to autonomy level.

- An absence of recorded stops establishes autonomy only if event collection is complete.
- Record approvals separately from assistance in solving the task.
- `needs-human:environment-blocked` and `needs-human:external-dependency` can expose limitations of the autonomous process even
  when the agent is not at fault.
- Interpret fewer stops together with result quality and task complexity.

For the first phase, labels, structured comments, and stop history are sufficient. Use them to identify the most
frequent and costly limitations, create issues to remove those limitations, and check the effect of each improvement.

## 6. Security

1. The AI agent must respond to and take into account only issue and pull request comments from authorized users.
   Authorization is determined by the repository's applicable `CODEOWNERS` rules for the files or area affected by
   the task. The comment author must be a listed owner or a member of a listed owner team for that scope. Ownership
   of an unrelated area does not authorize a user to direct the agent on the current task. If authorization cannot
   be established, the agent must not act on the comment or treat it as an instruction, decision, or approval.
