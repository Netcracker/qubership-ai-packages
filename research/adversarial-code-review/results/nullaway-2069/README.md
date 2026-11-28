# Example run: uber/NullAway#2069

One run of `adversarial-code-review` on [uber/NullAway#2069](https://github.com/uber/NullAway/pull/2069) at head
`fc9b07b3`, on November 9, 2026, made before the change description and branch hygiene axes became one axis. The
review was not published to the pull request; the files here are what the skill wrote locally:

- [`ledger.md`](ledger.md): the ledger `review-delivery` rendered, every finding grouped by root-cause class;
- [`review.json`](review.json): the verified findings, in the `review-delivery` schema.

The result is `request_changes` with 34 findings: 1 major, 21 minor, and 12 nit, in 4 root-cause classes. 17 of the
findings are earlier review threads whose defect remained at this head. 15 axes ran; security and reliability were
skipped because the change touches neither. The author then worked through the findings in a separate session: 30
fixed, 3 disputed, and 1 deferred.

## Cost

Every agent ran on Claude Opus 5.5. The run took 80 minutes. Tokens come from the session transcripts, and the price is
$4 per million input tokens, $5 per million 5-minute cache writes, $8 per million 1-hour cache writes, $0.20 per
million cache reads, and $20 per million output tokens.

| Part | Agents | Cache writes (5 minutes unless marked) | Cache reads | Output | Cost |
| --- | --- | --- | --- | --- | --- |
| Orchestrator | 1 | 155643 (1 hour) | 6291890 | 39324 | $3.29 |
| Review axes | 15 | 1513059 | 31478994 | 212700 | $18.12 |
| Diff coverage and mutation measurement | 1 | 289174 | 2113815 | 12027 | $2.11 |
| Verifier | 1 | 112516 | 3051586 | 21862 | $1.61 |
| Total | 18 | 2070392 | 42936285 | 285913 | $25.13 |

Uncached input was 810 tokens in total and adds less than one cent.
