# Case: review pgjdbc/pgjdbc#4251 at 71d1f287, a new SASL mechanism with protocol, secret-handling, and test gaps

A review-finding case for `adversarial-code-review`. The input is [pgjdbc/pgjdbc#4251][pr] at `71d1f287`, four commits
on top of `15df70ef`. The gold answer comes from the reviewer's inline comments on that commit, the second round of
review: 24 comments, of which the author replied in the thread or changed the code near 17, and this case keeps 16 of
those 17. The review was written in 2026, and reviews from 2025 on may be agent-assisted. Findings from the first round
are not given to the model; an earlier finding that is still unfixed at `71d1f287` and is reported again is not counted
against the run.

The change adds OAUTHBEARER (RFC 7628) authentication. `ConnectionFactoryImpl.doAuthentication` now reads the SASL
mechanism list itself in `readMechanisms`, picks OAuth when the server offers it and `oauthToken` or
`oauthTokenProviderClassName` is set, and otherwise falls through to SCRAM. `OAuthAuthenticator` sends the token, and on
`AuthenticationSASLContinue` logs the server's error and sends the dummy response. New connection properties
(`oauthToken`, `oauthIssuer`, `oauthClientSecret`, `oauthAllowInsecureIssuer`, `oauthAllowUnencryptedConnection`, and
others) get `BaseDataSource` setters, and the change adds a Keycloak container, CI matrix rows, a test token provider in
`testkit`, and integration and unit tests. The diff adds 1751 lines and removes 70, so the checks span the protocol
state machine, secret handling, CI and local test scripts, and the tests.

The pull request was rebased between rounds; `base` is the parent of the first commit of this round, and `base..head`
lists the four commits only. The prompt names neither the pull request nor its issue.

[pr]: https://github.com/pgjdbc/pgjdbc/pull/4251

## What it exercises

- Area *Security, privacy, and supply chain*: a server that rejects the token and then sends `AuthenticationOk`, a
  bearer token sent to a TLS peer that was never verified, and secrets copied into a URL the driver logs.
- Area *Correctness and data integrity*: an unreachable branch whose comment describes a path that would hang, a parser
  that ignores the message length, an issuer check that one of two paths skips, and two failure causes sharing one
  message.
- Area *Compatibility and evolution*, the **Contracts** bullet: a new public class in an exported package.
- Area *Verification and documentation*: a mechanism decision table with no test, tests that assert message text or a
  shared SQLState, a regression test that the refactoring made pass for the wrong reason, missing boundary inputs, and a
  test setup (`authMode`, `OAUTH`) that cannot be reproduced outside CI.

## Checks

Grade by reading `result.md`; the grep only finds the candidates. A finding passes as `blocking` or `non-blocking`; a
defect named only in a question under *Needed to complete the review* is partial. Line numbers are at `71d1f287`, and
`ConnectionFactoryImpl.java` means `pgjdbc/src/main/java/org/postgresql/core/v3/ConnectionFactoryImpl.java`.

1. **`AuthenticationOk` after a rejected token is accepted.** Pass: a finding that after the OAuth branch of
   `AUTH_REQ_SASL_CONTINUE` (`ConnectionFactoryImpl.java` lines 1176-1180) logs the server's error and sends the dummy
   response, no state records that the server rejected the token, so a following `AuthenticationOk` (`AUTH_REQ_OK`,
   lines 1206-1218) completes the connection; after the error the client must fail on any further authentication message
   (RFC 4422 section 3.6, libpq's "server sent additional OAuth data after error"). Partial: the report says the error
   sequence handling is loose or untested without naming the accepted `AuthenticationOk`. Fail: neither.
   `grep -niE 'AuthenticationOk|AUTH_REQ_OK|after (the )?(error|rejection)|SASL_CONTINUE|SASLContinue' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4251#discussion_r3970363209))
2. **The mechanism decision table has no test.** Pass: a finding that the choice between OAuth, SCRAM, and the error
   (lines 1085-1172) has no unit test, for example `requireAuth=!oauth` against a server that offers both mechanisms,
   which by the code falls through to SCRAM; the misleading pair `oauthOffered` (offered and configured) and
   `scramOffered` (offered only) may be named alongside. Partial: the report names only the variable names. Fail:
   neither.
   `grep -niE 'oauthOffered|scramOffered|decision|mechanism selection|requireAuth' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4251#discussion_r3970363222))
3. **The null-token branch is unreachable and would hang.** Pass: a finding that `isOAuthConfigured(info)` guards the
   OAuth branch, so `resolveOAuthToken` returns a non-empty token or throws and the `oauthToken != null` tests at lines
   1109-1126 never see `null`; and that if `null` did arrive, nothing would be sent and
   `setFinishedAuthenticationRequests` skipped, so the loop would wait for a server that is waiting for the client,
   which contradicts the comment at lines 1102-1106 that the code "already has support" for discovery. Naming either
   half passes. Partial: the report calls the comment stale without naming the unreachable `null` or the hang. Fail:
   neither.
   `grep -niE 'resolveOAuthToken|null token|unreachable|discovery|hang|isOAuthConfigured' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4251#discussion_r3970363230))
4. **`readMechanisms` ignores the message length.** Pass: a finding that `readMechanisms` (lines 1250-1266) reads
   strings until it meets a second NUL instead of reading the body length the caller has in `msgLen`, so a malformed or
   empty `AuthenticationSASL` makes it read into the next message, the `mechanisms.isEmpty()` check can never fire
   because the `do/while` adds before it tests, or the loop has no bound on the number of mechanisms; or that
   `assert c == 0` at line 1257 is the only check of the terminator and is skipped without `-ea`. Partial: the report
   says the parser trusts the server without naming the length, the bound, the dead check, or the `assert`. Fail:
   neither.
   `grep -niE 'readMechanisms|msgLen|assert c|isEmpty|terminator|unbounded|mechanism list' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4251#discussion_r3970363241))
5. **The issuer check skips static tokens, against the docs.** Pass: a finding that `validateOAuthIssuer` is called only
   in the provider branch of `resolveOAuthToken` (line 377), so a connection that sets `oauthToken` with an `http://`
   `oauthIssuer` connects without an error, while the `oauthAllowInsecureIssuer` entry in
   `docs/content/documentation/use.md` (lines 557-559) says a non-HTTPS issuer "is rejected with an error at connection
   time". Partial: the report notes the check runs only for providers without the contradiction with the docs, or the
   reverse. Fail: neither.
   `grep -niE 'validateOAuthIssuer|oauthIssuer|insecure ?issuer|HTTPS|static token' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4251#discussion_r3970363249))
6. **A malformed issuer gets the HTTPS message.** Pass: a finding that `validateOAuthIssuer` (lines 346-355) turns a
   `URISyntaxException` into `isHttps = false`, so a URL that does not parse is reported as "OAuth issuer URL must use
   HTTPS" with the remedy `oauthAllowInsecureIssuer=true`, which does not fix it. Partial: the report says the message
   is misleading without naming the malformed-URL path. Fail: neither.
   `grep -niE 'URISyntaxException|malformed|must use HTTPS|isHttps' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4251#discussion_r3970363257))
7. **Encrypted is not authenticated.** Pass: a finding that `checkTransportEncryption` in `OAuthAuthenticator.java`
   (line 55) accepts any `SSLSocket`, so under `sslmode=require` or `prefer`, which do not verify the server
   certificate, a rogue endpoint with a self-signed certificate passes the check and receives the bearer token; RFC 7628
   asks for TLS to keep the token from third parties. A note that the `prefer` fallback reconnects without TLS and, with
   `oauthAllowUnencryptedConnection=true`, sends the token again may be named alongside. Partial: the report says the
   TLS requirement is weak without naming the missing certificate verification. Fail: neither.
   `grep -niE 'SSLSocket|verify-(ca|full)|VERIFY_CA|certificate|sslmode|unverified|self-signed' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4251#discussion_r3970363266))
8. **`OAuthAuthenticator` is public for a test.** Pass: a finding that `OAuthAuthenticator` (line 30) is
   `public final class` in `org.postgresql.core.v3` while `ScramAuthenticator` is package-private, apparently because
   `OAuthAuthenticatorTest` sits in `org.postgresql.test.core.v3`, which adds a type to the published API; moving the
   test lets the class become package-private. Partial: the report says the class is wider than needed without the
   reason or the remedy. Fail: neither.
   `grep -niE 'OAuthAuthenticator.*public|public (final )?class|package-private|OAuthAuthenticatorTest' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4251#discussion_r3970363287))
9. **Secrets reach `getUrl()` and the logs.** Pass: a finding that `BaseDataSource.getUrl()` (line 1461) adds every
   `PGProperty` present in `properties` to the query string, so `oauthToken` and `oauthClientSecret`, which their
   setters store there, appear in the URL that `getConnection` logs at `FINE` (lines 99-107) and that `Driver.connect`
   logs again ("Connecting with URL"), whereas `password` is kept in its own field and stays out. Partial: the report
   says the token is kept as a `String` or may leak, without naming `getUrl()` or a log line. Fail: neither.
   `grep -niE 'getUrl|Connecting with URL|oauthToken|oauthClientSecret|log(ged|s)? .*(token|secret)|redact' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4251#discussion_r3970363298))
10. **`authMode` does not reach the test JVM.** Pass: a finding that
    `build-logic/jvm/src/main/kotlin/build-logic.test-base.gradle.kts` (lines 50-55) adds `enable_oauth_tests` to the
    properties passed to the test JVM but not `authMode`, which `TestUtil` reads (`testkit`, line 317) and `matrix.mjs`
    sets for `oauth=all`, so `-DauthMode=oauth` on a local Gradle run is ignored; CI works only because it passes the
    flags through `_JAVA_OPTIONS`. Partial: the report says the OAuth test modes are hard to run locally without naming
    `authMode`. Fail: neither.
    `grep -niE 'authMode|passProperty|enable_oauth_tests|test-base' result.md`
    ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4251#discussion_r3970363331))
11. **`OAUTH=yes` is a value CI never uses.** Pass: a finding that `docker/bin/postgres-server` (line 62) starts the
    Keycloak profile only for `OAUTH=yes`, while `matrix.mjs` uses `no`, `smoke`, and `all` and `entrypoint.sh` tests
    `!= "no"` and `= "all"`, so `OAUTH=smoke` or `OAUTH=all` installs the validator and writes the `oauth` rule into
    `pg_hba.conf` but starts no Keycloak (and on arm64 skips `PG_PLATFORM`). Partial: the report says the script header
    and the matrix disagree on values without the effect. Fail: neither.
    `grep -niE 'OAUTH=|postgres-server|COMPOSE_PROFILES|smoke|keycloak' result.md`
    ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4251#discussion_r3970363340))
12. **`invalidToken` asserts the server's message text.** Pass: a finding that `OAuthTest.invalidToken`
    (`pgjdbc/src/test/java/org/postgresql/test/jdbc4/OAuthTest.java`, lines 137-151) compares the exception message with
    the server's English text, which depends on `lc_messages` and the server version, where SQLState `28000` is stable;
    or that it does not show that `handleAuthenticationSASLContinue` ran, since the server's `ErrorResponse` arrives
    either way. Partial: the report calls the test brittle without naming either point. Fail: neither.
    `grep -niE 'invalidToken|lc_messages|28000|server message|SASLContinue' result.md`
    ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4251#discussion_r3970363353))
13. **Translated messages and a shared SQLState in the OAuth tests.** Pass: a finding that
    `channelBindingIncompatibleWithOAuth` (`OAuthTest.java` lines 198-200), or `OAuthAuthenticatorTest` at line 115,
    asserts a `GT.tr` message, which the runs on the `locale` axis of `matrix.mjs` will translate once the strings reach
    a `.po` file, against the rule stated at line 178 of the same file; or that `requireAuthForbidsOAuth` (lines
    168-180) checks only `CONNECTION_REJECTED`, which the transport check and the "none of them configured or supported"
    error also return, so it stays green with the `AuthMethod.isAllowed` check removed. Partial: the report says some
    tests assert message text without naming a test. Fail: neither.
    `grep -niE 'channelBindingIncompatible|requireAuthForbidsOAuth|GT\.tr|locali[sz]|translat' result.md`
    ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4251#discussion_r3970363361))
14. **The test token provider teaches the wrong contract.** Pass: a finding about
    `testkit/src/main/java/org/postgresql/test/OAuthTestTokenProvider.java` that names at least one of these: line 58
    sends `request.getClientSecret()` as the resource owner's `password`, while `realm.json` declares `pgjdbc-test` a
    public client with no secret; the message `oauthToken system property not set` (line 48) describes an empty
    `access_token`; `readResponse` (lines 101-106) reads only `getInputStream()`, so a Keycloak error body is lost on a
    4xx. Partial: the report flags the provider as test-only code with weak error handling without naming any of the
    three. Fail: neither.
    `grep -niE 'OAuthTestTokenProvider|getClientSecret|client secret|password|getErrorStream|access_token' result.md`
    ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4251#discussion_r3970363369))
15. **The channel-binding regression test now passes for another reason.** Pass: a finding that moving the `-PLUS` check
    into `ScramAuthenticator.initializeScramClient` (line 56), ahead of `getChannelBindingData`, lets
    `requireRejectsConnectionWithoutSsl` (`ScramAuthenticatorChannelBindingTest.java` line 65), which asserts only
    `CONNECTION_REJECTED`, stay green if `SCRAM-SHA-256-PLUS` is dropped from `MECHANISMS` (line 37), so it no longer
    guards the check it was written for. Partial: the report notes the new `MECHANISMS` argument without the weakened
    test. Fail: neither.
    `grep -niE 'ChannelBindingTest|requireRejectsConnectionWithoutSsl|-PLUS|MECHANISMS' result.md`
    ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4251#discussion_r3970363386))
16. **Token format boundaries are untested.** Pass: a finding that `BuildTokenMessageTest.invalidToken`
    (`pgjdbc/src/test/java/org/postgresql/core/v3/BuildTokenMessageTest.java`, lines 41-56) misses the edges of
    `TOKEN_REGEX` (`[A-Za-z0-9._~+/-]+=*`), such as `=` alone, `abc=def`, `abc==`, or a non-ASCII token, the last of
    which matters because `buildTokenMessage` narrows each `char` to a byte (`OAuthAuthenticator.java` line 141) and is
    safe only because the regex runs first. Naming the non-ASCII case, or two of the others, passes. Partial: the report
    asks for more invalid-token cases without naming one. Fail: neither.
    `grep -niE 'BuildTokenMessageTest|TOKEN_REGEX|non-ASCII|\(byte\)|padding|boundary' result.md`
    ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4251#discussion_r3970363394))

Check 4 was also raised in round 1, as a hard limit on the number of mechanisms
([comment](https://github.com/pgjdbc/pgjdbc/pull/4251#discussion_r3577858307)) and as the `assert` on the terminator
([comment](https://github.com/pgjdbc/pgjdbc/pull/4251#discussion_r3577863939)); `readMechanisms` is unchanged since.

## Skill parts

- `adversarial-code-review`: `SKILL.md` §Review areas, area *Security, privacy, and supply chain*
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Correctness and data integrity*, invalid inputs and state
  transitions
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Compatibility and evolution*, the **Contracts** bullet
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Verification and documentation*, tests that would catch an
  incorrect implementation and commands whose outcome depends on a configuration the change creates

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `15df70efac3cd70419e42f4e75307c6bfe5a9f06` (the parent of the first commit of the rebased pull request), and `71d1f287c7dd94e75038246fe3a8e47c8c61ead6` (the commit the second round reviewed). |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<head>` replaced by `run-review-case.sh`. |

## How to run

From the repository root, once per model and run:

```bash
research/adversarial-code-review/cases/run-review-case.sh research/adversarial-code-review/cases/pgjdbc-4251-r2-oauth-bearer-auth <model> <label> <rev>
```
