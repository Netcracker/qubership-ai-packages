## LLM usage statistics

The goal is to measure AI agents’ contribution to development by tracking their token usage and associated costs over
a specified period.

AI agents must append a signature to every comment they publish, including top-level comments, inline review
comments, review bodies, progress updates, and requests for human assistance. Pull request descriptions and issue
bodies published by AI agents must also carry the signature.

Place the signature on the last line, separated from the body by a blank line. Wrap it in `<sub>` tags so it
renders in small type, without backticks. The signature has the following format:

```markdown
Template:
<sub>🤖 MODEL EFFORT IN OUT CACHED COST</sub>

Example:
<sub>🤖 gpt-6.1 high in=12k cached=40k out=3k usd=0.083</sub>
```

Only 🤖 and MODEL are required. EFFORT, IN, OUT, CACHED, and COST are optional placeholders for the fields described
below; do not include the placeholder names literally.

Start with 🤖 (ROBOT FACE, U+1F916). MODEL is the model identifier reported by the runtime for the main agent
publishing the comment. EFFORT is its optional reasoning effort, such as `low`, `medium`, or `high`.

Separate the remaining optional fields with spaces. Each field is `key=value`; fields may appear in any order:

- `in` (IN): input tokens that are not cache reads, including cache writes. For OpenAI, subtract `cached_tokens`
  from `prompt_tokens`. For Anthropic, add `cache_creation_input_tokens` to `input_tokens`.
- `out` (OUT): output tokens, including reasoning tokens.
- `cached` (CACHED): input tokens read from the cache.
- `usd` (COST): cost in US dollars, rounded to two significant digits, such as `0.0042`, `0.083`, or `1.3`.

When reporting usage and cost totals, include work by subagents and retries. Use `k` for thousands of tokens,
such as `12k` or `12.5k`. Use usage and cost data provided by the runtime. Omit any unavailable optional field,
including effort; a missing field means its value is unknown. Never invent values or report unavailable usage as zero.

Minimal signature:

```markdown
<sub>🤖 gpt-6.1</sub>
```

The model identifier and numeric values above are illustrative.
