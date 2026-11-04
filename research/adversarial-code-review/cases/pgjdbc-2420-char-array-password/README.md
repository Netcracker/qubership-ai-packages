# Case: review pgjdbc/pgjdbc#2420 at a0cab93b, a char[] password that is never cleared

A review case for `adversarial-code-review`. The input is [pgjdbc/pgjdbc#2420][pr] at `a0cab93b`, one commit of 37
changed lines on top of `d281a788`. The change makes `AuthenticationPlugin.getPassword` return `char[]` instead of
`String`, and its commit message says this lets the caller clear the password securely. The gold comes from the inline
comments a maintainer left on this commit in January 2022, a manual review written before agents reviewed code. The
author replied in the thread or changed the code near each of them.

The code base is the pgjdbc of early 2022: the SCRAM code still lives in `org.postgresql.jre7.sasl`, and the commit
predates the `withPassword` and `withEncodedPassword` helpers that the review led to. This is older than the pgjdbc the
model usually knows. A finding that names today's API instead of the code at `a0cab93b` is not a pass.

The prompt names neither the pull request nor its author. The pull request was merged after a later push, so a model
that recognized it could know the fix; the checks only ask for the problem in this commit.

[pr]: https://github.com/pgjdbc/pgjdbc/pull/2420

## What it exercises

- Area *Security, privacy, and supply chain*: secret exposure, here a password left in heap memory after the change
  that claims to make clearing it possible.
- Area *Intent and scope*: whether the change delivers what its commit message states.

## Checks

Grade by reading `result.md`; the grep only finds the candidates. A finding passes as `blocking` or `non-blocking`; a
defect named only in a question under *Needed to complete the review* is partial.

1. **Nothing clears the password array.** Pass: a finding that the driver never overwrites the `char[]` that
   `AuthenticationPluginManager.getPassword` returns (for example with `Arrays.fill`), neither in `getEncodedPassword`
   (`pgjdbc/src/main/java/org/postgresql/core/AuthenticationPluginManager.java:73-83`) nor at the calls in
   `ConnectionFactoryImpl` (lines 500, 759, and 778), and that nothing documents who owns the array and must clear it,
   so the security benefit the commit message claims does not happen. Naming the uncleared `encodedPassword` byte
   arrays (lines 663 and 684) as well is fine. Partial: the report asks for Javadoc on ownership or on the encoding of
   `AuthenticationPlugin.getPassword` without saying the array stays uncleared. Fail: neither.
   `grep -niE 'Arrays\.fill|clear|erase|wipe|zero|owner' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/2420#discussion_r792588677))
2. **The password still becomes a `String`.** Pass: a finding that the change copies the `char[]` into an immutable
   `String`, which the driver cannot clear, at `AuthenticationPluginManager.java:82`
   (`String.valueOf(password).getBytes(StandardCharsets.UTF_8)`) or at the `ScramAuthenticator` call in
   `pgjdbc/src/main/java/org/postgresql/core/v3/ConnectionFactoryImpl.java:791`, so the password stays in heap memory
   on the MD5, cleartext, or SCRAM path; the fix encodes without a `String` (for example
   `StandardCharsets.UTF_8.encode(CharBuffer.wrap(password))`) or changes `ScramAuthenticator`. The commit message
   names the SCRAM conversion as deferred, so a report that only repeats that note without treating it as a gap is
   partial. Fail: neither.
   `grep -niE 'String\.valueOf|immutable|ScramAuthenticator|CharBuffer|heap' result.md`
   ([original comment, line 82](https://github.com/pgjdbc/pgjdbc/pull/2420#discussion_r792588677),
   [original comment, line 791](https://github.com/pgjdbc/pgjdbc/pull/2420#discussion_r792016085))

## Skill parts

- `adversarial-code-review`: `SKILL.md` §Review areas, area *Security, privacy, and supply chain* (secret exposure)
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Intent and scope* (the change solves the stated problem)

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `d281a788b227b73e5a5236a10f3e5f5e73d011e7` (the parent of the pull request's commit), and `a0cab93be327f9379533e27469f28821006cd5b8` (the reviewed commit). |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<head>` replaced by `run-review-case.sh`. |

## How to run

From the repository root, once per model and run:

```bash
research/adversarial-code-review/cases/run-review-case.sh research/adversarial-code-review/cases/pgjdbc-2420-char-array-password <model> <label> <rev>
```
