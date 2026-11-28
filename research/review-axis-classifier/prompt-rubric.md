# Review axes (rubric v1)

Each axis gets one label for the pull request **as submitted** (the initial version):

- `2` required: a focused check on this axis is owed. Either the kind of change mandates it by policy (see "mandated when"), or the initial version has a concrete defect or omission on this axis that a focused reviewer would raise.
- `1` glance: the axis is touched, a quick look is enough, and a focused pass is unlikely to find anything.
- `0` skip: the change does not touch this axis.

| id | axis | mandated when | typical finding |
| --- | --- | --- | --- |
| `tests` | Tests: are the changed or new behaviors covered, can the tests fail, right level | behavior changes (bug fix, feature) | no regression test, test cannot fail, missing negative case |
| `user_docs` | User documentation: docs pages, README, option reference, supported versions, migration notes | the change adds, renames, removes, or changes an option, property, flag, env var, supported version (JDK, database, Gradle), a user-visible error, or user-visible behavior | the docs still list the old JDK version; new property undocumented |
| `doc_comments` | Javadoc and code comments: new or changed contracts documented, comments match the code | public or protected API added or its contract changed; non-obvious code added | changed @throws not updated; comment contradicts code |
| `change_description` | PR title, description, commit message, changelog / release notes | user-visible change, which owes a changelog entry; description does not say why | no changelog entry; title does not describe the change |
| `performance` | Performance; a benchmark or measurement is owed | the change touches a hot path, an allocation- or IO-heavy loop, an algorithm's complexity, or claims a speed-up | quadratic loop; claimed speed-up with no benchmark |
| `security` | Security: authentication, TLS, crypto, parsing untrusted input, injection, resource exhaustion, secrets | the change touches auth, TLS, crypto, credentials, input parsing from the network, quoting/escaping | downgrade possible; unbounded allocation from peer input |
| `backward_compat` | Backward compatibility: public API/ABI, defaults, behavior existing users rely on, persisted or wire formats, supported platforms | the change alters public API, a default, a supported version, or observable behavior | removed public method; changed default silently |
| `concurrency` | Concurrency and resource lifecycle: threads, locks, close/cleanup, leaks | the change touches shared state, locking, streams/connections open and close | resource not closed on error path; race |
| `error_model` | Error model: what is thrown or returned, messages, error codes, diagnostics | the change adds or changes an error path or message | wrong exception type; message without the offending value |
| `correctness` | Logic correctness and edge cases of non-trivial code | non-trivial logic added or changed | off-by-one; null or empty input; wrong branch |
| `user_value` | Is it helpful to users: does it solve the right problem, is the API/UX good, is the feature worth its cost | a new feature, option, or user-facing API | feature solves a non-problem; awkward API; missing the common case |
| `surprising_behavior` | Does it add behavior a user would not expect (least astonishment) | behavior changes in a way a user might notice | silently swallows errors; option has non-obvious side effects |
| `contradictions` | Does the PR add contradictions: between code and docs/comments/tests/description, with similar code elsewhere, or within itself | always a candidate when docs, comments, or description are touched alongside code | description claims X, code does Y; two code paths now disagree |
| `build_ci` | Build, CI, dependencies, packaging, release | build scripts, CI config, dependency versions, published artifacts change | CI matrix no longer covers X; published POM changed |
| `observability` | Logging, metrics, tracing | a new failure, retry, fallback, or state a user waits on | swallowed error without log; log at wrong level |
| `spec_conformance` | Conformance to an external spec: SQL standard, PostgreSQL protocol, JDBC spec, JSpecify, Java language spec | the change implements or interprets an external spec | deviates from the spec section |

## Review plan

Besides the per-axis labels, decide how the review should be organized:

- `single`: one reviewer agent covers all required axes (small or cohesive change).
- `split`: separate focused subagents; give the groups of axis ids, one group per subagent.
