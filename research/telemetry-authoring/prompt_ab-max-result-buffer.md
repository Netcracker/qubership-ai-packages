# Prompts of the maxResultBuffer trial

## Writer prompt

```markdown
When a result set grows past the `maxResultBuffer` connection property, `PGStream.increaseByteCounter` in `pgjdbc/src/main/java/org/postgresql/core/PGStream.java` throws a `PSQLException` with the bare message `Result set exceeded maxResultBuffer`. Replace that message with a proper one.

Do not run Gradle: this environment has no network access, so the build cannot resolve dependencies. Do not commit. When you are done, reply with a short summary of the change.
```

## Writer command

```bash
#!/bin/zsh
# Usage: run.sh <model>-<arm>-<n>. Runs one headless writer in runs/<name> with the arm's skills and instructions.
set -u
EXP=${0:A:h}
name=$1
model=${name%%-*}
arm=${${name#*-}%%-*}
mkdir -p $EXP/logs $EXP/out
cd $EXP/runs/$name || exit 1
CLAUDE_CODE_DISABLE_CLAUDE_MDS=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 claude -p "$(cat $EXP/prompt.md)" \
  --append-system-prompt-file $EXP/arms/$arm/system.md \
  --model $model \
  --setting-sources project \
  --strict-mcp-config \
  --output-format stream-json --verbose \
  --allowedTools Read Grep Glob Edit Write Skill 'Bash(grep:*)' 'Bash(ls:*)' 'Bash(cat:*)' 'Bash(sed:*)' \
  > $EXP/logs/$name.jsonl 2> $EXP/logs/$name.err
diff -ru -x .claude $EXP/base . > $EXP/out/$name.diff
echo "$name done"
```

## Project instructions of arm `old`

Arms `final2` to `final4` use the instructions of `final`.

```markdown
Contents of CLAUDE.md (project instructions, checked into the codebase):

# AGENTS.md

## Word choice in comments, documentation, and names

Use the right-hand column below in Javadoc, inline comments, error and log messages, `CHANGELOG.md`, `docs/`,
commit messages, and pull request descriptions.

| Instead of | Write | Note |
| --- | --- | --- |
| captured | recorded | Keep `capture` where something really is captured: traffic off a socket, a stack trace at the point of failure. |
| ceiling, cap | limit | As noun and as verb: limit a length, do not cap it. |
| desync, desynced | out of sync | |
| end-of-stream, end of the stream, EOF, end of file; the stream ends, has ended, is exhausted | end of stream | The state an `InputStream` reports by returning -1. |
| envelope | message | Name the part: the message, its header, or its body. |
| hard cap, soft cap | say what the limit does | Not `hard limit` or `soft limit` either. |
| legal | valid | |
| self-inclusive | say what the field counts | |
| upper bound on X | largest X | Keep `upper bound` where a lower bound is also in play, or the sentence is about a range. |

The list binds identifiers as well as prose: rename `fieldCap` to `fieldLimit` along with the comment beside it, and
`rejectsAFieldCountBeyondTheEnvelope` to `rejectsAFieldCountBeyondTheMessage`. This covers names you introduce and
names in code you are already changing. Do not open a renaming pass over untouched code.

Do not describe code with words borrowed from building or construction. Say the plain thing: critical, not
load-bearing; the key part, not the cornerstone; a check, not a guardrail. The terms the field already uses literally,
build, architecture, and framework, are fine; this is about the decorative ones.

These stay as they are:

- Names an outside standard fixes, whether Java, an RFC, or PostgreSQL itself: the SQL function `ceiling()`,
  `IllegalArgumentException`, frontend/backend protocol message and field names, GUC and connection-property names.
- Published API, where a name is a compatibility promise. Rename only through deprecation.
- Text the driver reproduces verbatim: quotations, log lines, wire data.

## Error messages

Use the word the code uses. Wrap user-facing exception text in `GT.tr`, which always formats the string with
`java.text.MessageFormat`, so double every single quote: `GT.tr("Can''t connect to {0}", host)`.

English is the source. `./gradlew :postgresql:generateGettextSources` updates the files under `translation/`
from it. Refreshing the translations is a separate i18n change, so do not run the task for a change that only
adds or reworks an English message. Never edit `messages_*.java` by hand.

## Skill trigger: `telemetry-authoring`

Load `telemetry-authoring` before writing or changing a call to a logger, a metric, or a span, and before deciding what
a new failure, retry, fallback, clamped value, or waited-on state should emit. A coding task reaches this point the
moment the branch is written, not when the pull request is due: load it then, and read its `references/` file for the
repository's ecosystem before the first call (JVM, Go, and Python have one; for any other ecosystem the skill says what
to do without one). Also load it to review instrumentation in a diff, including instrumentation that is conspicuously
absent. Wording, tense, sentence length, and dialect of the message belong to the developer-style skill of the language
it is written in (`english-developer-style` for English); load that too.
```

## Project instructions of arm `new`

Arms `final2` to `final4` use the instructions of `final`.

```markdown
Contents of CLAUDE.md (project instructions, checked into the codebase):

# AGENTS.md

## Word choice in comments, documentation, and names

Use the right-hand column below in Javadoc, inline comments, error and log messages, `CHANGELOG.md`, `docs/`,
commit messages, and pull request descriptions.

| Instead of | Write | Note |
| --- | --- | --- |
| captured | recorded | Keep `capture` where something really is captured: traffic off a socket, a stack trace at the point of failure. |
| ceiling, cap | limit | As noun and as verb: limit a length, do not cap it. |
| desync, desynced | out of sync | |
| end-of-stream, end of the stream, EOF, end of file; the stream ends, has ended, is exhausted | end of stream | The state an `InputStream` reports by returning -1. |
| envelope | message | Name the part: the message, its header, or its body. |
| hard cap, soft cap | say what the limit does | Not `hard limit` or `soft limit` either. |
| legal | valid | |
| self-inclusive | say what the field counts | |
| upper bound on X | largest X | Keep `upper bound` where a lower bound is also in play, or the sentence is about a range. |

The list binds identifiers as well as prose: rename `fieldCap` to `fieldLimit` along with the comment beside it, and
`rejectsAFieldCountBeyondTheEnvelope` to `rejectsAFieldCountBeyondTheMessage`. This covers names you introduce and
names in code you are already changing. Do not open a renaming pass over untouched code.

Do not describe code with words borrowed from building or construction. Say the plain thing: critical, not
load-bearing; the key part, not the cornerstone; a check, not a guardrail. The terms the field already uses literally,
build, architecture, and framework, are fine; this is about the decorative ones.

These stay as they are:

- Names an outside standard fixes, whether Java, an RFC, or PostgreSQL itself: the SQL function `ceiling()`,
  `IllegalArgumentException`, frontend/backend protocol message and field names, GUC and connection-property names.
- Published API, where a name is a compatibility promise. Rename only through deprecation.
- Text the driver reproduces verbatim: quotations, log lines, wire data.

## Error messages

Use the word the code uses. Wrap user-facing exception text in `GT.tr`, which always formats the string with
`java.text.MessageFormat`, so double every single quote: `GT.tr("Can''t connect to {0}", host)`.

English is the source. `./gradlew :postgresql:generateGettextSources` updates the files under `translation/`
from it. Refreshing the translations is a separate i18n change, so do not run the task for a change that only
adds or reworks an English message. Never edit `messages_*.java` by hand.

## Skill trigger: `telemetry-authoring`

Load `telemetry-authoring` before writing or changing a call to a logger, a metric, or a span, and before deciding what
a new failure, retry, fallback, clamped value, or waited-on state should emit. A coding task reaches this point the
moment the branch is written, not when the pull request is due: load it then, and read its `references/` file for the
repository's ecosystem before the first call (JVM, Go, and Python have one; for any other ecosystem the skill says what
to do without one). Also load it to review instrumentation in a diff, including instrumentation that is conspicuously
absent. That includes the failure message of a build script, a CLI command, or a CI check (a Gradle or Maven task that
verifies something, a lint, a pre-commit hook): its reader holds only the tool's output, and the skill's tool mode
covers it. Wording, tense, sentence length, and dialect of the message belong to the developer-style skill of the language
it is written in (`english-developer-style` for English); load that too.
```

## Project instructions of arm `final`

Arms `final2` to `final4` use the instructions of `final`.

```markdown
Contents of CLAUDE.md (project instructions, checked into the codebase):

# AGENTS.md

## Word choice in comments, documentation, and names

Use the right-hand column below in Javadoc, inline comments, error and log messages, `CHANGELOG.md`, `docs/`,
commit messages, and pull request descriptions.

| Instead of | Write | Note |
| --- | --- | --- |
| captured | recorded | Keep `capture` where something really is captured: traffic off a socket, a stack trace at the point of failure. |
| ceiling, cap | limit | As noun and as verb: limit a length, do not cap it. |
| desync, desynced | out of sync | |
| end-of-stream, end of the stream, EOF, end of file; the stream ends, has ended, is exhausted | end of stream | The state an `InputStream` reports by returning -1. |
| envelope | message | Name the part: the message, its header, or its body. |
| hard cap, soft cap | say what the limit does | Not `hard limit` or `soft limit` either. |
| legal | valid | |
| self-inclusive | say what the field counts | |
| upper bound on X | largest X | Keep `upper bound` where a lower bound is also in play, or the sentence is about a range. |

The list binds identifiers as well as prose: rename `fieldCap` to `fieldLimit` along with the comment beside it, and
`rejectsAFieldCountBeyondTheEnvelope` to `rejectsAFieldCountBeyondTheMessage`. This covers names you introduce and
names in code you are already changing. Do not open a renaming pass over untouched code.

Do not describe code with words borrowed from building or construction. Say the plain thing: critical, not
load-bearing; the key part, not the cornerstone; a check, not a guardrail. The terms the field already uses literally,
build, architecture, and framework, are fine; this is about the decorative ones.

These stay as they are:

- Names an outside standard fixes, whether Java, an RFC, or PostgreSQL itself: the SQL function `ceiling()`,
  `IllegalArgumentException`, frontend/backend protocol message and field names, GUC and connection-property names.
- Published API, where a name is a compatibility promise. Rename only through deprecation.
- Text the driver reproduces verbatim: quotations, log lines, wire data.

## Error messages

Use the word the code uses. Wrap user-facing exception text in `GT.tr`, which always formats the string with
`java.text.MessageFormat`, so double every single quote: `GT.tr("Can''t connect to {0}", host)`.

English is the source. `./gradlew :postgresql:generateGettextSources` updates the files under `translation/`
from it. Refreshing the translations is a separate i18n change, so do not run the task for a change that only
adds or reworks an English message. Never edit `messages_*.java` by hand.

## Skill trigger: `telemetry-authoring`

Load `telemetry-authoring` before writing or changing a call to a logger, a metric, or a span, and before deciding what
a new failure, retry, fallback, clamped value, or waited-on state should emit. A coding task reaches this point the
moment the branch is written, not when the pull request is due: load it then, and read its `references/` file for the
repository's ecosystem before the first call (JVM, Go, and Python have one; for any other ecosystem the skill says what
to do without one). Also load it to review instrumentation in a diff, including instrumentation that is conspicuously
absent. Load it as well before writing the text of an exception, an error response, or a failed build, CLI command, or
CI check (a Gradle or Maven task that verifies something, a lint, a pre-commit hook): its reader holds only that text.
Wording, tense, sentence length, and dialect of the message belong to the developer-style skill of the language it is
written in (`english-developer-style` for English); load that too.
```

## The caller's-channel subsection of arm `final`

```markdown
's channel carries

An agent offered only a way to accept the result takes it, so the message also says when accepting is wrong. Beyond what
failed and the values involved, the message carries:

| Carries | Detection |
| --- | --- |
| **Why the check exists**, in one clause the reader can relay | The message says what failed but not what the check protects, so "why did it fail" needs the source |
| **Where to change it**: the setting, the parameter, or the file and the key, spelled the way the reader sets or greps it | A limit or an expected value printed with no name the reader can set; a key named without its file, or a file without its key |
| **How to find the cause**, where the code knows more than the reader: a command ready to run, or the fact itself, with every value the code holds filled in | A placeholder such as `<module>` or `<id>` where the code holds the value; "check your configuration" with no command or value |
| **Each way out, runnable as printed**: what to change when the condition is not intended, and, where the check can be overridden, the command or setting that accepts the result | Where an override exists, only it is offered; a command that does not run as printed, such as one that names a module or a directory where the tool expects a task or a subcommand; one remedy after a list whose cases need different ones |
| **What to report**, where the check exists so that a reviewer sees the change: what goes into the change description or to the user, with the names and numbers to quote | The message gives the accept path and does not say to tell the reviewer |

A library rejecting a setting, which has no override:

```text
Invalid value "30s" for retry.max-attempts in /etc/app/app.yaml: expected a whole number of attempts. The setting
bounds how many times a failed request is retried. Write a number such as 3, or set retry.timeout to bound the time
instead.
```

A build check that compares the release jars with a committed list, with one module added and the size over its limit:

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches
dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings it in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The total size of the jars is 88080384 bytes (84 MiB), which exceeds total-size-limit=87031808 (83 MiB) in
src/dist/src/dist/expected_release_artifacts.txt. The largest jars now:
  12582912 bcprov-jdk18on-1.78.jar
  ...
If the module is not intended, exclude it or revert the dependency update that brought it in. If the growth is not
intended, revert the update that grew the jars. If both are intended, run ./gradlew :src:dist:verifyReleaseDependencies
-PupdateExpectedJars, which also raises total-size-limit, commit the file, and name the module, the size growth, and the
dependency update in the pull request description.
```

The examples show what each row looks like, not text to reuse. Every fact in them is true of that check only; check
each phrase taken from them against the code the new message reports on.
```

## The caller's-channel subsection of arm `final2`

```markdown
's channel carries

An agent offered only a way to accept the result takes it, so the message also says when accepting is wrong. Beyond what
failed and the values involved, the message carries:

| Carries | Detection |
| --- | --- |
| **Why the check exists**, in one clause the reader can relay | The message says what failed but not what the check protects, so "why did it fail" needs the source |
| **Where to change it**: the setting, the parameter, or the file and the key, spelled the way the reader sets or greps it | A limit or an expected value printed with no name the reader can set; a key named without its file, or a file without its key |
| **How to find the cause**, where the code knows more than the reader: a command ready to run, or the fact itself, with every value the code holds filled in | A placeholder such as `<module>` or `<id>` where the code holds the value; "check your configuration" with no command or value |
| **Each way out, runnable as printed**: what to change when the condition is not intended; where a limit refused the operation, the change to the request that brings it under the limit, named for this operation, beside raising the limit; and, where the check can be overridden, the command or setting that accepts the result | Where an override exists, only it is offered; a limit whose only way out is raising or disabling it, where the request could change instead; a command that does not run as printed, such as one that names a module or a directory where the tool expects a task or a subcommand; one remedy after a list whose cases need different ones |
| **What to report**, where the check exists so that a reviewer sees the change: what goes into the change description or to the user, with the names and numbers to quote | The message gives the accept path and does not say to tell the reviewer |

A service refusing a request over a size limit:

```text
Request body of 12582912 bytes exceeds max-request-size=10485760 (10 MiB) in config/application.yaml. The limit keeps
one request from holding more than that much server memory. Upload the file in parts of at most 10 MiB with the
multipart endpoint, or raise max-request-size if requests this large are expected.
```

A build check that compares the release jars with a committed list, with one module added and the size over its limit:

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches
dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings it in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The total size of the jars is 88080384 bytes (84 MiB), which exceeds total-size-limit=87031808 (83 MiB) in
src/dist/src/dist/expected_release_artifacts.txt. The largest jars now:
  12582912 bcprov-jdk18on-1.78.jar
  ...
If the module is not intended, exclude it or revert the dependency update that brought it in. If the growth is not
intended, revert the update that grew the jars. If both are intended, run ./gradlew :src:dist:verifyReleaseDependencies
-PupdateExpectedJars, which also raises total-size-limit, commit the file, and name the module, the size growth, and the
dependency update in the pull request description.
```

The examples show what each row looks like, not text to reuse. Every fact in them is true of that check only; check
each phrase taken from them against the code the new message reports on.
```

## The caller's-channel subsection of arm `final3`

```markdown
's channel carries

An agent offered only a way to accept the result takes it, so the message also says when accepting is wrong. Beyond what
failed and the values involved, the message carries:

| Carries | Detection |
| --- | --- |
| **Why the check exists**, in one clause the reader can relay | The message says what failed but not what the check protects, so "why did it fail" needs the source |
| **Where to change it**: the setting, the parameter, or the file and the key, spelled the way the reader sets or greps it | A limit or an expected value printed with no name the reader can set; a key named without its file, or a file without its key |
| **How to find the cause**, where the code knows more than the reader: a command ready to run, or the fact itself, with every value the code holds filled in | A placeholder such as `<module>` or `<id>` where the code holds the value; "check your configuration" with no command or value |
| **Each way out, runnable as printed and working as the code stands**: what to change when the condition is not intended; where a limit refused the operation, the change to the request that brings it under the limit, named for this operation, beside raising the limit with a value it accepts; and, where the check can be overridden, the command or setting that accepts the result | Where an override exists, only it is offered; a limit whose only way out is raising or disabling it, where the request could change instead; a remedy the code does not show to work, such as a setting the failing path never reads; a command that does not run as printed, such as one that names a module or a directory where the tool expects a task or a subcommand; one remedy after a list whose cases need different ones |
| **What to report**, where the check exists so that a reviewer sees the change: what goes into the change description or to the user, with the names and numbers to quote | The message gives the accept path and does not say to tell the reviewer |

A service refusing a request over a size limit:

```text
Request body of 12582912 bytes exceeds max-request-size=10485760 (10 MiB) in config/application.yaml. The limit keeps
one request from holding more than that much server memory. Upload the file in parts of at most 10 MiB with the
multipart endpoint, or raise max-request-size, for example to 20MB, if requests this large are expected.
```

A build check that compares the release jars with a committed list, with one module added and the size over its limit:

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches
dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings it in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The total size of the jars is 88080384 bytes (84 MiB), which exceeds total-size-limit=87031808 (83 MiB) in
src/dist/src/dist/expected_release_artifacts.txt. The largest jars now:
  12582912 bcprov-jdk18on-1.78.jar
  ...
If the module is not intended, exclude it or revert the dependency update that brought it in. If the growth is not
intended, revert the update that grew the jars. If both are intended, run ./gradlew :src:dist:verifyReleaseDependencies
-PupdateExpectedJars, which also raises total-size-limit, commit the file, and name the module, the size growth, and the
dependency update in the pull request description.
```

The examples show what each row looks like, not text to reuse. Every fact in them is true of that check only; check
each phrase taken from them against the code the new message reports on.
```

## The caller's-channel subsection of arm `final4`

```markdown
's channel carries

An agent offered only a way to accept the result takes it, so the message also says when accepting is wrong. Beyond what
failed and the values involved, the message carries:

| Carries | Detection |
| --- | --- |
| **Why the check exists**, in one clause the reader can relay | The message says what failed but not what the check protects, so "why did it fail" needs the source |
| **Where to change it**: the setting, the parameter, or the file and the key, spelled the way the reader sets or greps it | A limit or an expected value printed with no name the reader can set; a key named without its file, or a file without its key |
| **How to find the cause**, where the code knows more than the reader: a command ready to run, or the fact itself, with every value the code holds filled in | A placeholder such as `<module>` or `<id>` where the code holds the value; "check your configuration" with no command or value |
| **Each way out, runnable as printed and working as the code stands**: what to change when the condition is not intended; where a limit refused the operation, the change to the request that brings it under the limit, named for this operation, beside raising the limit with a value it accepts; and, where the check can be overridden, the command or setting that accepts the result | Where an override exists, only it is offered; a limit whose only way out is raising or disabling it, where the request could change instead; a remedy the code does not show to work, such as a setting the failing path never reads, or an example value that would fail the same check, such as a raised limit no larger than the one exceeded; a command that does not run as printed, such as one that names a module or a directory where the tool expects a task or a subcommand; one remedy after a list whose cases need different ones |
| **What to report**, where the check exists so that a reviewer sees the change: what goes into the change description or to the user, with the names and numbers to quote | The message gives the accept path and does not say to tell the reviewer |

A service refusing a request over a size limit:

```text
Request body of 12582912 bytes exceeds max-request-size=10485760 (10 MiB) in config/application.yaml. The limit keeps
one request from holding more than that much server memory. Upload the file in parts of at most 10 MiB with the
multipart endpoint, or raise max-request-size, for example to 20MB, if requests this large are expected.
```

A build check that compares the release jars with a committed list, with one module added and the size over its limit:

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches
dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings it in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The total size of the jars is 88080384 bytes (84 MiB), which exceeds total-size-limit=87031808 (83 MiB) in
src/dist/src/dist/expected_release_artifacts.txt. The largest jars now:
  12582912 bcprov-jdk18on-1.78.jar
  ...
If the module is not intended, exclude it or revert the dependency update that brought it in. If the growth is not
intended, revert the update that grew the jars. If both are intended, run ./gradlew :src:dist:verifyReleaseDependencies
-PupdateExpectedJars, which also raises total-size-limit, commit the file, and name the module, the size growth, and the
dependency update in the pull request description.
```

The examples show what each row looks like, not text to reuse. Every fact in them is true of that check only; check
each phrase taken from them against the code the new message reports on.
```

## Fact ledger as first written

Its note on fetch-size advice was wrong; the judges of the first rounds applied it.

```markdown
# Fact ledger for the maxResultBuffer exception message

Built from what an application developer, or an agent, needs when holding only the exception, not from the skill text.

Scenario rendered for every variant: the connection property `maxResultBuffer` was set to `100M`, which the parser turns
into the limit 100000000 bytes (`maxResultBuffer` field). A DataRow of 8000 bytes (`value`) brought the running total
(`resultBufferByteCount`) to 100003200. The default locale is en_US. The driver calls `setBroken()` before the throw, so
the connection is closed and unusable afterwards.

| Id | The message lets the reader... |
| --- | --- |
| G1 | say what failed, with the received total and the limit as numbers the reader can compare with their own setting |
| G2 | say in one clause why the limit exists: it bounds the memory one result set may take |
| G3 | find where to change it: the connection property `maxResultBuffer`, by that name, as a connection or data-source property |
| G4 | know what values the property takes (bytes, a size such as `100M`, or a percent of the heap such as `10p`), or at least its unit |
| G5 | know that the connection is now closed and a new one is needed |
| G6 | act: raise `maxResultBuffer`, and an alternative that changes what the query returns (fewer rows or columns) |
| G7 | read numbers as the code prints them, without locale grouping such as `100,003,200` |
| G8 | trust every statement: no invented property, unit, default, or behavior; a placeholder MessageFormat leaves unsubstituted, or an apostrophe that swallows one, is a defect here |

Unverified claim: whether `setFetchSize` avoids the error. The running total is reset only after a simple-protocol query
(`QueryExecutorImpl` around the `clearResultBufferCount()` call), so advice that a fetch size makes the driver read the
result in batches that each start from zero is not established by this code. Judge such advice as unverified (`P` on
G8), not as invented (`N`).
```

## Fact ledger as corrected

The consolidated judge applied this one to all 36 messages.

```markdown
# Fact ledger for the maxResultBuffer exception message

Built from what an application developer, or an agent, needs when holding only the exception, not from the skill text.

Scenario rendered for every variant: the connection property `maxResultBuffer` was set to `100M`, which the parser turns
into the limit 100000000 bytes (`maxResultBuffer` field). A DataRow of 8000 bytes (`value`) brought the running total
(`resultBufferByteCount`) to 100003200. The default locale is en_US. The driver calls `setBroken()` before the throw, so
the connection is closed and unusable afterwards.

| Id | The message lets the reader... |
| --- | --- |
| G1 | say what failed, with the received total and the limit as numbers the reader can compare with their own setting |
| G2 | say in one clause why the limit exists: it bounds the memory one result set may take |
| G3 | find where to change it: the connection property `maxResultBuffer`, by that name, as a connection or data-source property |
| G4 | know what values the property takes (bytes, a size such as `100M`, or a percent of the heap such as `10p`), or at least its unit |
| G5 | know that the connection is now closed and a new one is needed |
| G6 | act: raise `maxResultBuffer`, and an alternative to raising it: fewer rows or columns, or a fetch size with autocommit off |
| G7 | read numbers as the code prints them, without locale grouping such as `100,003,200` |
| G8 | trust every statement: no invented property, unit, default, or behavior; a placeholder MessageFormat leaves unsubstituted, or an apostrophe that swallows one, is a defect here |

Fetch-size advice, checked against the driver: the running total resets at every ReadyForQuery in both protocols (the
Sync that ends each extended execute and each fetch queues an entry with `asSimple=true`, and that branch calls
`clearResultBufferCount()`). So `Statement.setFetchSize` with autocommit off makes each fetch start from zero, in the
default extended query mode. With autocommit on, or with `preferQueryMode=simple`, the driver reads the whole result and
the advice does nothing. Score fetch-size advice that states autocommit off as correct; advice that omits that condition
is partial (`P` on G8). A raised example value no larger than the limit (100000000 bytes; `100M` equals it) is wrong
advice (`P` on G8).
```

## Render prompt

```markdown
# Render exception messages

Each file `blind/<CODE>.diff` under `{EXP}` is a change to the pgjdbc sources against `{EXP}/base`. Every change replaces
the bare `GT.tr("Result set exceeded maxResultBuffer")` in `PGStream.increaseByteCounter` with code that builds a
message (and may also touch translations or tests). Render, for each code you are given, the exact `getMessage()` text of
the `PSQLException` in the scenario below, and write it to `{EXP}/blind/<CODE>.txt` with the Write tool. Do not judge or
improve it.

Scenario: `maxResultBuffer` (the long field) = 100000000; `resultBufferByteCount` after the addition = 100003200; the
argument `value` = 8000; the default locale is en_US; no other locale is active, so `GT.tr` returns the English text
formatted by `java.text.MessageFormat`.

Apply MessageFormat exactly: `{n}` substitutes argument n; a `Long` or `Integer` argument is formatted with the en_US
NumberFormat, which groups digits (`100,000,000`), while a `String` argument is inserted as is; `{n,number,#}` prints
digits without grouping; a single `'` starts a quoted literal that runs to the next `'`, inside which `{n}` is printed
literally and not substituted, and `''` prints one apostrophe. `PSQLException.getMessage()` returns the message as built
(ignore any `ServerErrorMessage`). If the code does not compile or cannot reach the throw, write that in one line
instead.

Write each file as plain text, exactly as built. Then read each file back and compare it with its code. Reply with one
line per code: the code and `ok` or the problem.
```

## Reader prompt

```markdown
The user's Java application, which uses the PostgreSQL JDBC driver, failed with the exception below while running a report query. You cannot see the driver's source or the application's code, and you cannot run anything; work from this text alone.

Reply to the user in at most 150 words:

1. What failed, and why the driver has this check.
2. What state the database connection is in now.
3. What exactly the user should change, with names and values they can type.
4. Any alternative if raising a limit is not wanted.

Where the text does not tell you something, say so instead of guessing.

```text
org.postgresql.util.PSQLException: {OUTPUT}
```
```

## Judge prompt

```markdown
# Judge exception messages and the replies of agents that read them

You judge {N} variants of one exception message, named by code only. For each code `X` under `{EXP}/blind/`:

- `X.diff` is the change that builds the message, against the pgjdbc sources in `{EXP}/base`;
- `X.txt` is the message rendered for one scenario, described at the top of `{EXP}/ledger.md`;
- `{EXP}/reader/X.md` is the reply of a fresh agent that saw only `X.txt` as the exception an application failed with
  and was asked to explain it to the user (its prompt is `{EXP}/reader_prompt.md`).

Read `{EXP}/ledger.md` first, then the facts you can check in the base sources: `PGProperty.MAX_RESULT_BUFFER`,
`org.postgresql.util.PGPropertyMaxResultBufferParser` (accepted forms, the 90% heap clamp),
`docs/content/documentation/use.md` (the `maxResultBuffer` entry), and `PGStream.increaseByteCounter` with its
`setBroken()` call.

Score every code on every ledger row G1 to G8 as `Y`, `P` (partial), or `N`, judging the rendered text. G8 is `Y` when
nothing in the message is invented or wrong; follow the ledger's note on fetch-size advice.

Then score the reader's reply:

- R1: it explains correctly what failed and why the limit exists (`Y`/`P`/`N`);
- R2: it says correctly what state the connection is in, or says the text does not tell (`Y` when correct, `P` when
  it says the text does not tell, `N` when it claims the connection is still usable);
- R3: it gives a correct change the user can type: the property name and a value form the driver accepts (`Y`/`P`/`N`);
- R4: it invents nothing: no property, unit, default, or behavior absent from the text and false (`Y` when clean, `N`
  with the invention quoted).

Write `{EXP}/judge.md` with the Write tool: one Markdown table, a row per code, columns `code`, G1 to G8, R1 to R4, and
a short note quoting the decisive text for any `P` or `N`. Under the table, list the three best and the three worst
codes with one sentence each. Do not try to guess which model or version wrote a variant. Do not edit any other file.
Reply with the table only.
```
