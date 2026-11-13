## LLM usage statistics

The goal is to identify GitHub work performed with AI-agent assistance and track how its share changes over time
relative to all publications in scope. Signatures mark AI-assisted publications; optional token usage
and cost fields provide additional resource-consumption data.

AI agents must append their own signature whenever they create or edit a GitHub comment, including top-level
comments, inline review comments, review bodies, progress updates, and requests for human assistance. The same
requirement applies when agents create or edit pull request descriptions and issue bodies, regardless of who
originally authored them.

For each reporting period, the AI-assisted share is the number of publications with at least one signature added
when creating or editing that publication, divided by the total number of publications in scope created during
that period. Assign publications to periods by their creation date and classify them using their current content.
Later AI-assisted edits may therefore change the share for an earlier period. This measures marked publications;
the absence of a signature does not prove that a publication was created entirely by humans. Quoted, copied,
or example signatures do not qualify a publication as AI-assisted.

Place the signature on the last line, separated from the body by a blank line. Wrap it in `<sub>` tags so it
renders in small type, without backticks. The signature has the following format:

```markdown
Template:
<sub>🤖 MODEL EFFORT IN OUT CACHED COST</sub>

Example:
<sub>🤖 gpt-6.1 high in=12k cached=40k out=3k usd=0.083</sub>
```

Only 🤖 and MODEL are required. EFFORT, IN, OUT, CACHED, and COST are optional placeholders for the fields described
below; do not include the placeholder names literally. Treat each optional field independently. Include a field
only when its value is available from the runtime and, for numeric fields, can be allocated without double counting.
If a value is unavailable, omit only that field; this does not require omitting other known fields. In particular,
an unknown cost does not require omitting known token usage or reasoning effort. The required signature may be
published before usage and cost are known.

Start with 🤖 (ROBOT FACE, U+1F916). MODEL is the model identifier reported by the runtime for the main agent
publishing the content. If the runtime does not provide the model identifier, use `MODEL-UNKNOWN`.
EFFORT is its optional reasoning effort, such as `low`, `medium`, or `high`.

MODEL and EFFORT describe the main agent publishing the content. Numeric fields may include usage and costs
from subagents and retries involving other models or reasoning efforts; they do not represent a per-model breakdown.

Separate the remaining optional fields with spaces. Each field is `key=value`; fields may appear in any order:

- `in` (IN): input tokens that are not cache reads, including cache writes. For OpenAI, subtract `cached_tokens`
  from `prompt_tokens`. For Anthropic, add `cache_creation_input_tokens` to `input_tokens`.
- `out` (OUT): output tokens, including reasoning tokens.
- `cached` (CACHED): input tokens read from the cache.
- `usd` (COST): cost in US dollars, rounded to two significant digits, such as `0.0042`, `0.083`, or `1.3`.

Report all token usage and costs incrementally: each signature records only the usage and cost allocated to that
publication, not cumulative session totals already reported elsewhere. Declared usage and cost are the sums of the
corresponding fields across signatures. For example, two comments under the same issue reporting `in=10k` and
`in=5k` represent `15k` input tokens in total. The same additive rule applies to `out`, `cached`, and `usd`.

Report only known usage and costs that can be allocated to the publication without double counting. Partial sums
are allowed, including when data for some subagents, retries, or parts of the session is unavailable. Reported
amounts do not need to reconcile with session totals. Include known usage and costs from subagents and retries
where available, counting each portion only once. A reported numeric field represents the known allocated amount
and does not imply complete coverage.

When editing an existing publication, preserve every existing signature verbatim except when correcting an error
and append a new signature on the last line, separated by a blank line. Do not replace or recalculate earlier
signatures except to correct an error. An erroneous signature may be corrected or replaced without retaining
its previous version. The new signature identifies the agent performing the edit and may report previously unreported
usage and costs allocated to the same publication, including its earlier creation or editing operations.
Count each portion only once; modify earlier signatures only to correct errors.

When calculating totals, count only signatures added when creating or editing the publication itself, including
signatures from earlier edits retained in its current content. Count each such signature once. Exclude signatures
reproduced as quoted, copied, or example content. Do not additionally count copies from earlier revisions.

Use `k` for thousands of tokens,
such as `12k` or `12.5k`. Use usage and cost data provided by the runtime. Omit any unavailable optional field,
including effort; a missing field means its value is not reported in this signature, not necessarily unknown.
Never invent values or report unavailable usage as zero.

Minimal signature:

```markdown
<sub>🤖 gpt-6.1</sub>
```

The model identifier and numeric values above are illustrative.
