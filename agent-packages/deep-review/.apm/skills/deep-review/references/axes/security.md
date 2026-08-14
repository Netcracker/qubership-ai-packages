# Axis: security

Finding prefix: `SEC`.

Defensive review of code the team owns, before it ships. Assess exposure and give the maintainers what they need to
fix it. Do not write exploit tooling; a proof-of-concept input that demonstrates the defect in a test is appropriate,
a weaponized exploit is not.

## Start with the model

Write the threat model down before reviewing anything, in five lines: what this component protects, who can reach it,
what a caller is trusted with, what the deployment assumes, and what is explicitly somebody else's problem. Most
false findings on this axis come from reviewing without one.

For a library, the attacker is usually the data, not a user: the peer that sends the bytes, the file being parsed, the
configuration being loaded.

## Areas

- **Input handling.** Every parser and deserializer reachable from untrusted data: unbounded allocation from a
  length field, recursion without a depth limit, index arithmetic on attacker-controlled offsets, format strings,
  path traversal in anything that opens a file by name, and deserialization of arbitrary types.
- **Injection.** SQL, command, LDAP, template, header, and log injection. Follow untrusted data to every sink; note
  where parameterization or escaping is missing rather than where it is present.
- **Secrets.** Credentials, tokens, and keys in source, tests, defaults, sample configuration, and error messages.
  Whether secrets reach logs, exception messages, stack traces, or crash dumps. How they are held in memory and
  whether they are cleared.
- **Cryptography and transport.** TLS verification that can be disabled and whether anything disables it by default;
  certificate and hostname validation; protocol and cipher selection; random number sources for anything security-
  relevant; home-grown cryptography of any kind.
- **AuthN/AuthZ** for components that have them: where the decision is made, whether every path goes through it, and
  what an unauthenticated caller can still reach or learn.
- **Resource exhaustion by design.** Unbounded queues, no rate limit, no timeout, a decompression ratio nobody
  checks, an allocation proportional to an attacker-supplied number.
- **Trust boundaries in the build.** Unpinned actions, scripts fetched at build time, publishing credentials in CI,
  and anything that runs attacker-influenced code during a build.
- **Information disclosure.** Error responses and logs that leak internal paths, versions, queries, or user data.

## Rules

- Every finding names the reachable path from an untrusted source to the sink. A dangerous function that no untrusted
  input reaches is `LOW` at most, and say why.
- **No generic hardening wishes.** "Should validate input", "should use a security header", "should rotate keys" are
  not findings unless a project requirement, a rendered configuration, or a reachable path makes them actionable
  here. This axis attracts checklist output more than any other, and a report padded with unreachable advice teaches
  the reader to skip it — which is how the one real finding gets missed.
- Distinguish "vulnerable" from "would be vulnerable if X". Name X.
- Where the ecosystem has a scanner (CodeQL, Semgrep, `gosec`, Bandit, SpotBugs with FindSecBugs), run it and triage
  its output rather than pasting it. An unreviewed scanner dump is not a report.
- Do not restate `dependencies` findings. Reference them and add the exploitability judgment they lack.
