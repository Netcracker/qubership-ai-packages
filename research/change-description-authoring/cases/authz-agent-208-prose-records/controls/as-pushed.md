## Commit

```text
feat(token): give keys that cannot be loaded a reason code of their own

A token that found no key got TOKEN_KID_UNKNOWN whether its source held no such key or could not be asked, so an outage of Keycloak read like a stream of invented tokens.

LookupOrReload now returns ErrKeysUnavailable when no loaded key matches and the last load got no answer about the keys of the source: the load failed, the wait for it ran out, or a limit refused it. Verify turns that into TOKEN_KEYS_UNAVAILABLE. A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys, because that is what a token with an invented realm gets. A realm that holds keys existed when it loaded them, so its 404 is a failed reload and the keys stay. A provider that answers 404 is not an answer either: the configuration names it, so the 404 says nothing about its keys. A 200 whose keys member is not an array, null included, is a failed load too, so such a body no longer removes the keys.

A load writes the flag after the keys and the lookup reads it before the keys, so a load that ends between the two cannot refuse a key it brought.

User-visible:
A JWKS with "keys": null keeps the keys of the source and counts as a failed load, where it used to remove them.
A token that no loaded key matches while the last load of its source failed, the wait for a reload ran out, or a limit refused the load is refused with TOKEN_KEYS_UNAVAILABLE: the keys of iss "<iss>" cannot be loaded, so the token cannot be checked

Not changed:
A token that names a realm that does not exist keeps TOKEN_KID_UNKNOWN.

Assisted-by: Claude Code (claude-opus-5-5)
```

## Title

feat(token): give keys that cannot be loaded a reason code of their own

## Description

````markdown
## Why

A token that finds no key gets `TOKEN_KID_UNKNOWN`, whether its source holds no such key or could not be asked. An outage of Keycloak therefore reads like a stream of invented tokens. ADR-0091 and ADR-0095 in #160 give that case a code of its own.

## What

- `LookupOrReload` returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source: the load failed, the wait for it ran out, or a limit refused it. `Verify` turns that into `TOKEN_KEYS_UNAVAILABLE`.
- A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys, because that is what a token with an invented realm gets. A realm that holds keys existed when it loaded them, so its 404 is a failed reload and the keys stay. A provider that answers 404 is not an answer either: the configuration names it, so the 404 says nothing about its keys.
- A 200 whose `keys` is not an array, `null` included, is a failed load. `null` used to count as an empty array and removed the keys, which ADR-0091 R28 and R39 rule out.
- A load writes the state of the source after the keys, and the lookup reads it before the keys, so a load that ends between the two cannot refuse a key it brought.

## User-visible changes

The packages are not wired into the service, so this reaches only code that calls them.

- A token that no loaded key matches while the last load of its source failed, the wait for a reload ran out, or a limit refused the load is refused with `TOKEN_KEYS_UNAVAILABLE`: `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
- A JWKS with `"keys": null` keeps the keys of the source and counts as a failed load.

Not changed: a token that names a realm that does not exist keeps `TOKEN_KID_UNKNOWN`.

## Verification

`go test ./...` and `go test -race -shuffle=on ./internal/token/...` pass, and golangci-lint is clean.

New tests cover each kind of answer of a reload, a key that stays usable during an outage and the load that ends it, the first load of a realm that fails or outlasts the wait, and a key that a `Refresh` brings during the wait. `TestLookupOrReload_TakesA404AsAnAnswerOnlyForARealmWithNoKeys` tells a realm that holds keys from one that does not, `TestLookupOrReload_TakesA404AsAnAnswerForARealmThatLostItsKeys` covers a realm whose JWKS emptied before the 404, and `TestLookupOrReload_TakesA404OfAProviderWithNoKeysAsNoAnswer` covers a provider that never loaded a key. `TestVerify_TellsAnOutageOfKeycloakFromARealmThatDoesNotExist` runs the two codes through a real `Set`.

Seven tests changed their expectation from `ErrKeyUnknown` to `ErrKeysUnavailable`, because the limit or the wait they exercise is the case this change names: `StartsAtMostTenLoadsAMinute`, `ACeilingOfLoadsCoversTheReloadOfAKnownRealm`, `KeepsNoMoreRealmsThanTheLimit`, `ANewRealmTakesThePlaceOfARealmThatFailedAMinuteAgo`, `StopsWaitingWhenItsContextEnds`, `StopsWaitingAfterTheReloadWait`, and `WaitsThreeSecondsForAReloadByDefault`, all of `TestLookupOrReload_`. In `internal/token/verify` the fake `KeyFinder` follows the same contract, and the row "context that has ended" expects the new code. The row `JWKS whose keys is null` of `TestRefresh_AJWKSWithoutAUsableKeyRemovesTheProvidersKeys` now keeps the key, because the rule for `null` moved.

Hand mutants of these lines fail the tests. They include each way of treating a load as answered, a 404 of a provider or of a realm with keys taken as an answer, each limit that keeps the old error, and `Verify` without the new branch.

## Scope

- This pull request is stacked on #203, which sits on #159, #202, and #201, and merges after them.
- The packages are not wired into the service yet, so no request is handled differently.
- ADR-0095 lists two more new codes, `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`. Both depend on the route or the mode, so the wiring change adds them.

## Rules

```text
Implements: ADR-0091 R23, R37, R38, R39.
Defers: ADR-0092 R2, ADR-0095 R2, and ADR-0095 R16 to the wiring change.
```
````
