## LLM usage statistics

The goal is to measure AI agents’ contribution to development by tracking their token usage and associated costs over
a specified period.

AI agents must append a signature to the pull request description, issue body, top-level comment, or review body
reporting a run's result, including when the agent stops for human assistance. When the result is reported in a pull
request description or issue body, no additional comment is needed solely to carry the signature. Inline comments
belonging to a review carry no signature. Report totals for the whole run, including subagents and retries, once
rather than repeating them across multiple publications.

Place the signature on the last line, separated from the body by a blank line. Wrap it in `<sub>` tags so it
renders in small type, without backticks:

```markdown
<sub>🤖 gpt-6.1 high in=12k cached=40k out=3k usd=0.083</sub>
```

Start with 🤖 (ROBOT FACE, U+1F916). The first word without `=` is the model identifier reported by the runtime for the
main agent publishing the result. The second, optional word is its reasoning effort, such as `low`, `medium`, or `high`.
Usage and cost totals also include work by subagents using other models.

Separate the remaining fields with spaces. Each field is `key=value`; fields may appear in any order:

- `in`: input tokens that are not cache reads, including cache writes. For OpenAI, subtract `cached_tokens` from
  `prompt_tokens`. For Anthropic, add `cache_creation_input_tokens` to `input_tokens`.
- `cached`: input tokens read from the cache.
- `out`: output tokens, including reasoning tokens.
- `usd`: cost in US dollars, rounded to two significant digits, such as `0.0042`, `0.083`, or `1.3`.

Use `k` for thousands of tokens, such as `12k` or `12.5k`. Use usage and cost data provided by the runtime. Omit any
unavailable field, including effort; a missing field means its value is unknown. Never invent values or report
unavailable usage as zero.

```markdown
<sub>🤖 gpt-6.1 high</sub>
```

The model identifier and numeric values above are illustrative.
