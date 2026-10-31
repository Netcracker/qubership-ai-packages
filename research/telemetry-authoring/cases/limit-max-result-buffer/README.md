# Case: a limit set in a connection property

The input restates the `maxResultBuffer` exception of pgjdbc from `../../ab-max-result-buffer.md` as notes. The limit
is set away from the call site, the reader may decide to raise it, and the request can change instead, so every row of
the subsection on the caller's channel applies except what to report. The case checks that the conditions added in
1.2.0 still let the rows through.

## Skill parts

- `SKILL.md`: §2 (What a message on the caller's channel carries)
- `english-developer-style`: §5 (an apostrophe inside a format pattern; sizes in two forms), §7 (Error and log
  messages)

## Checks

1. **Placeholders kept** (`placeholders_kept`) and **no apostrophe** (`no_apostrophe`), which would turn `{0}` into a
   literal.
1. **Why the limit exists** (`why_the_limit`): it bounds the client memory one result takes.
1. **Where to change it** (`names_the_property`): `maxResultBuffer`, named as a connection property.
1. **A value form** (`value_form`): a byte count, a suffixed size, or a percent of the heap, or at least the unit.
1. **An alternative to raising the limit** (`alternative_to_raising`): fewer rows or columns, or a fetch size with
   autocommit off.
1. **The connection is closed** (`connection_closed`), so the application needs a new one.
1. **No wrong advice** (`no_wrong_advice`): no raised value at or below the current limit, and no fetch-size advice
   without autocommit off.
1. **Length** (`length`), recorded and not graded: the earlier trial measured 50 to 103 words.

## Results

Runs of 2026-10-31, graded by reading; both models at the default effort. The new arm ran on skill tree `f3764558`
(`<model>/skill-tree`), the baseline on `9d2eab7`.

Every run passes checks 1, 2, 3, 5, 6, and 7: why the limit exists, `maxResultBuffer` by name, a fetch size with
autocommit off as the alternative to raising it, the closed connection, and no wrong advice.

| Run | Value form (4) | Alternative (5) | Length (8) |
| --- | --- | --- | --- |
| Opus r1 | the unit (`at least {0,number,#} bytes`) | fetch size with autocommit off, fewer rows or columns | 113 words |
| Opus r2 | byte count, `500M`, and `20p` | fetch size with autocommit off, fewer rows or columns | 133 words |
| Sonnet r1 | byte count, `100M`, and `10p` | fetch size with autocommit off, fewer rows or columns | 143 words |
| Sonnet r2 | fails: `raise the maxResultBuffer connection property`, with no value or unit | fetch size with autocommit off | 85 words |
| Opus baseline r1, r2 | byte count, suffixed size, percent of the heap | fetch size with autocommit off, fewer rows or columns | 137, 147 words |
| Sonnet baseline r1, r2 | the unit | fetch size with autocommit off, fewer rows or columns | 105, 100 words |

A draft of 1.2.0 that dropped "with a value it accepts" from the way-out row also left one Sonnet run with no value or
unit; the clause was put back, and one Sonnet run of four still gives none.
