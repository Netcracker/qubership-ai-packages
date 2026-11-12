# Case: review pgjdbc/pgjdbc#3964 at 1d9b3a8f, keep-alive options that break connects where the JDK lacks them

A review-finding case for `adversarial-code-review`. The input is [pgjdbc/pgjdbc#3964][pr] at `1d9b3a8f`, 17 commits on
top of `29bbe026`, five of them merges from the main branch. The gold answer comes from the reviewer's inline comments
on that commit, the third round of review: 17 comments, of which the author replied in the thread or changed the code
near seven, and this case keeps all seven. The review was written in 2026, and reviews from 2025 on may be
agent-assisted. Findings from the two earlier rounds are not given to the model; an earlier finding that is still
unfixed at `1d9b3a8f` and is reported again is not counted against the run.

The change adds the connection properties `tcpKeepAliveCount`, `tcpKeepAliveIdle`, and `tcpKeepAliveInterval`. A new
`ExtendedSocketOptionAccessorImpl` exists in two variants: the Java 8 one in `src/main/java` throws
`UnsupportedOperationException` from every setter, and the Java 11 one in `src/main/java11` looks up the fields of
`jdk.net.ExtendedSocketOptions` by reflection and calls `Socket.setOption`. `ConnectionFactoryImpl.tryConnect` applies
each property that is set, and the `PGStream` copy constructor, which the SSL and GSS fallbacks use, copies the three
options to the new socket. The diff adds 473 lines and removes 1.

`Socket.setOption` and `Socket.getOption` throw `UnsupportedOperationException` for an option that the socket's
`supportedOptions()` does not list, and the JDK declares the three fields on every platform. The Java 11 variant treats
a field it found as an option the socket supports, and that error reaches users who set none of the new properties.

The pull request merged the main branch into itself between rounds; `base` is the main-branch commit it last merged, so
`base..head` lists only its own commits. The prompt names neither the pull request nor its issue.

[pr]: https://github.com/pgjdbc/pgjdbc/pull/3964

## What it exercises

- Area *Compatibility and evolution*: a platform or `socketFactory` without the options (Windows before JDK 22, a custom
  `SocketImpl`) and a Java 8 runtime; connections that set none of the new properties must keep working.
- Area *Reliability, operability, and observability* and the error model: unchecked exceptions that escape the connect
  path as SQLState `99999`, an `IOException` that marks a host dead, a getter that hides a malformed value.
- Area *Architecture and maintainability*: a public interface that no caller uses as a type.
- Area *Verification and documentation*: tests whose assertions are skipped where the code is most likely to fail, and
  an oracle that reads the value back through the code under test.

## Checks

Grade by reading `result.md`; the grep only finds the candidates. A finding passes as `blocking` or `non-blocking`; a
defect named only in a question under *Needed to complete the review* is partial. Line numbers are at `1d9b3a8f`.

1. **A declared field is not a supported option.** Pass: a finding that `SocketOptionReference.isSupported()` in
   `src/main/java11/org/postgresql/core/ExtendedSocketOptionAccessorImpl.java` (lines 146-148) returns
   `socketOption != null`, which only says that `jdk.net.ExtendedSocketOptions` declares the field, while
   `Socket.setOption` and `getOption` throw `UnsupportedOperationException` for an option missing from
   `socket.supportedOptions()` (for example Windows before JDK 22, or a socket from a custom `socketFactory`), so the
   check has to take the socket. Partial: the report says the options may be unsupported on some platforms or that
   `UnsupportedOperationException` may escape, without naming the field-versus-`supportedOptions()` gap. Fail: neither.
   `grep -niE 'supportedOptions|isSupported|UnsupportedOperationException|Windows|SocketImpl' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/3964#discussion_r3972654676))
2. **The reflective lookup catches too little.** Pass: a finding that `createIntegerSocketOption` (lines 90-102) catches
   only `NoSuchFieldException`, `ClassNotFoundException`, and `IllegalAccessException`, so a `SecurityException`, a
   `LinkageError`, or an `ExceptionInInitializerError` from the class's static initializer, which runs at
   `Field.get(null)` because `ClassUtils.forName` loads without initializing, escapes into the connect path; or that
   `ClassUtils.forName` with `Object.class` as the expected type defeats its subtype check and is the wrong helper for a
   JDK class. Partial: the report questions the reflection or the helper choice without naming an uncaught throwable or
   the `Object.class` argument. Fail: neither.
   `grep -niE 'ClassUtils|forName|ExceptionInInitializerError|LinkageError|SecurityException|catch' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/3964#discussion_r3972654709))
3. **The `PGStream` copy constructor reads the options unconditionally.** Pass: a finding that the copy constructor in
   `PGStream.java` reads the three options at lines 159-161 for every connection, and the `catch` at line 164 handles
   only `SocketException`, so an `UnsupportedOperationException` from `getOption` fails the SSL fallback (`sslmode` when
   the server refuses SSL) and the `gssEncMode=prefer` fallback for users who set none of the new properties; or that
   `getOption` returns the system default when nothing was configured, so the setters always pin the OS defaults onto
   the new socket. Partial: the report says the copy constructor should copy the options only when they were set,
   without naming the escaping exception or the fallback paths. Fail: neither.
   `grep -niE 'PGStream|copy constructor|fallback|SocketException|getTcpKeep' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/3964#discussion_r3972654715))
4. **The options apply without `tcpKeepAlive`, and their errors take the wrong path.** Pass: a finding about the block
   in `ConnectionFactoryImpl.tryConnect` (lines 234-250) that names at least one of these: the three options are set
   whatever `tcpKeepAlive` says, though its default is `false` and the options then do nothing (libpq applies them only
   when keep-alives are on); on Java 8 the setter's bare `UnsupportedOperationException` is not caught by
   `openConnectionImpl` and reaches the user as the generic "Something unusual has occurred" error, SQLState `99999`; an
   out-of-range value makes `setOption` throw a `SocketException`, an `IOException`, so the driver reports a network
   failure and marks the host dead in `GlobalHostStatusTracker` instead of rejecting the property. Partial: the report
   says the values are not validated or the errors are unclear without naming any of the three. Fail: neither.
   `grep -niE 'tcpKeepAlive|99999|unusual|GlobalHostStatusTracker|host.*dead|out-of-range|negative|libpq' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/3964#discussion_r3972654722))
5. **A public interface that nothing uses as a type.** Pass: a finding that `ExtendedSocketOptionAccessor`
   (`src/main/java/org/postgresql/core/ExtendedSocketOptionAccessor.java`, line 19) is a public interface in an exported
   package, while every caller goes through `ExtendedSocketOptionAccessorImpl.INSTANCE`, so it should become the
   declared type or be removed; its missing method documentation, or the `throws IOException` that the Java 8 variant
   omits, may be named alongside. Partial: the report names only the missing documentation. Fail: neither.
   `grep -niE 'ExtendedSocketOptionAccessor\b|interface|INSTANCE|public API|exported' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/3964#discussion_r3972654749))
6. **The `DataSource` getters hide a malformed value.** Pass: a finding that `BaseDataSource.getTcpKeepAliveCount`,
   `getTcpKeepAliveIdle`, and `getTcpKeepAliveInterval` (lines 913, 934, and 955) catch `PSQLException` and return
   `null`, so a value that is not a number reads back as unset while the connection still fails, unlike the other
   integer getters of the class, which let the parse error out. Naming one of the three getters passes. Partial: the
   report flags the `catch` as swallowing an exception without saying what a caller then sees. Fail: neither.
   `grep -niE 'BaseDataSource|getTcpKeepAlive|swallow|PSQLException|return(s)? null' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/3964#discussion_r3972654755))
7. **The tests cannot fail where it matters.** Pass: a finding about `pGStreamSettings` or `socketSettings` in
   `ConnectionTest.java` (lines 538 and 577) that names at least one of these: every new assertion sits inside
   `if (...isTcpKeepCountSupported())` and its siblings, so on Java 8, where the no-op accessor returns `false`, all of
   them are skipped and the tests still pass instead of reporting a skip; the expected values are read back through the
   same `ExtendedSocketOptionAccessorImpl` that wrote them, so a mix-up between `TCP_KEEPCOUNT` and `TCP_KEEPIDLE` would
   not be caught. Missing cases (Java 8 refusal, `tcpKeepAlive=false`, invalid values) may be named alongside. Partial:
   the report asks only for more test cases. Fail: neither.
   `grep -niE 'ConnectionTest|pGStreamSettings|socketSettings|assume|skipped|same accessor|read back' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/3964#discussion_r3972654787))

## Skill parts

- `adversarial-code-review`: `SKILL.md` §Review areas, area *Compatibility and evolution*, the **Contracts** and
  **Baseline** bullets
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Correctness and data integrity*, invalid and
  partial-failure paths
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Reliability, operability, and observability*
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Architecture and maintainability*, explicit type
  boundaries
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Verification and documentation*, tests that would catch an
  incorrect implementation

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `29bbe0268c1e55cc2037fa171d61dcdafca39a7a` (the main-branch commit the pull request last merged, so that `base..head` lists only its own commits), and `1d9b3a8f38533a1e9b82ce59939d9c6728a8079a` (the commit the third round reviewed). |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<head>` replaced by `run-review-case.sh`. |

## How to run

From the repository root, once per model and run:

```bash
research/adversarial-code-review/cases/run-review-case.sh research/adversarial-code-review/cases/pgjdbc-3964-r3-tcp-keepalive-options <model> <label> <rev>
```
