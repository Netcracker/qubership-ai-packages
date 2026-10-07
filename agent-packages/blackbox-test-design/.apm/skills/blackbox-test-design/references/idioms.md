# Implementation idioms per area and platform

Use with §6 of `SKILL.md`. Each row is a boundary where a reference built on a given platform most likely
does whatever a common library call does. Turn each alternative the model does not use into a standing hypothesis at
every handling point the row applies to. The lists are starting points, not complete; add what you find.

## Contents

- Areas common to all platforms
- JVM (Java, Kotlin, Scala)
- .NET (C#)
- Python
- Go
- JavaScript and TypeScript (Node, browsers)
- JSON binding layers
- SQL and databases
- Web frameworks and HTTP

## Areas common to all platforms

| Area | Alternatives to consider |
| --- | --- |
| Trimming | none; ASCII space only; all control characters up to U+0020; Unicode whitespace; only one end |
| Emptiness | `null` only; empty; blank (whitespace only); absent key versus `null` versus `""` treated alike or not |
| Splitting | trailing empties kept or dropped; leading empties kept or dropped; regex or literal separator; parts trimmed or not; a limit on the number of parts; a quoted separator respected or not |
| Case | case-sensitive; ASCII-only case folding; Unicode case folding; locale-dependent lower or upper casing (the Turkish dotless i) |
| Number parsing | integer only; floating point; arbitrary precision; leading `+`; leading zeros (and octal readings); exponent; `NaN` and `Infinity`; locale decimal separator; overflow wraps, saturates, fails, or falls back to text |
| Number printing | the text as written; shortest round-trip floating text; fixed scale; arbitrary precision with trailing zeros kept or stripped; scientific notation above a threshold |
| Number comparison | numeric; by text; by value and scale; mixed number and string coerced one way or the other |
| Equality of structures | ordered; as sets; by printed text; by serialized JSON; element-wise with coercion |
| Collection order | insertion; sorted; hash order (stable per process, per run, or per content); deduplicated or not |
| Printing a value | JSON; the platform's default `toString` of a map or list; strings quoted or not; `null` versus `"null"` versus empty |
| Patterns | regex metacharacters passed through; escaped; glob; anchored or not; whole-match versus find; dot matches newline or not |
| Templating | substitution once or recursively; escape syntax; default-value syntax; unresolved placeholders left as is, emptied, or an error |
| Dates and times | time zone of parsing; leap seconds; lenient parsing that rolls over (February 30); epoch in seconds or milliseconds |
| Encoding | UTF-8 versus platform default; normalization form (NFC or NFD) before comparison; byte length versus character length limits |
| Exceptions | which failures stop the whole operation, which skip one part, which become a default value, which are logged and ignored |
| Error mapping | which input failures become 400, 409, 422 or 500; whether the body carries the message |
| Limits | column or field length enforced at input, at storage (late failure), or not at all; recursion depth |

## JVM (Java, Kotlin, Scala)

- `String.trim()` strips every character up to U+0020, including control characters; `strip()` strips Unicode
  whitespace; `isEmpty` versus `isBlank` (and the commons-lang `StringUtils` variants, which are null-safe).
- `String.split(regex)` takes a regex and drops trailing empty strings; a limit of `-1` keeps them.
- `equalsIgnoreCase` versus `toLowerCase()` with the default locale.
- `Integer.parseInt` accepts a leading `+` and rejects whitespace and decimals; `Double.parseDouble` accepts
  surrounding whitespace, exponents, `NaN`, `Infinity`, and a trailing `d` or `f`.
- `BigDecimal.equals` compares scale (`1.5` is not `1.50`); `compareTo` does not. `BigDecimal.toString` may print
  scientific notation; `toPlainString` does not. `new BigDecimal(double)` exposes binary floating error.
- `Double.toString` uses scientific notation outside 10^-3 to 10^7.
- `HashMap` and `HashSet` iterate in hash order, which depends on the content's `hashCode` (stable across runs for
  strings and records, not for objects using identity hash).
- `String.matches` anchors the whole string; `Matcher.find` does not; `Pattern.quote` is often forgotten.
- `String.format` and `MessageFormat` differ in quoting; commons-text `StringSubstitutor` resolves recursively and
  supports `$${escape}` and `${name:-default}`.
- Lombok `@EqualsAndHashCode` on mutable entities makes set membership change when fields change.
- Short-circuit `&&` and `||` evaluate left to right; streams are lazy until a terminal operation.

## .NET (C#)

- `string.Trim()` strips Unicode whitespace; `String.IsNullOrEmpty` versus `IsNullOrWhiteSpace`.
- `string.Split` keeps empty entries unless `StringSplitOptions.RemoveEmptyEntries`.
- Culture-sensitive comparison and parsing by default (`CurrentCulture`), versus `Ordinal` and `InvariantCulture`.
- `decimal` keeps scale in `ToString()` (`1.50m` prints `1.50`) but `==` ignores it.
- `Dictionary` enumeration order is insertion order in practice, but not guaranteed after removals.
- `System.Text.Json` is case-sensitive on property names by default; Newtonsoft is not.

## Python

- `str.strip()` strips Unicode whitespace; `split()` without arguments collapses runs of whitespace and drops empties,
  `split(",")` keeps them.
- `int()` accepts surrounding whitespace, underscores, and a sign; `float()` accepts `nan`, `inf`, and exponents.
- `round()` rounds half to even; `Decimal` keeps scale in `str()`.
- `dict` keeps insertion order; `set` order depends on hashing, and string hashing is randomized per process unless
  `PYTHONHASHSEED` is set.
- `re.match` anchors at the start only; `re.fullmatch` anchors both ends.
- `str.lower()` versus `str.casefold()` differ on non-ASCII letters.
- `json.loads` accepts `NaN` and `Infinity` by default and keeps the last of duplicate keys.

## Go

- `strings.TrimSpace` strips Unicode whitespace; `strings.Split` keeps every empty part; `strings.Fields` drops them.
- `strconv.Atoi` rejects whitespace and accepts a sign; `ParseFloat` accepts `NaN`, `Inf` and hex floats.
- Map iteration order is deliberately randomized per iteration.
- `encoding/json` matches field names case-insensitively, ignores unknown fields by default, decodes numbers into
  `float64` in `interface{}` values (precision loss above 2^53), and turns `null` into the zero value.
- `fmt` prints maps sorted by key; `%v` of a nil slice is `[]`.
- `regexp` is RE2: no backreferences or lookaround, so patterns that use them fail at compile time.

## JavaScript and TypeScript

- `String.prototype.trim` strips Unicode whitespace including line terminators.
- `split` keeps empties; `split` with a limit truncates.
- `Number("")` is `0`; `Number(" 12 ")` is `12`; `parseInt("12px")` is `12`; `parseInt("0x10")` is `16`; numbers
  above 2^53 lose precision; `-0` and `NaN` compare surprisingly.
- `==` coerces; `===` does not; `Object.keys` order puts integer-like keys first, in numeric order.
- `JSON.stringify` drops `undefined`, turns `NaN` into `null`, and keeps key insertion order.
- `toLowerCase` versus `toLocaleLowerCase`.

## JSON binding layers

- Jackson (JVM): unknown properties fail or are ignored per configuration; a number or boolean is accepted into a
  string field; enums are case-sensitive by name but accept numeric ordinals; a single value is rejected for a list
  unless `ACCEPT_SINGLE_VALUE_AS_ARRAY`; `null` for a primitive becomes its default or fails; a creator that throws
  becomes a mapping error.
- Gson, Moshi, System.Text.Json, Newtonsoft, Go `encoding/json`, Python `pydantic`: compare the same points. Each
  differs in coercion, case of keys, duplicate keys, and `null` versus absent.

## SQL and databases

- String comparison collation: case and accent sensitivity, trailing-space padding (`CHAR` and some collations
  ignore trailing spaces).
- `NULL` in comparisons and `NOT IN` with a `NULL` element; empty string as `NULL` (Oracle).
- Column length enforced at insert, so an over-long value fails late, often as a generic 500.
- `ORDER BY` absent means unspecified order, often insertion order until a vacuum or index change.
- Numeric types: integer division, rounding on insert into a fixed-scale column.

## Web frameworks and HTTP

- Header names are case-insensitive; repeated headers may be joined with commas or kept separate; the first or the
  last value wins.
- Query parameters: repeated keys, empty values, `+` versus `%20`, matrix parameters.
- Path normalization: trailing slash, double slash, encoded slash, `..`.
- Exception mappers: which exception types map to which status, and what a mapper does with a wrapped exception.
- Validation annotations run at binding time, before business logic; business validation may run later, in a
  transaction, and fail differently.
