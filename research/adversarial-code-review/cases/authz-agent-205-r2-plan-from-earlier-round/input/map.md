# Code map

Added lines per directory.

| Directory | Code | Tests | Docs | Data | Config | Generated or lock |
| --- | --- | --- | --- | --- | --- | --- |
| `internal/regogen` | 13787 | 12594 | 0 | 5770 | 0 | 0 |
| `internal/regogen/spectables` | 1397 | 1038 | 0 | 274 | 0 | 0 |
| `components/authz-policy-admin` | 1334 | 1848 | 64 | 0 | 0 | 0 |
| `internal/policyir` | 1212 | 1143 | 0 | 0 | 0 | 0 |
| `components/authz-agent/internal/snapshot` | 1197 | 3747 | 0 | 0 | 0 | 0 |
| `internal/regobuiltins` | 550 | 666 | 0 | 0 | 0 | 0 |
| `components/authz-agent/internal/server` | 493 | 1351 | 0 | 0 | 0 | 0 |
| `components/authz-agent/cmd/snapshot-corpus` | 477 | 46 | 0 | 0 | 0 | 0 |
| `components/authz-agent` | 430 | 828 | 178 | 0 | 0 | 0 |
| `components/authz-agent/cmd/filter-corpus` | 303 | 0 | 0 | 0 | 0 | 0 |
| `components/authz-agent/internal/legacy` | 207 | 126 | 0 | 0 | 0 | 0 |
| `internal/costcheck` | 202 | 109 | 0 | 0 | 0 | 0 |
| `internal/legacyvalue` | 178 | 140 | 0 | 0 | 0 | 0 |
| `internal/jsonvalue` | 139 | 101 | 0 | 0 | 0 | 0 |
| `internal/jsonpath` | 136 | 190 | 0 | 0 | 0 | 0 |
| `tools/ruleguard` | 133 | 33 | 0 | 0 | 0 | 0 |
| `components/authz-agent/internal/pull` | 125 | 306 | 0 | 0 | 0 | 0 |
| `components/authz-agent/internal/panics` | 80 | 89 | 0 | 0 | 0 | 0 |
| `components/authz-agent/internal/corpus` | 60 | 62 | 0 | 0 | 0 | 0 |
| `components/authz-agent/internal/m2m` | 44 | 153 | 0 | 0 | 0 | 0 |
| `internal/badrequest` | 40 | 0 | 0 | 0 | 0 | 0 |
| `policies` | 31 | 255 | 19 | 0 | 0 | 0 |
| `.` | 23 | 0 | 14 | 0 | 16 | 19 |
| `components/authz-agent/internal/engine` | 5 | 7 | 0 | 0 | 0 | 0 |
| `internal/token/keys` | 1 | 0 | 0 | 0 | 0 | 0 |
| `.github/linters` | 0 | 0 | 0 | 0 | 23 | 0 |
| `.github/workflows` | 0 | 0 | 0 | 0 | 28 | 0 |
| `api` | 0 | 0 | 0 | 0 | 170 | 0 |
| `docs/decisions` | 0 | 0 | 228 | 0 | 0 | 0 |
| `docs/plans` | 0 | 0 | 5 | 0 | 0 | 0 |
| `helm-templates/authz-agent` | 0 | 0 | 0 | 22 | 20 | 0 |
| `helm-templates/authz-agent/templates` | 0 | 0 | 0 | 0 | 14 | 0 |
| `helm-templates/authz-policy-admin` | 0 | 0 | 0 | 21 | 7 | 0 |
| `helm-templates/authz-policy-admin/templates` | 0 | 0 | 0 | 0 | 4 | 0 |
| `internal/regogen/testdata` | 0 | 0 | 221 | 0 | 0 | 0 |
| `test` | 0 | 0 | 33 | 1 | 0 | 0 |
| `test/integration/pipstub` | 0 | 50 | 0 | 0 | 0 | 0 |
| `test/integration/testify` | 0 | 145 | 0 | 0 | 0 | 0 |
| `test/integration/testify/testdata` | 0 | 0 | 0 | 0 | 0 | 0 |
| `test/k8s` | 0 | 0 | 0 | 0 | 3 | 0 |
| `test/k8s/parity` | 0 | 0 | 0 | 0 | 3 | 0 |
| `test/parity/suite` | 0 | 15 | 0 | 0 | 0 | 0 |
| `test/parity/suite/testdata/fixtures/policies/suite` | 0 | 0 | 0 | 4 | 0 | 0 |
| `test/scripts` | 0 | 46 | 0 | 0 | 0 | 0 |
| `test/scripts/token-testkit` | 0 | 0 | 0 | 0 | 0 | 0 |
| `test/svt` | 0 | 0 | 6 | 0 | 0 | 0 |
| `test/svt/common/scripts/lib` | 0 | 4 | 0 | 0 | 0 | 0 |
| `test/svt/profiler` | 0 | 0 | 10 | 0 | 0 | 0 |
| `test/svt/scripts` | 0 | 16 | 0 | 0 | 0 | 0 |
| `tools/ruleguard/testdata` | 0 | 3 | 0 | 0 | 0 | 0 |
| `tools/ruleguard/testdata/internal/jsonpath` | 0 | 8 | 0 | 0 | 0 | 0 |
| `tools/ruleguard/testdata/internal/regogen` | 0 | 98 | 0 | 0 | 0 | 0 |
| total | 22584 | 25217 | 778 | 6092 | 288 | 19 |

## Makefile (+23)

Added: 7-12, 15-16, 18, 20, 22, 24, 26, 62-70, 368


## components/authz-agent/cmd/filter-corpus/main.go (+303)

Added: 1-303

- struct `bundle` lines 54-60
- struct `answer` lines 62-65
- struct `request` lines 67-77
- struct `quiet` lines 79-82: used in components/authz-agent/internal/snapshot/registry_test.go; 16 calls sb did not attribute
- struct `replay` lines 87-110: 1 calls sb did not attribute
- struct `record` lines 113-125
- function `main` lines 127-237: 2 calls sb did not attribute
- function `verdict` lines 239-252
- function `sameJSON` lines 254-260
- function `toRequest` lines 265-276
- function `knownPaths` lines 280-303

## components/authz-agent/cmd/snapshot-corpus/main.go (+477)

Added: 1-477

- struct `bundle` lines 63-69
- struct `request` lines 71-81
- struct `quiet` lines 83-86: used in components/authz-agent/internal/snapshot/registry_test.go; 16 calls sb did not attribute
- struct `nullPIP` lines 90-95: 2 calls sb did not attribute
- struct `replay` lines 100-127: 2 calls sb did not attribute
- field `replayEntitlements` lines 131-131
- function `newRegistry` lines 133-137
- function `toRequest` lines 141-147
- function `resources` lines 150-159
- function `comparable` lines 163-171
- struct `outcome` lines 173-181
- function `run` lines 183-247: 4 calls sb did not attribute
- function `pct` lines 249-257
- function `q` lines 259-261
- function `bulk` lines 265-295
- function `underLoad` lines 299-342
- function `liveHeap` lines 345-355
- function `main` lines 357-477: 2 calls sb did not attribute

## components/authz-agent/config.go (+146)

Added: 18-22, 30, 49-58, 61-62, 65-83, 85-90, 93-94, 98-102, 105-107, 109-112, 115-139, 141-150, 152-166, 169-178, 181-190, 193, 196-200, 206, 209-220

- struct `config` lines 36-59
- delegate `lookup` lines 63-63
- function `envName` lines 67-69: used in components/authz-agent/main.go
- function `loadConfig` lines 75-113: used in components/authz-agent/{config_test.go, main.go, settings_drift_test.go}
- struct `settings` lines 117-220: 9 calls sb did not attribute
- field `maxSeconds` lines 170-170

## components/authz-agent/internal/corpus/subject.go (+60)

Added: 1-60

- function `Subject` lines 38-60: used in components/authz-agent/cmd/filter-corpus/main.go; components/authz-agent/cmd/snapshot-corpus/main.go; components/authz-agent/internal/corpus/subject_test.go

## components/authz-agent/internal/engine/engine.go (+5)

Added: 15-19

- struct `Options` lines 36-39
- struct `Engine` lines 43-146: used in components/authz-agent/internal/engine/engine_test.go; components/authz-agent/internal/server/{decide.go, public_test.go, server_test.go}; components/authz-agent/internal/snapshot/{decide.go, filter.go}; internal/regobuiltins/httpsend_test.go; internal/regogen/{bulk_test.go, entitlements_test.go, filtersub_test.go, gen_test.go, metamorphic_test.go} and 3 more; 7 calls sb did not attribute
- function `New` lines 55-79: used in components/authz-agent/internal/server/public_test.go; 158 calls sb did not attribute
- function `Query` lines 83-92: used in components/authz-agent/internal/engine/engine_test.go; components/authz-agent/internal/server/specconform_test.go; components/authz-agent/internal/snapshot/registry.go; components/authz-policy-admin/handlers.go; internal/regobuiltins/httpsend_test.go; internal/regogen/{bulk_test.go, entitlements_test.go, gen_test.go, metamorphic_test.go, pipcall_test.go, placement_test.go, scaling_test.go} and 1 more
- function `clone` lines 150-156: 2 calls sb did not attribute

## components/authz-agent/internal/legacy/legacy.go (+207)

Added: 22, 34-36, 38-41, 48-62, 65-70, 74-88, 131-136, 167, 187-189, 200-201, 203-208, 235-236, 238-239, 251, 253-255, 270-275, 280-281, 283-284, 289-291, 293, 297, 301-307, 309-332, 336-340, 342, 344, 347, 350-358, 360, 381-386, 388-390, 392-393, 395, 434-437, 440, 445-450, 456, 458-502, 505-507, 509

- delegate `RequestError` lines 41-41
- field `errBadRequest` lines 44-44
- field `errDuplicateID` lines 45-45
- function `errEmpty` lines 50-52
- function `required` lines 57-63
- struct `Resource` lines 71-83
- struct `RawResource` lines 87-89
- struct `Entry` lines 94-97
- struct `checkItem` lines 101-287
- struct `operationsItem` lines 109-114
- struct `v2Body` lines 118-121
- struct `v2Entry` lines 124-128
- function `CheckResource` lines 137-150: used in components/authz-agent/cmd/snapshot-corpus/main.go; components/authz-agent/internal/legacy/legacy_test.go
- function `CheckResourceBulk` lines 156-181: used in components/authz-agent/internal/server/public.go
- function `CheckResourceBulkOperations` lines 190-220: used in components/authz-agent/internal/legacy/legacy_test.go
- function `CheckResourceBulkOperationsV2` lines 227-267: used in components/authz-agent/internal/legacy/legacy_test.go
- function `CheckFilter` lines 274-276: used in components/authz-agent/cmd/filter-corpus/main.go; components/authz-agent/internal/server/public.go
- function `newResource` lines 292-310
- function `scalar` lines 315-324: 1 calls sb did not attribute
- function `structure` lines 327-333
- function `expand` lines 341-365
- function `array` lines 369-379
- function `operations` lines 384-396
- function `text` lines 401-413: 8 calls sb did not attribute
- function `uniqueIDs` lines 418-431
- field `skipHeaders` lines 438-443
- function `RequestHeaders` lines 449-459: used in components/authz-agent/internal/snapshot/subject.go
- function `Header` lines 464-471: used in components/authz-agent/internal/snapshot/subject.go; components/authz-policy-admin/{handlers.go, store_test.go}; test/integration/pipstub/{main.go, main_test.go}
- function `IncomingToken` lines 475-477: used in components/authz-agent/internal/snapshot/subject.go
- function `SubjectToken` lines 482-490: used in components/authz-agent/internal/snapshot/subject.go
- function `Input` lines 499-511: used in components/authz-agent/internal/server/decide.go
- function `AuthError` lines 518-533: used in components/authz-agent/internal/server/decide.go
- function `CheckResourceResponse` lines 538-544
- function `CheckResourceBulkResponse` lines 549-557
- function `CheckResourceBulkOperationsResponse` lines 564-581
- function `object` lines 583-586
- function `results` lines 588-591
- function `first` lines 593-598
- function `allowed` lines 600-602
- function `number` lines 606-620
- function `mustJSON` lines 624-632

## components/authz-agent/internal/m2m/m2m.go (+44)

Added: 16-20, 77-83, 89, 93-98, 104, 124, 129-134, 137-143, 214, 224, 235, 255-257, 265-267, 269

- field `DefaultClientIDFile` lines 42-42
- field `DefaultClientSecretFile` lines 43-43
- field `DefaultTokenFile` lines 47-47
- field `DefaultRenewBefore` lines 48-48
- field `DefaultWatchInterval` lines 49-49
- field `initialBackoff` lines 51-51
- field `maxBackoff` lines 52-52
- struct `Config` lines 61-69
- interface `Logger` lines 72-75: 18 calls sb did not attribute
- field `ErrNoToken` lines 79-79
- field `ErrTokenExpired` lines 80-80
- struct `Source` lines 85-272: used in components/authz-agent/internal/m2m/m2m_test.go; 495 calls sb did not attribute
- function `New` lines 104-127: 143 calls sb did not attribute
- function `renewal` lines 190-199: 1 calls sb did not attribute
- function `fetchToken` lines 277-322: used in components/authz-agent/internal/m2m/m2m_test.go
- function `jwtExpiry` lines 326-345
- function `readFile` lines 347-353: 1 calls sb did not attribute

## components/authz-agent/internal/panics/panics.go (+80)

Added: 1-80

- struct `Recovered` lines 27-44: used in components/authz-agent/cmd/filter-corpus/main.go; components/authz-agent/cmd/snapshot-corpus/main.go; components/authz-agent/main_test.go; 106 calls sb did not attribute
- function `Catch` lines 50-55
- function `site` lines 61-80

## components/authz-agent/internal/pull/pull.go (+125)

Added: 15-19, 37-39, 53-63, 66-73, 77-78, 80, 91-97, 99-103, 106, 112-113, 120-126, 131, 139-143, 156, 183, 186, 190-205, 212-214, 217-247, 252, 260-261, 266-267, 278-281, 291-294, 306

- field `DefaultInterval` lines 35-35
- field `DefaultHTTPTimeout` lines 36-36
- field `defaultTokenWait` lines 39-39
- struct `Config` lines 45-56
- interface `SnapshotLoader` lines 62-64: 1 calls sb did not attribute
- interface `PartialLoad` lines 71-74: 2 calls sb did not attribute
- interface `Tokens` lines 79-82: 9 calls sb did not attribute
- interface `Logger` lines 85-89: 18 calls sb did not attribute
- struct `Status` lines 98-104: 34 calls sb did not attribute
- struct `Puller` lines 107-352: used in components/authz-agent/internal/pull/pull_test.go; components/authz-agent/main_test.go; 519 calls sb did not attribute
- function `New` lines 131-145: 150 calls sb did not attribute
- struct `partialState` lines 191-194

## components/authz-agent/internal/server/decide.go (+310)

Added: 1-310

- field `tenantHeader` lines 35-35
- struct `refusal` lines 167-170
- field `callerTenantMismatch` lines 175-175
- field `defaultTenantNotTranslated` lines 178-178
- field `retryAfterSeconds` lines 182-182
- function `hasTenantClaim` lines 198-201
- function `callerMayReach` lines 208-223
- function `m2mToken` lines 228-240
- function `subject` lines 289-291
- function `legacyResult` lines 296-310
- method `decide` lines 43-79: 2 calls sb did not attribute
- method `filter` lines 85-109: 2 calls sb did not attribute
- method `failed` lines 116-122
- method `admit` lines 137-163
- method `reject` lines 186-193
- method `defaultTenant` lines 243-248
- method `log` lines 252-254
- method `admission` lines 258-268
- method `tenant` lines 277-285

## components/authz-agent/internal/server/public.go (+71)

Added: 18, 27-28, 38, 83-106, 111-140, 149, 160, 181, 188, 203-210, 212

- struct `PublicHealthResponse` lines 86-89
- struct `TenantCounts` lines 92-102
- function `countTenants` lines 124-141
- function `lastQuery` lines 193-201: used in components/authz-agent/internal/server/decide.go
- function `sendJSON` lines 215-218: used in components/authz-agent/internal/server/decide.go
- method `RegisterPublic` lines 37-52: used in components/authz-agent/internal/server/{public_test.go, server_test.go}; components/authz-agent/main.go
- method `requestID` lines 59-76
- method `notFound` lines 78-81
- method `publicHealth` lines 107-121
- method `checkResource` lines 143-153
- method `checkResourceBulk` lines 155-163
- method `checkResourceBulkOperations` lines 166-185
- method `checkFilter` lines 187-189
- method `refuse` lines 206-213: 1 calls sb did not attribute

## components/authz-agent/internal/server/server.go (+112)

Added: 22, 25, 28, 32-33, 73-84, 91-95, 98-103, 111-116, 137-147, 152-153, 167-170, 173-179, 186, 192-195, 204, 206-217, 229-232, 242-273

- field `LegacyAPIVersion` lines 38-38
- interface `Logger` lines 47-50: 8 calls sb did not attribute
- struct `discardLogger` lines 53-60: 8 calls sb did not attribute
- struct `Options` lines 63-85
- struct `Server` lines 88-272: used in components/authz-agent/internal/server/public.go; components/authz-agent/main.go
- field `panicsName` lines 102-102
- function `Register` lines 107-122: used in components/authz-agent/internal/server/{public_test.go, server_test.go}; components/authz-agent/main.go
- struct `Report` lines 127-148
- struct `HealthResponse` lines 151-154
- struct `HealthErrorResponse` lines 157-160
- struct `HealthErrorDetails` lines 166-171
- function `unavailable` lines 224-235
- function `apiVersion` lines 237-240
- function `opaError` lines 275-277: used in components/authz-agent/internal/server/decide.go

## components/authz-agent/internal/snapshot/decide.go (+201)

Added: 1-201

- struct `Request` lines 35-38
- struct `Result` lines 41-44
- field `ReasonNoTenant` lines 50-50
- field `ReasonDenied` lines 52-52
- field `ReasonUnknown` lines 56-56
- function `unknownReason` lines 181-201
- method `Decide` lines 66-150: used in components/authz-agent/cmd/filter-corpus/main.go; components/authz-agent/cmd/snapshot-corpus/main.go; components/authz-agent/internal/server/decide.go; components/authz-agent/internal/snapshot/{deep_test.go, registry_test.go}
- method `evalItem` lines 155-173

## components/authz-agent/internal/snapshot/filter.go (+74)

Added: 1-74

- struct `FilterRequest` lines 28-32
- method `Filter` lines 41-74: 8 calls sb did not attribute

## components/authz-agent/internal/snapshot/health.go (+125)

Added: 1-125

- struct `Health` lines 26-34: used in components/authz-agent/cmd/snapshot-corpus/main.go; components/authz-agent/internal/server/{public.go, server.go}; components/authz-agent/internal/snapshot/registry_test.go; components/authz-agent/main.go
- struct `TenantHealth` lines 39-60
- struct `Failure` lines 63-83: 106 calls sb did not attribute
- struct `Rejection` lines 89-94
- struct `Form` lines 97-101
- function `failuresOf` lines 119-125: used in components/authz-agent/internal/snapshot/registry.go
- method `Health` lines 104-117: used in components/authz-agent/cmd/snapshot-corpus/main.go; components/authz-agent/internal/server/{public.go, server.go}; components/authz-agent/internal/snapshot/registry_test.go; components/authz-agent/main.go

## components/authz-agent/internal/snapshot/metrics.go (+57)

Added: 1-57

- field `tenantsDesc` lines 24-28
- struct `Collector` lines 31-57: used in components/authz-policy-admin/store.go; internal/regogen/{gen_test.go, leaf.go}
- function `NewCollector` lines 36-36: used in components/authz-agent/internal/snapshot/metrics_test.go; components/authz-agent/main.go

## components/authz-agent/internal/snapshot/registry.go (+585)

Added: 1-585

- interface `Logger` lines 50-53: 16 calls sb did not attribute
- struct `Config` lines 56-72
- struct `Snapshot` lines 75-88: used in components/authz-agent/cmd/snapshot-corpus/main.go; components/authz-agent/internal/snapshot/{decide.go, filter.go, registry_test.go}
- struct `queries` lines 91-94
- struct `state` lines 98-113
- struct `Registry` lines 117-564: used in components/authz-agent/cmd/snapshot-corpus/main.go; components/authz-agent/internal/snapshot/{decide.go, filter.go, registry_test.go}; 44 calls sb did not attribute
- function `New` lines 135-149: 138 calls sb did not attribute
- struct `LoadSummary` lines 162-174
- struct `TenantRefusal` lines 177-184
- struct `RefusedError` lines 188-223: 77 calls sb did not attribute
- function `refusalsOf` lines 361-369
- function `keepsWhat` lines 371-376
- struct `build` lines 379-388: 5 calls sb did not attribute
- struct `refusal` lines 393-396
- function `exportFailure` lines 401-407
- function `prepareQuery` lines 505-508
- function `now` lines 510-510: used in components/authz-agent/internal/m2m/m2m.go
- function `newElements` lines 568-585

## components/authz-agent/internal/snapshot/subject.go (+155)

Added: 1-155

- struct `Subject` lines 32-48: used in components/authz-agent/internal/snapshot/{decide.go, filter.go}
- function `NewSubject` lines 57-65: used in components/authz-agent/internal/corpus/subject.go; components/authz-agent/internal/server/decide.go; components/authz-agent/internal/snapshot/subject_test.go
- function `NewRequest` lines 70-80: used in components/authz-agent/cmd/snapshot-corpus/{main.go, main_test.go}; components/authz-agent/internal/server/{decide.go, public_test.go, server_test.go}; components/authz-policy-admin/store_test.go; test/integration/pipstub/main_test.go; 17 calls sb did not attribute
- function `NewFilterRequest` lines 84-90: used in components/authz-agent/cmd/filter-corpus/main.go; components/authz-agent/internal/server/decide.go
- function `claimsOf` lines 94-108: 5 calls sb did not attribute
- function `body` lines 112-122: 4 calls sb did not attribute
- function `decode` lines 124-129: 3 calls sb did not attribute
- method `prepare` lines 135-155: 2 calls sb did not attribute

## components/authz-agent/main.go (+45)

Added: 24, 41, 48-50, 66-70, 94, 97, 100-105, 107-115, 117-122, 150, 159, 246, 254-258, 267-270

- field `logger` lines 54-54
- function `init` lines 56-63
- function `main` lines 65-166: 2 calls sb did not attribute
- function `serve` lines 176-194: 5 calls sb did not attribute
- struct `surface` lines 198-202
- function `serveUntilShutdown` lines 208-239
- function `get` lines 245-250: 50 calls sb did not attribute
- function `report` lines 257-272: used in components/authz-agent/internal/pull/pull.go; components/authz-agent/main_test.go

## components/authz-agent/tenant.go (+239)

Added: 1-239

- field `tenantLookupPath` lines 35-35
- field `tenantID` lines 38-38
- struct `defaultTenant` lines 45-239: used in components/authz-agent/{main.go, tenant_test.go}; 587 calls sb did not attribute
- interface `tenantLog` lines 55-59: 16 calls sb did not attribute
- function `newDefaultTenant` lines 61-66: used in components/authz-agent/{main.go, main_test.go, tenant_test.go}
- struct `lookupError` lines 144-150: 75 calls sb did not attribute
- function `lookupState` lines 158-196
- function `retryPause` lines 200-202: used in components/authz-agent/tenant_test.go
- function `redacted` lines 205-211

## components/authz-policy-admin/condition.go (+305)

Added: 1-305

- function `conditionRefusal` lines 33-55: used in components/authz-policy-admin/validate.go
- function `conditionTextRefusal` lines 65-117
- function `splitTokenRefusal` lines 123-134
- field `quotedPattern` lines 137-137
- field `splitOperatorPatterns` lines 138-149
- field `splitListPattern` lines 150-150
- field `singleSubjectKinds` lines 156-156
- field `multiSubjectKinds` lines 157-157
- field `eqLeftKinds` lines 158-158
- field `singleKinds` lines 159-161
- field `multiKinds` lines 162-162
- field `arithKinds` lines 163-163
- field `listKinds` lines 164-164
- function `concat` lines 167-167
- function `operandKindRefusal` lines 171-207
- function `operandKind` lines 211-247: 1 calls sb did not attribute
- function `describeKind` lines 249-261
- function `booleanListRefusal` lines 265-276
- function `operandRefusal` lines 283-305

## components/authz-policy-admin/convert.go (+104)

Added: 18, 21, 24-25, 30-34, 36-65, 68-69, 71-90, 127, 161-179, 192, 197-199, 213-214, 224, 228, 244, 269-272, 274, 278, 280, 282, 307, 312-316

- struct `simplifiedPolicy` lines 35-66
- struct `simplifiedPIP` lines 70-112
- struct `v3PolicySetsResponse` lines 116-120
- struct `v3PolicySet` lines 122-133
- struct `v3Policy` lines 135-140
- struct `v3Rule` lines 142-152
- struct `v3PIPsResponse` lines 154-158
- struct `v3PIP` lines 160-187
- function `toV3PolicySets` lines 196-287: used in components/authz-policy-admin/{convert_test.go, handlers.go}
- function `toV3PIPs` lines 290-324: used in components/authz-policy-admin/{convert_test.go, handlers.go}
- function `rolesTarget` lines 337-351: 1 calls sb did not attribute
- function `rolesKey` lines 354-361
- function `conditionString` lines 365-380

## components/authz-policy-admin/handlers.go (+74)

Added: 22, 38-43, 73, 77, 81, 89-102, 104-107, 111, 115, 127, 131, 135, 143-153, 155-158, 162-163, 242-265

- field `maxBodyBytes` lines 27-27
- struct `server` lines 36-264: used in components/authz-agent/main.go; components/authz-policy-admin/{main.go, store_test.go, totality_test.go}
- function `handleNotFound` lines 217-219
- function `methodNotAllowed` lines 221-226
- function `pathDomain` lines 233-240
- function `readBody` lines 266-273
- function `writeJSON` lines 275-279
- function `timestamp` lines 281-283

## components/authz-policy-admin/main.go (+21)

Added: 63, 95-97, 110-125, 142

- interface `logSink` lines 71-77: 1245 calls sb did not attribute
- field `logger` lines 80-80
- function `init` lines 82-88
- function `main` lines 90-107: 2 calls sb did not attribute
- function `build` lines 116-144: 5 calls sb did not attribute
- function `envOr` lines 146-151
- function `logStop` lines 157-162

## components/authz-policy-admin/store.go (+174)

Added: 21, 23-24, 28, 46-49, 67-87, 100, 113-116, 126-128, 134, 136-139, 165, 176-177, 179, 190-191, 204-206, 210-213, 215, 217, 222, 226-227, 231-234, 236, 238, 243, 247-260, 297-330, 333, 336, 339, 364-365, 370-374, 381-382, 399-401, 403-404, 425-439, 457, 462-473, 482-487, 490-496, 565

- field `unreadableFile` lines 44-44
- field `shadowedFile` lines 48-48
- field `policiesFilePrefix` lines 51-51
- field `pipsFilePrefix` lines 52-52
- field `stateFileName` lines 53-53
- field `tempFilePattern` lines 54-54
- field `domainPattern` lines 61-61
- function `validDomain` lines 63-65: used in components/authz-policy-admin/{handlers.go, main.go}
- field `defaultTenant` lines 69-69
- function `scopeKey` lines 75-77
- struct `persistedState` lines 92-98
- struct `store` lines 111-405: used in components/authz-policy-admin/{handlers.go, main.go}; 32 calls sb did not attribute
- function `newStore` lines 134-159: used in components/authz-policy-admin/{main.go, store_test.go, totality_test.go}
- function `keyDomain` lines 323-325
- function `hashItems` lines 415-423
- function `withPolicyScope` lines 425-431
- function `withPIPTenant` lines 433-438
- function `normalizePolicies` lines 442-447
- function `normalizePIPs` lines 449-454
- struct `domainFile` lines 456-460
- function `globDomainFiles` lines 473-499
- function `sortedKeys` lines 501-508: 2 calls sb did not attribute
- function `sortedKeysOfPolicies` lines 510-517
- function `sortedKeysOfPIPs` lines 519-526
- function `readIfPresent` lines 528-537
- function `probeWritable` lines 542-550
- function `sweepTempFiles` lines 552-562
- function `writeFileAtomic` lines 566-594

## components/authz-policy-admin/validate.go (+656)

Added: 1-656

- struct `refusal` lines 40-43
- function `badRequest` lines 45-47
- function `conflict` lines 49-51
- function `decodeUpload` lines 56-69: used in components/authz-policy-admin/handlers.go
- function `coerceTexts` lines 76-93: used in components/authz-policy-admin/handlers.go
- field `pipTexts` lines 98-100
- field `policyTexts` lines 101-103
- delegate `fieldKind` lines 107-107
- field `text` lines 111-111
- field `flag` lines 115-115
- field `integer` lines 118-118
- field `object` lines 119-119
- field `list` lines 120-120
- field `pipFieldKinds` lines 124-129
- field `predicatesFieldKinds` lines 132-132
- field `policyFieldKinds` lines 133-136
- function `fieldRefusal` lines 142-189
- field `longPattern` lines 191-191
- field `pipTypes` lines 198-198
- field `returnTypes` lines 199-199
- field `pipNamePattern` lines 206-206
- field `reservedHeaders` lines 210-210
- field `subjectRefPattern` lines 214-214
- field `requestAttributeBuiltins` lines 218-218
- field `mappingKeyBuiltins` lines 223-223
- function `validatePIPs` lines 229-245: used in components/authz-policy-admin/handlers.go
- function `trimPIPEnums` lines 251-266: used in components/authz-policy-admin/handlers.go
- function `cloneItem` lines 268-274
- function `pipType` lines 277-282
- function `headerRefusal` lines 286-294
- function `declaredKinds` lines 299-310
- function `pipRefusal` lines 314-418
- function `requestAttributeRefusal` lines 424-445
- function `mappingRefusal` lines 450-473
- function `mappingKeyKind` lines 477-495
- function `otherDomainOf` lines 499-511
- field `uuidPattern` lines 516-516
- function `validatePolicies` lines 522-535: used in components/authz-policy-admin/handlers.go
- function `policyRefusal` lines 539-578
- function `javaTrim` lines 583-585: used in components/authz-policy-admin/condition.go
- function `javaBlank` lines 591-601
- function `unicodeBlank` lines 605-607
- function `javaSplit` lines 611-617
- function `jsonText` lines 622-635: used in components/authz-policy-admin/{condition.go, convert.go}
- function `falsy` lines 639-656

## internal/badrequest/badrequest.go (+40)

Added: 1-40

- struct `Error` lines 28-40: used in components/authz-agent/cmd/filter-corpus/main.go; components/authz-agent/cmd/snapshot-corpus/main.go; components/authz-agent/internal/server/{decide.go, public.go}; internal/regogen/project.go; 154 calls sb did not attribute

## internal/costcheck/subprocess.go (+202)

Added: 1-202

- field `childEnv` lines 36-36
- field `childDone` lines 41-41
- field `MaxStack` lines 46-46
- field `childTimeout` lines 49-49
- struct `Run` lines 52-59
- function `InSubprocess` lines 74-103: used in internal/costcheck/subprocess_test.go
- function `runPattern` lines 107-113: used in internal/costcheck/subprocess_test.go
- struct `Known` lines 117-124
- function `Deep` lines 133-142
- function `verdict` lines 146-161
- field `excerptFrames` lines 164-164
- function `Excerpt` lines 173-202: used in internal/costcheck/subprocess_test.go

## internal/jsonpath/filter.go (+32)

Added: 19, 75, 78-87, 92-94, 245-250, 358-360, 365-369, 405, 410, 414

- delegate `predicate` lines 32-32
- field `listOpRE` lines 35-35
- field `quotedRE` lines 36-36
- field `sizeRE` lines 37-37
- field `regexOpRE` lines 38-38
- field `compareRE` lines 39-39
- field `nestedRE` lines 40-40
- field `existsRE` lines 41-41
- struct `missing` lines 45-45
- function `member` lines 49-59: used in internal/jsonpath/jsonpath.go; internal/legacyvalue/structuretext.go
- function `parseFilter` lines 67-141: used in internal/jsonpath/jsonpath.go
- function `nestedFilter` lines 148-158
- struct `literal` lines 161-172
- function `stringLiteral` lines 175-179
- function `listItem` lines 185-191
- function `equal` lines 199-222
- function `compareFilter` lines 229-273
- function `javaCompare` lines 278-301
- function `order` lines 304-314
- function `listFilter` lines 323-354
- function `sizeFilter` lines 361-395
- function `regexFilter` lines 402-427
- function `regexInput` lines 431-444
- field `javaSpace` lines 450-450
- field `javaVertical` lines 451-451
- field `javaDot` lines 452-452
- function `javaPattern` lines 468-537: used in internal/jsonpath/jsonpath_test.go
- function `onlyCloseParens` lines 541-543
- function `quantifierEnd` lines 547-566
- function `groupStart` lines 570-585
- function `escape` lines 591-636
- function `hexEscape` lines 639-657
- function `charClass` lines 661-709
- function `classAtom` lines 716-738
- function `isASCIILetter` lines 740-742
- function `swapCase` lines 744-749

## internal/jsonpath/jsonpath.go (+104)

Added: 51-55, 90, 98-110, 154-156, 208-214, 216-227, 234, 236-247, 254-255, 260-262, 266-269, 271-272, 275, 308, 331-333, 335-337, 344, 349-375, 382-384

- field `ErrUnsupported` lines 96-96
- field `errJaywayRefuses` lines 100-100
- field `errGoRegex` lines 105-105
- field `errBeyondInt` lines 109-109
- delegate `Kind` lines 112-112
- field `KindOne` lines 117-117
- field `KindMany` lines 120-120
- field `KindMissing` lines 122-122
- field `KindNullParent` lines 126-126
- field `KindIndexOutOfBounds` lines 128-128
- field `KindBracket` lines 131-131
- field `KindTooLarge` lines 141-141
- struct `Result` lines 146-149
- struct `Path` lines 152-536: used in internal/jsonpath/jsonpath_test.go; internal/regogen/{local.go, operand.go, pipcall.go, request.go}; 64 calls sb did not attribute
- delegate `stepKind` lines 159-159
- field `stepKey` lines 162-162
- field `stepDeep` lines 163-163
- field `stepStar` lines 164-164
- field `stepFilter` lines 165-165
- field `stepIndex` lines 166-166
- field `stepIndexList` lines 167-167
- field `stepSlice` lines 168-168
- field `stepRootBracket` lines 169-169
- field `stepFunction` lines 170-170
- struct `step` lines 173-183
- field `word` lines 189-189
- field `space` lines 190-190
- field `filterToken` lines 194-194
- field `tokenRE` lines 196-200
- field `bracketKeyRE` lines 201-201
- field `indexListRE` lines 202-202
- field `sliceRE` lines 203-203
- field `indexRE` lines 204-204
- function `Compile` lines 215-217: 13 calls sb did not attribute
- function `CompileRootKey` lines 223-225: used in internal/regogen/{local.go, pipcall.go, pipreplay.go}
- function `compile` lines 227-264: 2 calls sb did not attribute
- function `parseStep` lines 269-328
- function `parseInt` lines 334-347: used in internal/jsonpath/filter.go
- function `appendMembers` lines 538-544
- function `walk` lines 550-574: 4 calls sb did not attribute
- function `slice` lines 582-599
- delegate `outcome` lines 602-602
- field `computed` lines 605-605
- field `empty` lines 610-610
- field `thrown` lines 613-613
- function `function` lines 621-640: 2 calls sb did not attribute
- function `apply` lines 658-725: used in internal/regogen/metamorphic_test.go
- function `isSpace` lines 729-731

## internal/jsonvalue/decimal.go (+10)

Added: 186-195

- struct `Decimal` lines 28-254: used in components/authz-agent/internal/m2m/{m2m.go, m2m_test.go}; components/authz-agent/internal/pull/pull.go; components/authz-agent/internal/snapshot/{health.go, registry.go}; internal/jsonvalue/decimal_test.go; internal/legacyvalue/record_test.go; internal/regogen/{jsonkey.go, rel.go}; 168 calls sb did not attribute
- field `maxExponent` lines 36-36
- function `ParseDecimal` lines 45-48: used in internal/jsonpath/{filter.go, jayway_test.go, jsonpath.go}; internal/jsonvalue/decimal_test.go; internal/regogen/{jsonkey.go, pipcall.go, rel.go}
- function `ParseBigDecimal` lines 54-57: used in internal/jsonvalue/decimal_test.go; internal/legacyvalue/record.go; internal/regogen/{deep.go, eqtokens.go, operand.go}
- function `parseDecimal` lines 61-123
- function `newDecimal` lines 127-134
- function `isDigit` lines 138-140
- function `digitValue` lines 145-154
- function `compareMagnitude` lines 206-217

## internal/jsonvalue/encode.go (+114)

Added: 1-114

- function `Encode` lines 25-29: used in components/authz-agent/cmd/filter-corpus/main.go; components/authz-agent/internal/legacy/legacy.go; components/authz-agent/internal/m2m/m2m.go; components/authz-policy-admin/handlers.go; internal/jsonpath/filter.go; internal/jsonvalue/encode_test.go; internal/regogen/{filtersub_test.go, filtertext.go, pipreplay.go, pipresponse_test.go}; test/integration/pipstub/main.go; 7 calls sb did not attribute
- function `writeJSONText` lines 31-63
- function `writeJSONString` lines 70-114

## internal/jsonvalue/value.go (+15)

Added: 75-78, 81-82, 86, 96-98, 105-107, 112, 127

- delegate `Value` lines 29-29
- delegate `Number` lines 35-35
- struct `Object` lines 38-73: used in components/authz-agent/internal/m2m/m2m.go; components/authz-agent/internal/pull/pull.go; components/authz-agent/internal/server/{decide.go, public.go, public_test.go, server.go, server_test.go}; components/authz-policy-admin/{handlers.go, store_test.go}; internal/jsonpath/{jayway_test.go, jsonpath.go, jsonpath_test.go} and 9 more; 263 calls sb did not attribute
- function `NewObject` lines 44-46: used in components/authz-agent/cmd/filter-corpus/main.go; components/authz-agent/internal/snapshot/subject.go; internal/regobuiltins/builtins.go; internal/regogen/{deep.go, filtersub_test.go, filtertext.go, local.go, pipcall.go, pipreplay.go, project.go}; 4 calls sb did not attribute
- field `MaxDepth` lines 77-77
- function `Decode` lines 83-94: used in components/authz-agent/internal/corpus/subject.go; components/authz-agent/internal/legacy/{legacy.go, legacy_test.go}; components/authz-agent/internal/server/{cost_test.go, public_test.go, specconform_test.go}; components/authz-agent/internal/snapshot/{filter_test.go, registry_test.go, subject.go}; components/authz-policy-admin/{convert.go, validate.go}; internal/jsonpath/jayway_test.go and 6 more; 29 calls sb did not attribute
- function `decodeValue` lines 98-143
- function `FromAST` lines 148-150: used in internal/jsonvalue/value_test.go
- function `FromASTKnown` lines 155-199: used in internal/regobuiltins/builtins.go

## internal/legacyvalue/javatext.go (+11)

Added: 86, 93-102

- function `Fold` lines 30-46: used in internal/legacyvalue/record.go; internal/regogen/{deep.go, entitlements.go, eqtokens.go, project.go}
- function `NumberText` lines 51-68: used in internal/legacyvalue/{record.go, structuretext.go}; internal/regogen/eqtokens.go
- function `isIntegerText` lines 71-82
- function `Text` lines 87-91: used in internal/jsonpath/jayway_test.go; internal/legacyvalue/record.go; internal/regogen/{local.go, pipcall.go, pipresponse_test.go, subject.go}
- function `FilterText` lines 96-101: used in internal/regogen/filtersub.go
- function `writeText` lines 103-135

## internal/legacyvalue/record.go (+76)

Added: 17, 87-88, 90, 95-98, 115-127, 132, 135-145, 156-159, 161, 164, 178-186, 188-189, 192-193, 199-211, 213-223

- delegate `State` lines 20-20
- field `StateValue` lines 27-27
- field `StateNullElement` lines 31-31
- field `StateAbsent` lines 32-32
- field `StateNull` lines 33-33
- field `StatePIPEmpty` lines 34-34
- field `StateEmptyColl` lines 35-35
- field `StateEmptySel` lines 36-36
- field `StateIndexOOB` lines 37-37
- field `StatePIPNull` lines 38-38
- field `StateError` lines 39-39
- delegate `Class` lines 44-44
- field `ClassString` lines 49-49
- field `ClassScalar` lines 51-51
- field `ClassList` lines 53-53
- field `ClassOther` lines 56-56
- delegate `Type` lines 60-60
- field `TypeString` lines 64-64
- field `TypeNumber` lines 65-65
- field `TypeBoolean` lines 66-66
- field `TypeArray` lines 67-67
- field `TypeObject` lines 68-68
- struct `Record` lines 77-107
- function `WithState` lines 111-113
- delegate `Parts` lines 116-116
- field `PartKey` lines 121-121
- field `PartKeys` lines 123-123
- field `AllParts` lines 125-125
- function `Of` lines 131-133: used in components/authz-agent/internal/server/public_test.go; internal/legacyvalue/record_test.go; internal/regogen/operand.go
- function `OfParts` lines 138-143: used in internal/legacyvalue/record_test.go; internal/regogen/project.go
- function `of` lines 145-167: used in internal/regogen/gen.go
- function `scalar` lines 169-176: 1 calls sb did not attribute
- function `listRecord` lines 181-197
- function `EqualsString` lines 205-214
- function `elementText` lines 218-224
- function `classify` lines 228-239

## internal/legacyvalue/structuretext.go (+91)

Added: 1-91

- function `StructureText` lines 30-61: used in internal/legacyvalue/{record.go, structuretext_test.go}; internal/regogen/{deep.go, project.go}
- function `structureNumberText` lines 71-91

## internal/policyir/cond.go (+15)

Added: 144-145, 152, 188-189, 197, 230-235, 239-241

- delegate `Place` lines 27-27
- field `PlaceSimplified` lines 31-31
- field `PlaceRuleCondition` lines 32-32
- field `PlaceRuleTarget` lines 33-33
- field `PlacePolicyTarget` lines 34-34
- field `PlaceSetTarget` lines 35-35
- field `places` lines 38-38
- function `Places` lines 41-41
- delegate `Operator` lines 46-46
- field `OpEQ` lines 50-50
- field `OpNE` lines 51-51
- field `OpLT` lines 52-52
- field `OpLE` lines 53-53
- field `OpGT` lines 54-54
- field `OpGE` lines 55-55
- field `OpIsNull` lines 56-56
- field `OpIsNotNull` lines 57-57
- field `OpIsEmpty` lines 58-58
- field `OpIsNotEmpty` lines 59-59
- field `OpIn` lines 60-60
- field `OpNotIn` lines 61-61
- field `OpContains` lines 62-62
- field `OpNotContains` lines 63-63
- field `OpContainsAny` lines 64-64
- field `OpNotContainsAny` lines 65-65
- field `OpIsSubset` lines 66-66
- field `OpIsNotSubset` lines 67-67
- field `OpMatch` lines 68-68
- field `OpNotMatch` lines 69-69
- field `operators` lines 72-76
- function `Operators` lines 79-79: used in internal/policyir/cond_test.go; internal/regogen/placement_test.go
- interface `Atom` lines 104-106: 6 calls sb did not attribute
- struct `Const` lines 109-132: 6 calls sb did not attribute
- struct `IsM2M` lines 114-133: 6 calls sb did not attribute
- struct `Access` lines 119-134: 6 calls sb did not attribute
- struct `Compare` lines 126-135: 6 calls sb did not attribute
- function `NewCompare` lines 153-159: used in internal/policyir/parse.go
- function `validateCompare` lines 161-215
- function `compiles` lines 219-228
- function `patternText` lines 233-246
- struct `Condition` lines 252-274: used in internal/policyir/cond_test.go; internal/regogen/gen.go
- function `NewCondition` lines 260-269: used in internal/policyir/{cond_test.go, parse.go}
- function `validateCondition` lines 276-294: used in internal/policyir/tree.go
- function `validateAtom` lines 296-309
- method `Unary` lines 82-89: used in components/authz-policy-admin/condition.go; internal/regogen/placement_test.go; 8 calls sb did not attribute
- method `TakesList` lines 93-100: used in internal/policyir/{cond_test.go, parse.go}
- method `atom` lines 136-136: 6 calls sb did not attribute

## internal/policyir/dump.go (+48)

Added: 67-69, 173-180, 185, 192, 206, 208, 222-224, 231-236, 238, 269, 274-276, 278-279, 287-303

- function `externalID` lines 92-97
- function `frontend` lines 99-104
- function `algorithm` lines 106-111
- function `pipFields` lines 113-149
- function `dumpPredicates` lines 151-160
- function `dumpCondition` lines 162-167
- function `FormatCondition` lines 173-173: used in components/authz-policy-admin/convert_test.go; internal/policyir/{cond_test.go, parse_test.go}; internal/regogen/gen.go
- function `FormatConditionBrief` lines 178-178: used in internal/regogen/comment.go
- function `formatCondition` lines 180-190
- function `formatAtom` lines 192-214
- function `FormatOperand` lines 222-222
- function `formatOperand` lines 224-285
- function `writtenBack` lines 289-302
- function `formatUnsupported` lines 304-306
- function `quoteAll` lines 308-314
- function `sortedMap` lines 316-323
- method `Dump` lines 32-90: 17 calls sb did not attribute

## internal/policyir/export.go (+461)

Added: 24, 26-27, 37-38, 42, 44-82, 85-98, 115-125, 139-141, 170-171, 178-179, 181-182, 195-196, 199, 201-214, 228-234, 240, 243, 246, 256, 259, 263-266, 268-276, 280-281, 284, 287-290, 295, 301, 306, 318-329, 335-339, 342, 358-466, 471-474, 477-478, 485, 497, 499, 593-632, 642-664, 706-710, 738-740, 804-817, 861-926, 974-1000, 1104-1110, 1142-1144, 1432-1437

- struct `Export` lines 32-48
- struct `Element` lines 52-83: 114 calls sb did not attribute
- struct `ElementError` lines 87-97: 78 calls sb did not attribute
- function `elementError` lines 92-94
- function `FromRegular` lines 144-356: used in components/authz-agent/internal/snapshot/{registry.go, registry_test.go}; components/authz-policy-admin/{convert_test.go, totality_test.go}; internal/policyir/export_test.go; internal/regogen/{filtersub_test.go, filterveto_test.go, gen_test.go, placement_test.go, scaling_test.go}; 1 calls sb did not attribute
- function `identicalSets` lines 363-390
- function `samePIP` lines 417-433
- function `sameJSONMap` lines 437-448
- function `sameJSON` lines 458-465
- struct `exportHead` lines 469-475
- function `readHead` lines 481-501
- function `topLevelApplies` lines 505-512
- struct `exportSet` lines 514-623: 1 calls sb did not attribute
- struct `exportIterate` lines 538-541
- struct `exportPolicy` lines 543-552: 1 calls sb did not attribute
- struct `exportRule` lines 554-571: 1 calls sb did not attribute
- struct `exportCustom` lines 573-576
- field `ruleTypeFrontend` lines 578-578
- function `condition` lines 582-591: 1 calls sb did not attribute
- function `enumText` lines 596-598
- function `cutExpression` lines 626-630
- function `algorithmOf` lines 633-638
- struct `setBuilder` lines 640-819: 42 calls sb did not attribute
- function `groupRefused` lines 658-665
- function `foreignElement` lines 670-693
- struct `nodeError` lines 754-769: 78 calls sb did not attribute
- function `within` lines 773-779
- function `predicates` lines 823-847
- function `isNull` lines 849-851
- function `compact` lines 853-859
- function `notGlobal` lines 868-899
- function `onlyRoles` lines 903-925
- function `simplifiedGroup` lines 929-972
- function `GlobalResourceType` lines 977-979: used in components/authz-policy-admin/validate.go
- function `SimplifiedSetTarget` lines 987-992: used in components/authz-policy-admin/convert.go
- function `SimplifiedPolicyTarget` lines 997-999: used in components/authz-policy-admin/convert.go
- function `resourceTypeTarget` lines 1004-1006
- function `operationTarget` lines 1010-1015
- function `rolesTarget` lines 1019-1021: 1 calls sb did not attribute
- function `onlyEquality` lines 1024-1035
- function `rolesOf` lines 1039-1061
- struct `exportPIP` lines 1063-1092: 1 calls sb did not attribute
- function `readPIP` lines 1096-1158
- function `present` lines 1162-1167
- function `decodeExact` lines 1175-1178
- function `decodeReporting` lines 1183-1197
- struct `keyPath` lines 1202-1228: 111 calls sb did not attribute
- field `rawMessageType` lines 1230-1230
- struct `exactFilter` lines 1236-1390: 10 calls sb did not attribute
- struct `unknownKey` lines 1248-1251
- struct `exactField` lines 1254-1257
- function `ignoredKeysOf` lines 1364-1369
- function `containerEnds` lines 1394-1409
- function `stringEnd` lines 1413-1422
- function `skipSpace` lines 1426-1431
- function `setElement` lines 1435-1437

## internal/policyir/key.go (+111)

Added: 1-111

- struct `Key` lines 28-30: used in internal/policyir/key_test.go
- function `appendKey` lines 48-107
- function `appendKeyString` lines 109-111
- method `Key` lines 38-42: used in internal/policyir/key_test.go

## internal/policyir/operand.go (+60)

Added: 27-28, 48-52, 55-57, 59-60, 119-141, 182-187, 190-203, 318-322

- interface `Operand` lines 29-31: 2 calls sb did not attribute
- interface `Literal` lines 34-37: 1 calls sb did not attribute
- struct `Operation` lines 40-190: 2 calls sb did not attribute
- struct `ResourceType` lines 43-191: 2 calls sb did not attribute
- struct `Resource` lines 58-192: 2 calls sb did not attribute
- delegate `SubjectAttr` lines 64-64
- field `SubjectID` lines 69-69
- field `SubjectName` lines 70-70
- field `SubjectType` lines 71-71
- field `SubjectServiceAccount` lines 72-72
- field `SubjectRoles` lines 73-73
- field `SubjectScopes` lines 74-74
- field `SubjectPermissions` lines 75-75
- field `SubjectIsM2M` lines 76-76
- field `SubjectPermissionScope` lines 77-77
- field `subjectAttrs` lines 80-83
- struct `Subject` lines 91-193: used in components/authz-agent/internal/snapshot/{decide.go, filter.go}; 2 calls sb did not attribute
- struct `PIPRef` lines 106-194: 2 calls sb did not attribute
- struct `Entitled` lines 114-195: 2 calls sb did not attribute
- struct `RefusedSubject` lines 130-202: used in components/authz-policy-admin/condition.go; internal/policyir/pattern.go; 2 calls sb did not attribute
- struct `PassValue` lines 146-196: 2 calls sb did not attribute
- struct `String` lines 152-205: 3 calls sb did not attribute
- struct `Number` lines 158-206: 3 calls sb did not attribute
- struct `Bool` lines 163-207: 3 calls sb did not attribute
- struct `List` lines 172-200: 2 calls sb did not attribute
- struct `Pattern` lines 180-201: 2 calls sb did not attribute
- field `numberSyntax` lines 211-211
- function `NewNumber` lines 215-220
- function `NewList` lines 225-231
- function `validateList` lines 233-265: used in internal/policyir/parse.go
- function `validatePath` lines 267-272
- function `validateOperand` lines 274-328: used in internal/policyir/cond.go
- function `validateSubject` lines 330-341
- method `operand` lines 203-203: 2 calls sb did not attribute

## internal/policyir/parse.go (+168)

Added: 103-111, 132-149, 205, 209, 212, 352, 460-461, 463, 469-490, 492-514, 516, 550-552, 569-575, 598-603, 606-611, 613-616, 625, 629-647, 685-688, 692, 695-696, 701-702, 704, 707-711, 713-728, 736-746

- struct `SyntaxError` lines 30-37: 75 calls sb did not attribute
- function `ParseCondition` lines 55-73: used in components/authz-policy-admin/condition.go; internal/policyir/{export.go, parse_test.go}; internal/regogen/placement_test.go
- function `wholeBool` lines 79-87
- function `asciiLower` lines 89-94
- struct `parser` lines 96-745: used in components/authz-agent/internal/snapshot/deep_test.go; internal/regogen/filtersub_test.go; 138 calls sb did not attribute
- field `pathKey` lines 107-107
- field `jpFilter` lines 108-108
- field `jpFunction` lines 109-109
- field `quotedRE` lines 113-113
- field `listCommaRE` lines 114-114
- field `bracketsRE` lines 115-115
- field `bracketParenRE` lines 116-116
- field `tightCompareRE` lines 117-117
- field `connectiveRE` lines 118-118
- field `lowerKeywordRE` lines 119-119
- field `lowerOpRE` lines 120-120
- field `misspelledOpRE` lines 121-121
- field `stringLitRE` lines 122-122
- field `numberLitRE` lines 123-123
- field `numberStartRE` lines 124-124
- field `entitledRE` lines 125-125
- field `entitledAsRE` lines 126-126
- field `indexStepRE` lines 127-127
- field `accessRE` lines 128-128
- field `constAtomRE` lines 129-129
- field `filteredRE` lines 130-130
- field `listMoreRE` lines 131-131
- field `boolAttrRE` lines 132-132
- field `boolLitRE` lines 133-133
- field `prefixedPathRE` lines 137-138
- field `plainPathRE` lines 139-139
- field `matchTokenRE` lines 144-144
- field `matchBracketsRE` lines 145-145
- field `matchNumberRE` lines 146-146
- field `scopeTokenRE` lines 150-150
- field `pipTokenRE` lines 151-151
- field `patternReserved` lines 156-161
- field `keywords` lines 163-167
- field `opWords` lines 170-183
- function `newParser` lines 185-213
- function `dropLineBreaks` lines 218-237
- function `joinListCommas` lines 241-261
- function `startsWithNumber` lines 263-266
- function `lastRune` lines 268-271
- function `firstRune` lines 273-276
- function `isWord` lines 278-280
- function `isSpaceOrWord` lines 282-284
- function `endsToken` lines 288-294
- function `followedByConnective` lines 373-375
- function `readPattern` lines 481-508: used in internal/policyir/cond.go
- function `isASCII` lines 510-517
- function `pathToken` lines 640-648
- function `normalizeIndexes` lines 653-683
- function `isSubjectToken` lines 697-699
- function `isScopeToken` lines 703-705
- function `SubjectOperand` lines 720-734: used in internal/regogen/mapping.go
- function `truncate` lines 747-752

## internal/policyir/pattern.go (+133)

Added: 1-133

- function `patternRefused` lines 80-85: used in internal/policyir/pattern_test.go
- function `conditionRefused` lines 91-117: used in internal/policyir/export.go
- function `trueCondition` lines 121-123: used in internal/policyir/export.go
- function `isolatedTarget` lines 128-133: used in internal/policyir/export.go
- method `Regexp` lines 28-53
- method `Anchored` lines 60-75: used in internal/policyir/pattern_test.go; internal/regogen/template.go

## internal/policyir/tree.go (+44)

Added: 155-160, 188-194, 256-257, 309, 327-330, 333, 336-342, 344-346, 349-353, 406, 409, 426, 463, 477-479, 485

- delegate `Algorithm` lines 27-27
- field `AlgorithmAbsent` lines 32-32
- field `AlgorithmDenyOverrides` lines 33-33
- field `AlgorithmPermitOverrides` lines 34-34
- field `AlgorithmDenyUnlessPermit` lines 35-35
- field `AlgorithmPermitUnlessDeny` lines 36-36
- field `algorithms` lines 39-42
- delegate `Effect` lines 47-47
- field `EffectAbsent` lines 51-51
- field `EffectAllow` lines 52-52
- field `EffectDeny` lines 53-53
- field `EffectNotApplicable` lines 54-54
- field `EffectUseFilterCondition` lines 55-55
- field `effects` lines 58-58
- delegate `Dialect` lines 61-61
- field `DialectRSQL` lines 66-66
- field `DialectSQL` lines 67-67
- field `DialectMongoDB` lines 68-68
- field `DialectQueryDSL` lines 69-69
- field `dialects` lines 72-72
- function `Dialects` lines 76-76
- struct `Predicates` lines 79-85
- struct `CustomPredicate` lines 90-93
- struct `Tree` lines 97-419: used in internal/policyir/export_test.go
- struct `SimplifiedGroup` lines 112-121
- struct `SimplifiedPolicy` lines 124-136
- struct `PolicySet` lines 139-166
- struct `Iterate` lines 175-178
- struct `Policy` lines 181-195
- struct `Rule` lines 198-209
- delegate `PIPType` lines 212-212
- field `PIPGeneral` lines 217-217
- field `PIPFiltered` lines 218-218
- field `PIPHeader` lines 219-219
- field `PIPToken` lines 220-220
- field `PIPMapping` lines 221-221
- field `PIPPermissionScope` lines 222-222
- field `pipTypes` lines 225-225
- struct `PIP` lines 229-281: used in internal/policyir/export_test.go
- function `NewTree` lines 313-319: used in internal/policyir/{dump_test.go, export.go, tree_test.go, unsupported_test.go}
- struct `checker` lines 321-529: used in internal/regogen/{gen_test.go, placement_test.go}; 43 calls sb did not attribute
- struct `node` lines 331-357: used in components/authz-agent/internal/server/specconform_test.go; internal/policyir/unsupported.go; 113 calls sb did not attribute
- function `checkPredicates` lines 531-545
- function `checkJSON` lines 549-558

## internal/policyir/unsupported.go (+172)

Added: 30-31, 33-34, 87, 102-195, 199, 202, 207-208, 210, 213-214, 217-222, 227, 232, 236-288, 291-292, 294-296

- delegate `Form` lines 25-25
- field `FormJSONPath` lines 35-35
- field `FormSyntax` lines 39-39
- field `FormNestedIterate` lines 41-41
- field `FormPIPExtension` lines 44-44
- field `forms` lines 47-47
- struct `Unsupported` lines 51-54: used in internal/policyir/export_test.go
- function `validateUnsupported` lines 56-64: used in internal/policyir/{cond.go, operand.go}
- struct `Finding` lines 67-74
- delegate `WarningKind` lines 110-110
- field `WarnIsM2MComparison` lines 116-116
- field `WarnNoEffect` lines 119-119
- struct `Warning` lines 125-155: 110 calls sb did not attribute
- function `warning` lines 157-159
- struct `sibling` lines 271-283: used in internal/policyir/tree.go; 108 calls sb did not attribute
- function `labels` lines 287-300: used in internal/policyir/tree.go
- function `groupLabel` lines 302-304
- function `simplifiedPolicyLabel` lines 306-306
- function `setLabel` lines 307-307: 1 calls sb did not attribute
- function `policyLabel` lines 308-308
- function `ruleLabel` lines 309-309
- method `Unsupported` lines 80-106: used in internal/policyir/export_test.go
- method `Warnings` lines 165-183
- method `walk` lines 190-234: 4 calls sb did not attribute
- method `EachPredicates` lines 239-267

## internal/regobuiltins/builtins.go (+36)

Added: 18-23, 50, 52-55, 200-208, 210-211, 213-222, 224, 229, 235, 237

- struct `Builtin` lines 44-48
- function `All` lines 51-56: used in components/authz-agent/internal/server/{public.go, public_test.go}
- function `Capabilities` lines 60-66: 3 calls sb did not attribute
- function `Options` lines 69-76: used in internal/regobuiltins/httpsend_test.go; internal/regogen/jsonpath.go
- struct `Documents` lines 83-149: used in components/authz-agent/internal/server/public.go; components/authz-agent/internal/snapshot/{decide.go, filter.go, subject.go}; internal/regogen/{bulk.go, entitlements_test.go, filtersub.go, filtersub_test.go, gen_test.go, pipcall_test.go, pipresponse_test.go, project.go} and 1 more; 24 calls sb did not attribute
- function `NewDocuments` lines 88-90: used in internal/regogen/{bulk.go, project.go}
- struct `documentsKey` lines 144-144
- struct `convertedKey` lines 153-153
- function `JSONOf` lines 163-190: used in internal/regobuiltins/httpsend.go
- field `maxPaths` lines 196-196
- field `paths` lines 198-201
- struct `pathKey` lines 205-208
- function `CompilePath` lines 212-214: used in internal/regogen/{jsonpath.go, pipcall.go, project.go}
- function `CompileRootKeyPath` lines 218-220: used in internal/regogen/pipcall.go
- function `cachedPath` lines 222-240

## internal/regobuiltins/httpsend.go (+514)

Added: 1-514

- field `DefaultTimeout` lines 42-42
- field `maxResponseBody` lines 47-47
- struct `HTTP` lines 53-72: 22 calls sb did not attribute
- struct `httpKey` lines 67-67
- struct `requestIDKey` lines 74-74
- function `WithRequestID` lines 80-82: used in components/authz-agent/internal/snapshot/subject.go
- struct `callsKey` lines 84-84
- struct `calls` lines 87-337: used in components/authz-agent/internal/snapshot/registry_test.go; components/authz-policy-admin/totality_test.go; internal/regobuiltins/httpsend_test.go; test/integration/pipstub/{main.go, main_test.go}; 27 calls sb did not attribute
- struct `call` lines 97-104
- function `WithCalls` lines 115-117: used in components/authz-agent/internal/snapshot/subject.go; internal/regobuiltins/httpsend_test.go; internal/regogen/{entitlements_test.go, filtersub_test.go, gen_test.go, pipcall_test.go, pipresponse_test.go, scope_test.go}
- function `StatusRead` lines 122-122
- struct `Answer` lines 127-137
- function `ReadAnswer` lines 145-183: used in internal/regogen/{entitlements.go, pipcall.go, scope.go}
- function `FailedPIPs` lines 188-196: used in components/authz-agent/internal/snapshot/decide.go
- function `Sent` lines 200-208: used in internal/regobuiltins/httpsend_test.go
- field `record` lines 210-210
- field `httpSendDecl` lines 212-217
- struct `sendRequest` lines 220-391: 1 calls sb did not attribute
- field `codeNoToken` lines 232-232
- field `codeTimeout` lines 233-233
- field `codeTransport` lines 234-234
- function `httpSend` lines 246-290
- function `Send` lines 294-296: used in components/authz-agent/internal/server/public.go; internal/regogen/{filtersub.go, pipresponse_test.go, scope.go}
- function `NoteFailed` lines 301-305: used in internal/regogen/pipcall.go
- function `send` lines 339-377: 1 calls sb did not attribute
- function `do` lines 396-467: 10 calls sb did not attribute
- function `readBody` lines 475-491
- function `response` lines 493-514

## internal/regogen/bulk.go (+338)

Added: 1-338

- struct `Bulk` lines 31-338: used in components/authz-agent/internal/snapshot/decide.go; internal/regobuiltins/{builtins.go, httpsend.go}; internal/regogen/{bulk_test.go, entitlements_test.go, pipcall.go}; 7 calls sb did not attribute
- struct `resourceView` lines 56-188: 1 calls sb did not attribute
- struct `listKey` lines 82-85
- function `identity` lines 90-100
- function `itemOperand` lines 192-194
- function `NewBulk` lines 200-233: used in components/authz-agent/internal/snapshot/decide.go; internal/regogen/bulk_test.go

## internal/regogen/comment.go (+358)

Added: 1-358

- struct `exprSrc` lines 41-55
- field `uuidRE` lines 57-57
- function `setLabel` lines 65-71: 1 calls sb did not attribute
- function `escapeID` lines 75-88: used in internal/regogen/gen.go
- struct `nodeSource` lines 99-102
- function `condText` lines 105-110: used in internal/regogen/gen.go
- function `atomText` lines 112-114: used in internal/regogen/gen.go
- function `nodeHead` lines 118-123: used in internal/regogen/gen.go
- function `stamp` lines 126-142: used in internal/regogen/gen.go
- function `clauseNodes` lines 146-166
- function `isBelow` lines 172-175: used in internal/regogen/gen_test.go
- function `dnfNodes` lines 179-185: used in internal/regogen/{gen.go, groups.go}
- function `atoms` lines 189-199: 1 calls sb did not attribute
- function `clauseComment` lines 205-224: used in internal/regogen/gen.go
- function `commentLine` lines 227-234: used in internal/regogen/gen.go
- field `legend` lines 237-310
- struct `commenter` lines 313-358: used in internal/regogen/gen.go; 7 calls sb did not attribute
- method `source` lines 92-97: 7 calls sb did not attribute

## internal/regogen/deep.go (+506)

Added: 1-506

- struct `deep` lines 47-360: 6 calls sb did not attribute
- function `deepOf` lines 53-60: used in internal/regogen/project_test.go
- function `writeDeep` lines 62-109
- function `textShape` lines 112-112
- function `structureAlias` lines 120-122
- function `stringAlias` lines 124-124
- delegate `deepIndex` lines 138-138
- struct `textGroup` lines 144-254: 22 calls sb did not attribute
- field `maxSubsetLeaves` lines 153-153
- field `maxLookup` lines 154-154
- field `noTextsGroup` lines 200-200
- field `noTextsShape` lines 201-201
- function `textsKey` lines 219-219
- function `deepAny` lines 278-280: used in internal/regogen/groups.go
- function `deepAll` lines 282-284: used in internal/regogen/subset.go
- function `elementAlts` lines 290-303: used in internal/regogen/{operand.go, project.go}
- function `elementIndex` lines 310-331: used in internal/regogen/{operand.go, project.go, project_test.go}
- function `eqElements` lines 336-345: used in internal/regogen/project.go
- function `asList` lines 347-352
- field `noTexts` lines 358-358
- function `textsTerm` lines 362-371
- function `deepsTerm` lines 373-379: used in internal/regogen/project.go
- function `altsTerm` lines 381-387: used in internal/regogen/{project.go, subset.go}
- field `noTextsGroups` lines 423-424
- function `deepHit` lines 429-429
- function `deepMiss` lines 431-431
- field `deepHitName` lines 433-433
- field `deepFunctions` lines 439-455
- function `regoDeepAny` lines 459-461: used in internal/regogen/template.go
- function `regoDeepNone` lines 463-465: used in internal/regogen/template.go
- function `regoDeepAll` lines 467-469: used in internal/regogen/subset.go
- function `regoDeepNotAll` lines 471-473: used in internal/regogen/subset.go
- function `literalDeepAny` lines 479-496: used in internal/regogen/template.go
- function `regoEqAll` lines 500-502: used in internal/regogen/template.go
- function `regoEqNotAll` lines 504-506: used in internal/regogen/template.go
- method `add` lines 157-194: 17 calls sb did not attribute
- method `has` lines 222-236: 2 calls sb did not attribute
- method `tooBig` lines 261-274: used in internal/regogen/{project.go, project_test.go}
- method `term` lines 394-421: 6 calls sb did not attribute

## internal/regogen/dialecttext.go (+81)

Added: 1-81

- struct `dialectText` lines 30-69: used in internal/regogen/{filtertext.go, rsql.go}; 125 calls sb did not attribute
- function `newDialectText` lines 38-38: used in internal/regogen/{filtertext.go, rsql.go}
- function `sqlMayEndInLineComment` lines 78-81

## internal/regogen/entitlements.go (+219)

Added: 1-219

- function `entText` lines 45-50: used in internal/regogen/gen.go
- field `entitlementsPIP` lines 54-54
- function `entCall` lines 58-60: used in internal/regogen/{entitlements_test.go, pipresponse_test.go, project.go}
- field `EntRecordDecl` lines 63-68
- function `entRecordFunction` lines 70-96: used in internal/regogen/jsonpath.go
- function `entResolve` lines 106-170: used in internal/regogen/pipresponse_test.go
- function `pyList` lines 175-182
- function `truthy` lines 186-203: used in internal/regogen/{local.go, mapping.go, scope.go}
- function `pyStr` lines 208-210
- function `containsString` lines 212-219

## internal/regogen/eqtokens.go (+196)

Added: 1-196

- field `numberKeyPrefix` lines 48-48
- field `valueTokenPrefix` lines 49-49
- struct `scalarTokens` lines 55-71: used in internal/regogen/{operand.go, project.go}; 4 calls sb did not attribute
- delegate `numberValue` lines 74-74
- function `inputNumberValue` lines 79-85
- function `literalNumberValue` lines 89-94
- function `numberTokens` lines 96-98
- function `stringTokens` lines 102-109
- function `scalarTokensOf` lines 113-127: used in internal/regogen/{operand.go, project.go}
- function `scalarTokensOfRecord` lines 131-142: used in internal/regogen/project.go
- function `listTokens` lines 147-173: used in internal/regogen/project.go
- function `splitTokens` lines 180-196: used in internal/regogen/template.go

## internal/regogen/expr.go (+226)

Added: 1-226

- field `clsIndexEq` lines 26-26
- field `clsIndexIn` lines 27-27
- field `clsCheck` lines 28-28
- field `clsBuiltin` lines 29-29
- field `clsAfterBuilt` lines 30-30
- struct `expr` lines 34-53
- struct `fact` lines 58-65
- delegate `factField` lines 68-68
- field `factState` lines 72-72
- field `factClass` lines 73-73
- field `factValue` lines 74-74
- delegate `clause` lines 78-78
- delegate `dnf` lines 82-82
- field `dnfTrue` lines 85-85
- field `dnfFalse` lines 86-86
- function `conj` lines 110-122: 87 calls sb did not attribute
- function `union` lines 125-138: used in internal/regogen/{filter.go, gen.go, groups.go, iterate.go, leaf.go, template.go}
- function `prod` lines 141-152: used in internal/regogen/{gen.go, leaf.go, template.go}
- function `consistent` lines 158-202
- function `guarded` lines 205-212: used in internal/regogen/gen.go
- method `key` lines 89-96: 3 calls sb did not attribute
- method `key` lines 98-104: 3 calls sb did not attribute
- method `isTrue` lines 106-106: used in internal/regogen/{filter.go, gen.go}
- method `isFalse` lines 107-107: used in internal/regogen/{filter.go, gen.go, groups.go, iterate.go, leaf.go}
- method `refsNodeRule` lines 217-226: used in internal/regogen/gen.go

## internal/regogen/failures.go (+139)

Added: 1-139

- struct `Rejection` lines 27-40
- field `FormGenerator` lines 47-47
- field `FormSpecification` lines 48-48
- struct `gapError` lines 52-60: 76 calls sb did not attribute
- function `gap` lines 57-57: used in internal/regogen/{gen.go, leaf.go}
- struct `RejectedError` lines 69-79: 76 calls sb did not attribute
- struct `Failure` lines 97-107
- method `fail` lines 110-117: 27 calls sb did not attribute
- method `whereText` lines 121-139: used in internal/regogen/{gen.go, operand.go}

## internal/regogen/filter.go (+538)

Added: 1-538

- struct `status` lines 54-72: used in internal/regobuiltins/httpsend.go; 6 calls sb did not attribute
- struct `fnode` lines 75-299
- struct `fsimp` lines 99-104
- struct `filterPlan` lines 107-111
- function `GenerateFilter` lines 117-174: used in components/authz-policy-admin/totality_test.go; internal/regogen/{filtersub_test.go, filterveto_test.go, metamorphic_test.go, placement_test.go, scaling_test.go}
- struct `filterGen` lines 177-538: used in internal/regobuiltins/httpsend.go; 51 calls sb did not attribute
- function `anyLeaf` lines 221-223
- function `FilterQuery` lines 388-388: used in components/authz-agent/internal/snapshot/registry.go; internal/regogen/{metamorphic_test.go, scaling_test.go}
- struct `Statuses` lines 391-394
- struct `passKey` lines 396-399
- function `ReadStatuses` lines 403-444: used in components/authz-agent/internal/snapshot/filter.go; internal/regogen/{filtersub_test.go, metamorphic_test.go}
- function `passIndex` lines 446-457
- struct `leafStatus` lines 483-490
- method `Filter` lines 464-478: 8 calls sb did not attribute

## internal/regogen/filteralg.go (+635)

Added: 1-635

- delegate `rowKind` lines 56-56
- field `rowsNone` lines 59-59
- field `rowsAll` lines 60-60
- field `rowsSome` lines 61-61
- field `rowsNot` lines 62-62
- field `rowsUnknown` lines 63-63
- struct `rows` lines 68-71
- struct `pair` lines 74-74
- field `none` lines 77-77
- field `allRows` lines 78-78
- field `errDenyAll` lines 85-85
- function `unionRows` lines 90-120
- struct `filterEval` lines 123-614: used in internal/regogen/filter.go; 37 calls sb did not attribute
- struct `tri` lines 143-147
- function `complement` lines 575-587
- function `groupOf` lines 619-627
- function `groupsKey` lines 629-635

## internal/regogen/filterrows.go (+92)

Added: 1-92

- delegate `rowsF` lines 37-37
- field `rowsFalse` lines 40-40
- field `rowsTrue` lines 41-41
- field `rowsDepend` lines 42-42
- function `fAnd` lines 45-53: used in internal/regogen/filteralg.go
- function `fOr` lines 55-63
- function `fNot` lines 65-73: used in internal/regogen/filteralg.go
- struct `rowsVal` lines 78-78
- function `kleeneAnd` lines 82-85: used in internal/regogen/filteralg.go
- function `kleeneOr` lines 89-92: used in internal/regogen/filteralg.go

## internal/regogen/filtersub.go (+467)

Added: 1-467

- delegate `valueKind` lines 56-56
- field `valScalar` lines 59-59
- field `valList` lines 60-60
- field `valUUID` lines 61-61
- field `valKeep` lines 62-62
- field `valEmpty` lines 63-63
- struct `sourceValue` lines 66-70
- struct `substituter` lines 73-350: 10 calls sb did not attribute
- field `templateRE` lines 128-128
- function `fillTemplate` lines 139-157: used in internal/regogen/filtertext.go
- function `fromResolved` lines 217-236: used in internal/regogen/filtersub_test.go
- function `renderValue` lines 353-387: used in internal/regogen/filtersub_test.go
- function `sortedItems` lines 390-396
- function `hashSetOrder` lines 402-425
- function `sortedKeys` lines 427-427: 2 calls sb did not attribute
- function `predicateRejections` lines 433-467: used in internal/regogen/gen.go

## internal/regogen/filtertext.go (+876)

Added: 1-876

- struct `fexpr` lines 33-82: 3 calls sb did not attribute
- struct `fterm` lines 40-458
- struct `customTerm` lines 52-840
- function `hasPredicate` lines 58-58: used in internal/regogen/filteralg.go
- function `orOf` lines 61-66: used in internal/regogen/{filteralg.go, filtertextmeaning_test.go}
- function `distinct` lines 93-103: used in internal/regogen/filteralg.go
- function `andOf` lines 108-132: used in internal/regogen/{filteralg.go, filtertextmeaning_test.go}
- function `bare` lines 136-141
- function `absorbed` lines 145-155
- function `negate` lines 158-177: 11 calls sb did not attribute
- field `filterFields` lines 180-188
- function `render` lines 194-285: 36 calls sb did not attribute
- function `mayBeOr` lines 292-300
- function `rsqlMayBeOr` lines 308-330: used in internal/regogen/filtertext_test.go
- function `sqlMayBeOr` lines 341-392: used in internal/regogen/filtertext_test.go
- field `sqlOperatorBytes` lines 396-396
- function `sqlWordByte` lines 400-402
- function `joinGroups` lines 406-431
- function `negateRSQLTerm` lines 439-446
- field `errNoSubstitution` lines 462-462
- field `mongoNegate` lines 465-466
- field `mongoTokenRE` lines 471-472
- function `braceMongo` lines 479-485
- function `negateMongoLeaf` lines 492-499
- struct `mongoNode` lines 505-510
- struct `mongoItem` lines 515-520
- struct `mongoToken` lines 522-525
- function `mongoTree` lines 532-607
- struct `mongoEdit` lines 610-613
- function `negateMongoText` lines 619-644
- function `mongoNegations` lines 647-677
- function `allObjects` lines 679-686
- struct `FilterAnswer` lines 691-722
- field `FilterAllow` lines 699-699
- field `FilterDeny` lines 700-700
- field `FilterCondition` lines 701-701
- field `_` lines 724-724
- function `filterAnswer` lines 727-771: used in internal/regogen/filter.go
- function `customObject` lines 773-778
- function `opObject` lines 780-785
- function `renderCustom` lines 790-828
- function `namePaths` lines 847-864
- function `collectCustom` lines 866-876

## internal/regogen/gen.go (+1624)

Added: 1-1624

- struct `Options` lines 34-73
- function `DefaultOptions` lines 79-81: used in components/authz-agent/internal/snapshot/registry.go; components/authz-policy-admin/totality_test.go; internal/regogen/{bulk_test.go, domain_test.go, entitlements_test.go, filtersub_test.go, filterveto_test.go, gen_test.go, local_test.go, mapping_test.go, metamorphic_test.go, pipcall_test.go} and 5 more
- struct `Module` lines 84-124
- struct `Stats` lines 129-136
- delegate `nodeKind` lines 138-138
- field `kindRule` lines 141-141
- field `kindPolicy` lines 142-142
- field `kindSet` lines 143-143
- field `kindSimplified` lines 144-144
- field `kindUnknown` lines 145-145
- field `kindIterate` lines 146-146
- struct `node` lines 149-158: used in components/authz-agent/internal/server/specconform_test.go
- struct `simpKid` lines 160-164
- struct `gen` lines 166-1624: used in internal/regogen/{filter.go, gen_test.go, groups.go, iterate.go}; internal/regogen/spectables/load.go; 61 calls sb did not attribute
- function `Generate` lines 240-310: used in components/authz-policy-admin/totality_test.go; internal/regogen/{bulk_test.go, domain_test.go, entitlements_test.go, gen_test.go, local_test.go, mapping_test.go, metamorphic_test.go, pipcall_test.go, placement_test.go, project_test.go, request_test.go} and 3 more
- function `newGen` lines 315-334: used in internal/regogen/filter.go
- function `naturalCompare` lines 458-463: used in internal/regogen/gen_test.go
- function `naturalRuns` lines 465-485
- function `digitRun` lines 487-493
- struct `cond` lines 700-1058: used in internal/regogen/{filter.go, iterate.go}; test/integration/testify/entitlements_test.go; 52 calls sb did not attribute
- field `ruleFailed` lines 1089-1089
- field `rulePermit` lines 1090-1090
- field `failedRef` lines 1093-1093
- field `prefixAnd` lines 1099-1099
- field `prefixRailT` lines 1100-1100
- field `prefixRailF` lines 1101-1101
- function `hashedPrefix` lines 1105-1107
- field `sequentialFactors` lines 1192-1192
- struct `literalVar` lines 1383-1386
- struct `combo` lines 1389-1389
- function `minimize` lines 1392-1424
- field `decisionText` lines 1457-1463
- function `readsPass` lines 1466-1475
- function `clauseText` lines 1477-1494

## internal/regogen/groups.go (+693)

Added: 1-693

- struct `test` lines 31-681: 5 calls sb did not attribute
- struct `Group` lines 68-73
- function `subjectClauses` lines 77-90
- function `EvalGroups` lines 217-250: used in internal/regogen/{gen_test.go, project.go}
- struct `groupIndex` lines 265-283
- field `maxPlainClauses` lines 287-287
- struct `clauseKey` lines 291-294
- struct `factorClause` lines 296-296
- struct `keySource` lines 299-302
- struct `groupEval` lines 416-565: used in internal/regogen/{project.go, subset.go}
- function `listSlot` lines 516-524
- field `slotsPerRef` lines 527-527
- method `group` lines 95-153: 11 calls sb did not attribute
- method `grouped` lines 155-162
- method `groupedT` lines 166-180: used in internal/regogen/gen.go
- method `groupedF` lines 184-198: used in internal/regogen/gen.go
- method `tWithSubject` lines 202-214: used in internal/regogen/gen.go
- method `groupIndex` lines 313-411
- method `list` lines 658-663: 14 calls sb did not attribute
- method `scalar` lines 685-693: 1 calls sb did not attribute

## internal/regogen/iterate.go (+95)

Added: 1-95

- field `scopeFailed` lines 32-32
- method `iterateFlag` lines 35-61: used in internal/regogen/gen.go
- method `anyPass` lines 66-95: used in internal/regogen/gen.go

## internal/regogen/jsonkey.go (+144)

Added: 1-144

- function `pyKey` lines 32-36: used in internal/regogen/{entitlements.go, mapping.go}
- function `typedKey` lines 42-46: used in internal/regogen/pipcall.go
- function `writeKey` lines 52-78
- function `writeTypedScalar` lines 80-88
- function `writePyScalar` lines 90-101
- function `pyNumberKey` lines 108-135
- function `floatKey` lines 139-144

## internal/regogen/jsonpath.go (+168)

Added: 1-168

- field `JSONPathDecl` lines 39-44
- function `Builtins` lines 52-54: 10 calls sb did not attribute
- function `pathText` lines 58-61: 1 calls sb did not attribute
- function `jsonPathFunction` lines 70-121: used in internal/regogen/pipcall_test.go
- struct `jsonPathKey` lines 125-129
- function `Capabilities` lines 134-138: 3 calls sb did not attribute
- delegate `pathError` lines 140-140
- field `errNotAPath` lines 145-145
- field `errNotAFieldSet` lines 146-146
- function `JSONPathRecord` lines 156-158: used in internal/regogen/gen_test.go
- function `jsonPathRecord` lines 162-168: used in internal/regogen/bulk.go
- method `Error` lines 142-142: 75 calls sb did not attribute

## internal/regogen/leaf.go (+1081)

Added: 1-1081

- field `errUndeclared` lines 27-27
- struct `leafRails` lines 32-49
- struct `point` lines 51-58: used in internal/regogen/report.go
- function `matchBeyondDouble` lines 393-408
- function `failedCells` lines 418-476
- function `joinClasses` lines 500-536
- function `rightAt` lines 538-543
- function `kindOf` lines 771-776
- function `sideSubjectOnly` lines 781-795
- function `withoutValueFacts` lines 944-958
- function `uncovered` lines 962-969
- field `rightListOp` lines 1015-1016
- struct `rowSide` lines 1020-1033
- function `readsResource` lines 1078-1081
- method `points` lines 61-81
- method `field` lines 84-93: used in components/authz-agent/internal/snapshot/filter_test.go; internal/regogen/{rel.go, subset.go, template.go}; 7 calls sb did not attribute
- method `bind` lines 97-111: used in internal/regogen/{rel.go, subset.go, template.go}; 8 calls sb did not attribute
- method `cls` lines 114-119: used in internal/regogen/template.go
- method `at` lines 123-134: 6 calls sb did not attribute
- method `compare` lines 145-384: 1 calls sb did not attribute
- method `failed` lines 482-493
- method `byValue` lines 552-769: used in internal/regogen/spectables/load_test.go
- method `cellTemplate` lines 804-871
- method `literalCell` lines 881-940
- method `rightListScalarOps` lines 977-1011
- method `rowPoints` lines 1040-1075

## internal/regogen/local.go (+266)

Added: 1-266

- function `pipName` lines 106-112
- function `headerPIP` lines 117-135: used in internal/regogen/{filtersub.go, filtersub_test.go, mapping.go}
- function `latin1` lines 139-145
- function `tokenPIP` lines 151-179: used in internal/regogen/{filtersub.go, mapping.go, pipcall.go}
- function `tokenSelect` lines 183-201: used in internal/regogen/pipcall.go
- function `tokenDefault` lines 207-216: used in internal/regogen/pipcall.go
- function `defaultText` lines 221-239
- function `splitItems` lines 243-253
- function `pipList` lines 257-266
- method `ResolveSubject` lines 52-102: used in components/authz-agent/internal/snapshot/subject.go; internal/regogen/{entitlements_test.go, local_test.go, mapping_test.go}

## internal/regogen/mapping.go (+196)

Added: 1-196

- function `decodeMapping` lines 114-123
- field `mappingErrorStates` lines 128-131
- method `permissions` lines 48-110: used in internal/regogen/{filtersub.go, local.go}
- method `mappingKeyValues` lines 141-196

## internal/regogen/networkpip.go (+63)

Added: 1-63

- field `PIPDecl` lines 29-33
- struct `inputKey` lines 35-35
- function `pipFunction` lines 39-56: used in internal/regogen/jsonpath.go
- method `Context` lines 61-63: 22 calls sb did not attribute

## internal/regogen/operand.go (+620)

Added: 1-620

- struct `Ref` lines 38-94
- struct `litVal` lines 97-117
- struct `side` lines 121-131: used in internal/regogen/leaf.go
- field `jsonpathRE` lines 133-133
- function `resourceKind` lines 138-149: used in internal/regogen/leaf.go
- function `specPath` lines 154-159: used in internal/regogen/leaf.go
- function `readPath` lines 165-170: used in internal/regogen/pipcall.go
- function `specKey` lines 172-178: used in internal/regogen/{filtersub.go, filtersub_test.go, filtertextmeaning_test.go, mapping.go, pipcall.go}
- function `SpecKey` lines 182-202: used in internal/regogen/request_test.go
- function `literal` lines 205-205: 1 calls sb did not attribute
- function `literalSplit` lines 209-298
- function `refText` lines 362-384
- function `refVar` lines 387-403
- function `refIndex` lines 407-412: used in internal/regogen/{gen.go, leaf.go, project.go, project_test.go}
- field `identRE` lines 414-414
- field `regoKeywords` lines 416-418
- method `operandKind` lines 303-358: 1 calls sb did not attribute
- method `ref` lines 421-474: used in internal/regogen/gen.go
- method `side` lines 477-529: used in internal/regogen/leaf.go
- method `splitList` lines 537-569
- method `pathDomain` lines 582-607
- method `stringKnob` lines 610-620: used in internal/regogen/{leaf.go, request.go}

## internal/regogen/pipcall.go (+686)

Added: 1-686

- field `pipSendText` lines 52-52
- function `pipText` lines 55-62: 1 calls sb did not attribute
- function `pipPath` lines 70-85: used in internal/regogen/{filtersub.go, operand.go}
- field `placeholderRE` lines 88-88
- field `fullPlaceholderRE` lines 89-89
- field `urlResourceRE` lines 92-92
- function `pipPlaceholders` lines 134-161: used in internal/regogen/gen.go
- function `pipCall` lines 165-258: used in internal/regogen/{filtersub.go, project.go}
- field `ownHeaders` lines 265-266
- function `valueText` lines 269-274
- function `pathSegment` lines 280-289
- function `replaceAllIndex` lines 293-303
- function `mapsKeys` lines 305-313
- function `tenantHeaders` lines 317-323
- function `subjectCall` lines 332-347: used in internal/regogen/{entitlements.go, scope.go}
- field `queryState` lines 351-351
- function `stateCall` lines 355-358: used in internal/regogen/entitlements_test.go
- function `callState` lines 362-372: used in internal/regogen/scope.go
- function `noteFailed` lines 378-386
- function `remoteRefused` lines 392-407
- function `substituteAttr` lines 412-417
- function `mapAttrPlaceholders` lines 424-441
- function `placeholderValue` lines 447-502
- function `resourcePlaceholder` lines 507-519
- function `jsonTerm` lines 522-547
- field `PIPRecordDecl` lines 550-555
- function `pipRecordFunction` lines 557-577: used in internal/regogen/{jsonpath.go, pipcall_test.go}
- function `pipOptions` lines 582-600
- function `pipResolve` lines 607-662: used in internal/regogen/filtersub.go
- function `dedupe` lines 667-686: used in internal/regogen/{filtersub.go, local.go}

## internal/regogen/pipreplay.go (+192)

Added: 1-192

- function `ReplayTransport` lines 45-91: used in internal/regogen/{gen_test.go, pipcall_test.go}
- struct `replayAnswer` lines 93-97
- delegate `replay` lines 99-99
- function `replayKey` lines 129-135
- function `pipAnswer` lines 140-192: used in components/authz-agent/internal/snapshot/deep_test.go; internal/regogen/filtersub_test.go
- method `RoundTrip` lines 101-127: 1 calls sb did not attribute

## internal/regogen/project.go (+1011)

Added: 1-1011

- struct `Resolved` lines 36-43
- struct `Request` lines 49-77
- struct `Scope` lines 81-91
- struct `Record` lines 96-998: 6 calls sb did not attribute
- struct `Input` lines 157-1011: used in components/authz-agent/internal/snapshot/{decide.go, filter.go}; internal/policyir/key.go; internal/regobuiltins/httpsend.go; internal/regogen/{bulk.go, bulk_test.go, entitlements_test.go, filtersub_test.go, gen_test.go, metamorphic_test.go, pipcall_test.go, placement_test.go} and 2 more
- function `class` lines 193-211
- field `errIndexTooBig` lines 216-218
- function `fromRequest` lines 227-236: used in internal/regogen/project_test.go
- field `errOutsideDomain` lines 243-243
- struct `kindState` lines 246-249
- field `knownOutsideDomain` lines 256-256
- function `inDomain` lines 261-267
- function `record` lines 272-282: 1 calls sb did not attribute
- struct `pathKey` lines 301-304
- function `sourceRecord` lines 339-345
- function `projectRecord` lines 350-358: used in internal/regogen/bulk.go
- function `pathRecord` lines 364-370: used in internal/regogen/jsonpath.go
- function `buildRecord` lines 372-462
- function `literalRecord` lines 468-494: used in internal/regogen/leaf.go
- function `Project` lines 535-610: used in components/authz-agent/internal/snapshot/{decide.go, filter.go}; internal/regogen/{bulk.go, bulk_test.go, entitlements_test.go, filtersub_test.go, gen_test.go, metamorphic_test.go, pipcall_test.go, placement_test.go, scaling_test.go}
- function `strTerm` lines 646-646: used in internal/regogen/{bulk.go, bulk_test.go, pipreplay.go}
- function `strsTerm` lines 648-654: used in internal/regogen/deep.go
- function `keysTerm` lines 659-665
- function `fieldMaps` lines 778-784
- field `fieldState` lines 790-790
- field `fieldClass` lines 791-791
- field `fieldKey` lines 792-792
- field `fieldValueKey` lines 793-793
- field `fieldMatchKey` lines 794-794
- field `fieldElementKeys` lines 795-795
- field `fieldElementOwnKeys` lines 796-796
- field `fieldText` lines 797-797
- field `fieldSegments` lines 798-798
- field `fieldSegmentsFromEnd` lines 799-799
- field `fieldSegmentCount` lines 800-800
- field `fieldHasNull` lines 801-801
- field `fieldTextKey` lines 802-802
- field `fieldEqAlts` lines 803-803
- field `fieldEqIndex` lines 804-804
- field `fieldLength` lines 805-805
- field `fieldElementAlts` lines 806-806
- field `fieldElementIndex` lines 807-807
- field `fieldNumber` lines 808-808
- field `fieldSubsetIndex` lines 809-809
- field `fieldBeyondDouble` lines 810-810
- field `memberFoldedRoles` lines 815-815
- field `memberM2M` lines 816-816
- field `memberSubjectGroups` lines 817-817
- field `memberScopePasses` lines 818-818
- field `memberScopeFailed` lines 819-819
- field `memberResource` lines 820-820
- field `memberPIPRequests` lines 821-821
- field `recordFields` lines 825-828
- delegate `fieldSet` lines 831-831
- field `fieldsKnown` lines 834-834
- function `fieldBit` lines 836-842: used in internal/regogen/{gen.go, leaf.go, project_test.go, template.go}
- field `fieldReadRE` lines 865-865
- function `markEmitted` lines 870-891: used in internal/regogen/{filter.go, gen.go, project_test.go}
- function `fieldObjects` lines 910-922: used in internal/regogen/bulk.go
- method `Placeholders` lines 644-644
- method `has` lines 846-856: 2 calls sb did not attribute
- method `reads` lines 860-860
- method `parts` lines 895-907

## internal/regogen/rel.go (+182)

Added: 1-182

- field `relText` lines 31-32
- field `relFlip` lines 35-36
- function `orderKey` lines 46-59: used in internal/regogen/project.go
- function `jsonNumber` lines 61-61
- function `literalNumber` lines 67-78: used in internal/regogen/operand.go
- function `isIntegerLiteral` lines 80-83
- function `relTemplate` lines 88-140: used in internal/regogen/template.go
- field `relComplement` lines 144-145
- function `relTest` lines 149-162
- function `relHolds` lines 166-182: used in internal/regogen/groups.go

## internal/regogen/report.go (+126)

Added: 1-126

- struct `LeafReport` lines 32-52
- struct `CellReport` lines 55-64
- struct `whereNow` lines 68-74
- function `reportCells` lines 91-103: used in internal/regogen/leaf.go
- function `opText` lines 106-117
- function `ruleNames` lines 120-126: used in internal/regogen/leaf.go
- method `reportLeaf` lines 77-87: used in internal/regogen/leaf.go

## internal/regogen/request.go (+199)

Added: 1-199

- struct `Body` lines 30-138: 12 calls sb did not attribute
- function `ReadBody` lines 43-53: used in internal/regogen/{bulk_test.go, request_test.go, scaling_test.go}
- function `BodyOf` lines 57-66
- function `empty` lines 71-85
- function `resourceOperand` lines 102-110: used in internal/regogen/bulk.go
- function `selection` lines 148-175: used in internal/regogen/{jsonpath.go, pipcall.go, project.go}
- method `Resolve` lines 92-98: used in components/authz-agent/internal/snapshot/decide.go; internal/regogen/{bulk_test.go, entitlements_test.go, gen_test.go, request_test.go, scaling_test.go}
- method `compileResourcePath` lines 181-199: used in internal/regogen/operand.go

## internal/regogen/rsql.go (+351)

Added: 1-351

- field `errRSQL` lines 40-40
- field `rsqlNegOp` lines 42-43
- field `rsqlDefaultOps` lines 45-46
- struct `rsqlToken` lines 48-48
- field `rsqlUnreserved` lines 51-51
- field `rsqlFIQL` lines 52-52
- field `rsqlAlt` lines 53-53
- function `rsqlQuoted` lines 56-67
- function `rsqlTokens` lines 69-123: used in internal/regogen/filtertext.go
- struct `rsqlNode` lines 127-332: 19 calls sb did not attribute
- struct `rsqlParser` lines 139-255: used in test/svt/scripts/{build-mixed-flow-seeds.py, build-per-scenario-jmx.py, build-per-scenario-seeds.py}; 8 calls sb did not attribute
- function `parseRSQL` lines 257-271
- function `negateRSQL` lines 339-351: used in internal/regogen/{filtertext.go, rsql_test.go}

## internal/regogen/scope.go (+222)

Added: 1-222

- field `ScopePIP` lines 32-32
- function `scopeKey` lines 95-101
- function `scopeAnswer` lines 106-178
- function `firstTruthy` lines 182-189
- function `pyIndex` lines 193-199
- function `pyIter` lines 204-222
- method `ReadScope` lines 54-91: used in components/authz-agent/internal/snapshot/subject.go; internal/regogen/{pipresponse_test.go, scope_test.go}

## internal/regogen/spectables/doc.go (+124)

Added: 1-124


## internal/regogen/spectables/load.go (+813)

Added: 1-813

- field `SchemaVersion` lines 28-28
- field `maxProblems` lines 31-31
- field `ErrInvalid` lines 37-37
- field `ErrIncomplete` lines 41-41
- field `ErrNotCovered` lines 43-43
- struct `Table` lines 48-712: used in internal/regogen/{domain_test.go, filtersub_test.go, gen.go, leaf.go, operand.go}; internal/regogen/spectables/load_test.go; 13 calls sb did not attribute
- struct `combo` lines 62-72: 106 calls sb did not attribute
- struct `line` lines 78-81
- struct `contextFilter` lines 85-378: 27 calls sb did not attribute
- struct `tableJSON` lines 92-103
- function `Load` lines 108-180: 36 calls sb did not attribute
- function `isCode` lines 248-250
- function `readGrid` lines 312-338
- function `checkLeaf` lines 382-396
- function `checkAliases` lines 401-412
- function `sameCell` lines 495-497
- function `mirrorOutcome` lines 499-508
- function `checkDomain` lines 540-557
- function `checkResult` lines 562-580
- function `checkValueOutcomes` lines 582-592
- function `checkValueRule` lines 596-612
- function `checkNodes` lines 616-669
- function `combos` lines 716-735
- function `describePoint` lines 737-745
- function `describeContext` lines 747-750
- function `describeSide` lines 752-757
- function `points` lines 762-774
- function `allContexts` lines 776-788
- struct `problems` lines 791-813: 17 calls sb did not attribute

## internal/regogen/spectables/types.go (+460)

Added: 1-460

- delegate `Operator` lines 21-21
- field `OpEQ` lines 25-25
- field `OpNE` lines 26-26
- field `OpLT` lines 27-27
- field `OpLE` lines 28-28
- field `OpGT` lines 29-29
- field `OpGE` lines 30-30
- field `OpIsNull` lines 31-31
- field `OpIsNotNull` lines 32-32
- field `OpIsEmpty` lines 33-33
- field `OpIsNotEmpty` lines 34-34
- field `OpIn` lines 35-35
- field `OpNotIn` lines 36-36
- field `OpContains` lines 37-37
- field `OpNotContains` lines 38-38
- field `OpContainsAny` lines 39-39
- field `OpNotContainsAny` lines 40-40
- field `OpIsSubset` lines 41-41
- field `OpIsNotSubset` lines 42-42
- field `OpMatch` lines 43-43
- field `OpNotMatch` lines 44-44
- field `Operators` lines 48-52
- field `Negations` lines 69-72
- delegate `Kind` lines 77-77
- field `KindOperation` lines 81-81
- field `KindResourceType` lines 82-82
- field `KindResource` lines 87-87
- field `KindResPath` lines 88-88
- field `KindResNested` lines 89-89
- field `KindResJSONPath` lines 90-90
- field `KindSubjID` lines 92-92
- field `KindSubjName` lines 93-93
- field `KindSubjType` lines 94-94
- field `KindSubjServiceAccount` lines 95-95
- field `KindSubjRoles` lines 96-96
- field `KindSubjScopes` lines 97-97
- field `KindSubjPermissions` lines 98-98
- field `KindSubjPermissionScope` lines 99-99
- field `KindSubjIsM2M` lines 100-100
- field `KindPIPToken` lines 102-102
- field `KindPIPHeader` lines 103-103
- field `KindPIPGeneral` lines 104-104
- field `KindPIPFiltered` lines 105-105
- field `KindPIPMapping` lines 106-106
- field `KindEntitled` lines 109-109
- field `KindLitStr` lines 111-111
- field `KindLitNum` lines 112-112
- field `KindLitBool` lines 113-113
- field `KindNull` lines 114-114
- field `KindListStr1` lines 117-117
- field `KindListStrN` lines 118-118
- field `KindListNum1` lines 119-119
- field `KindListNumN` lines 120-120
- field `KindPattern` lines 124-124
- field `Kinds` lines 129-139
- delegate `State` lines 143-143
- field `StateValue` lines 147-147
- field `StateAbsent` lines 148-148
- field `StateNull` lines 149-149
- field `StatePIPEmpty` lines 150-150
- field `StateEmptyColl` lines 151-151
- field `StateEmptySel` lines 152-152
- field `StateIndexOOB` lines 153-153
- field `StatePIPNull` lines 154-154
- field `StateError` lines 155-155
- field `StateSingleOdd` lines 156-156
- field `StateScalarOdd` lines 157-157
- field `StateScopeOutside` lines 158-158
- field `States` lines 162-165
- delegate `Class` lines 168-168
- field `ClassString` lines 173-173
- field `ClassScalar` lines 175-175
- field `ClassList` lines 177-177
- field `ClassPIPList` lines 181-181
- field `ClassNullElement` lines 183-183
- field `ClassNested` lines 186-186
- field `ClassObject` lines 188-188
- field `ClassNull` lines 191-191
- field `Classes` lines 195-196
- delegate `ValueRule` lines 200-200
- field `RuleEq` lines 206-206
- field `RuleListEq` lines 208-208
- field `RuleStructureTextLeft` lines 211-211
- field `RuleArrayEq` lines 214-214
- field `RuleObjectEq` lines 216-216
- field `RuleRel` lines 218-218
- field `RuleEmpty` lines 220-220
- field `RuleInAny` lines 222-222
- field `RuleContainsAny` lines 224-224
- field `RuleContainsRightAttributeList` lines 227-227
- field `RuleSubset` lines 229-229
- field `RuleMatch` lines 231-231
- field `RuleNullElementEnds` lines 234-234
- field `RuleRightListScalarOps` lines 237-237
- field `RuleSingleOdd` lines 240-240
- field `RuleScalarOddRel` lines 245-245
- field `ValueRules` lines 249-251
- delegate `NodeOutcome` lines 254-254
- field `NodePermit` lines 258-258
- field `NodeDeny` lines 259-259
- field `NodeNotApplicable` lines 260-260
- field `NodeOutcomes` lines 264-264
- field `Algorithms` lines 267-267
- field `RuleEffects` lines 271-271
- field `AbsentEffects` lines 275-275
- struct `Combination` lines 279-284
- struct `Nodes` lines 288-301
- delegate `Place` lines 304-304
- field `PlaceSimplified` lines 308-308
- field `PlaceRuleCondition` lines 309-309
- field `PlaceRuleTarget` lines 310-310
- field `PlacePolicyTarget` lines 311-311
- field `PlaceSetTarget` lines 312-312
- field `Places` lines 316-316
- delegate `Effect` lines 319-319
- field `EffectAllow` lines 323-323
- field `EffectDeny` lines 324-324
- field `Effects` lines 328-328
- delegate `Profile` lines 333-333
- field `ProfileLegacy` lines 338-338
- field `ProfileAgent` lines 341-341
- delegate `Outcome` lines 345-345
- field `OutcomeT` lines 350-350
- field `OutcomeF` lines 352-352
- field `OutcomeU` lines 355-355
- field `OutcomeAbort` lines 357-357
- field `OutcomeErr` lines 359-359
- field `OutcomeBadRequest` lines 361-361
- field `OutcomeUnsupported` lines 363-363
- field `OutcomeByValue` lines 366-366
- function `Outcomes` lines 371-380: used in internal/regogen/spectables/{load.go, schema_test.go}
- function `valueOutcomes` lines 383-388: used in internal/regogen/spectables/{load.go, schema_test.go}
- field `RequiredKnobs` lines 402-403
- struct `Domain` lines 407-410
- struct `Point` lines 414-418
- struct `Context` lines 421-426
- struct `Key` lines 430-434
- struct `Cell` lines 437-445
- function `admitsRight` lines 447-452: used in internal/regogen/spectables/load.go
- function `admitsLeft` lines 454-456: used in internal/regogen/spectables/load.go
- function `known` lines 458-460: used in internal/jsonvalue/value.go; internal/regogen/spectables/load.go
- method `Unary` lines 55-62: 8 calls sb did not attribute

## internal/regogen/subject.go (+260)

Added: 1-260

- delegate `ServiceIDClaim` lines 27-27
- field `ServiceIDSame` lines 32-32
- field `ServiceIDClientID` lines 34-34
- field `ServiceIDAzp` lines 36-36
- field `ServiceIDClientIDEmpty` lines 39-39
- delegate `AnonymousID` lines 43-43
- field `AnonymousIDToken` lines 49-49
- field `AnonymousIDSub` lines 51-51
- field `AnonymousIDNull` lines 53-53
- struct `SubjectRules` lines 58-63
- field `DefaultSubjectRules` lines 66-66
- field `serviceAccountPrefix` lines 69-69
- field `keySubjID` lines 73-73
- field `keySubjName` lines 74-74
- field `keySubjType` lines 75-75
- field `keySubjServiceAccount` lines 76-76
- field `keySubjScopes` lines 77-77
- field `keySubjRoles` lines 78-78
- struct `Subject` lines 82-147: used in components/authz-agent/internal/snapshot/{decide.go, filter.go, subject.go}; internal/regogen/{bulk_test.go, mapping_test.go, scaling_test.go}
- function `SubjectOf` lines 109-136: used in components/authz-agent/internal/snapshot/subject.go; internal/regogen/{bulk_test.go, mapping_test.go, scaling_test.go, subject_test.go}
- struct `token` lines 149-243: used in components/authz-agent/internal/snapshot/deep_test.go; internal/regogen/pipcall.go; 1 calls sb did not attribute
- function `isPySpace` lines 219-226
- function `roleText` lines 248-260: used in internal/regogen/entitlements.go

## internal/regogen/subset.go (+127)

Added: 1-127

- function `subsetTemplate` lines 32-70: used in internal/regogen/template.go
- function `subsetTest` lines 75-93
- method `subsetHolds` lines 97-127: used in internal/regogen/groups.go

## internal/regogen/tables.go (+36)

Added: 1-36

- field `agentTables` lines 29-29
- field `defaultTable` lines 31-33
- function `DefaultTable` lines 36-36: used in components/authz-agent/cmd/filter-corpus/main.go; components/authz-agent/cmd/snapshot-corpus/main.go; components/authz-agent/internal/server/public_test.go; components/authz-agent/internal/snapshot/registry_test.go; components/authz-agent/main.go; components/authz-policy-admin/totality_test.go; internal/regogen/gen_test.go

## internal/regogen/template.go (+774)

Added: 1-774

- struct `tpl` lines 31-58
- function `fieldOf` lines 66-80
- function `isStructureOrList` lines 83-85
- function `isListClass` lines 88-91: used in internal/regogen/leaf.go
- function `isStructure` lines 95-97
- function `lit` lines 99-102: used in internal/regogen/{entitlements.go, gen.go, groups.go, jsonpath.go, leaf.go, operand.go, pipcall.go}
- function `setLit` lines 104-116: used in internal/regogen/leaf.go
- struct `tb` lines 118-756: used in internal/regogen/subset.go; 3 calls sb did not attribute
- function `vfact` lines 152-157: used in internal/regogen/{leaf.go, rel.go}
- function `isScalar` lines 159-161: used in internal/regogen/project.go
- function `isRes` lines 163-166: used in internal/regogen/leaf.go
- field `negated` lines 170-174
- function `template` lines 180-223: used in internal/regogen/{gen_test.go, leaf.go}
- function `hasNull` lines 226-228: used in internal/regogen/leaf.go
- function `valueTemplate` lines 230-584
- function `matchRegex` lines 587-589: used in internal/regogen/leaf.go
- function `segmentGuards` lines 597-642
- function `refTest` lines 646-652: used in internal/regogen/{leaf.go, rel.go}
- function `ownFields` lines 721-726
- function `scalarField` lines 730-735
- function `rightTest` lines 761-766
- function `pairTest` lines 769-774: used in internal/regogen/rel.go

## internal/token/keys/keys.go (+1)

Added: 128

- field `DefaultHTTPTimeout` lines 42-42
- field `DefaultStartupTimeout` lines 43-43
- field `DefaultRefreshInterval` lines 44-44
- field `defaultFirstRetryDelay` lines 50-50
- field `maxRetryDelay` lines 51-51
- interface `Logger` lines 55-58: 21 calls sb did not attribute
- struct `Options` lines 62-95
- struct `discard` lines 97-105: 21 calls sb did not attribute
- struct `Key` lines 108-134: 12 calls sb did not attribute
- function `AcceptsAlgorithm` lines 140-143
- struct `Set` lines 147-321: 503 calls sb did not attribute
- struct `snapshot` lines 158-161: used in components/authz-agent/cmd/filter-corpus/main.go; components/authz-agent/cmd/snapshot-corpus/main.go; components/authz-agent/internal/corpus/subject.go; components/authz-agent/internal/server/{decide.go, public_test.go}; components/authz-agent/{main.go, main_test.go}
- function `Load` lines 170-206: 36 calls sb did not attribute
- function `sameKIDs` lines 323-333

## policies/authorize_internals.rego (+31)

Added: 40-59, 64, 70-71, 73, 76-78, 80-83


## tools/ruleguard/rules.go (+133)

Added: 1-133

- function `recordOutsideItsConstructor` lines 30-41
- function `textAsIdentity` lines 49-106
- function `discardedResponse` lines 111-118
- function `pathTextOutsideJSONPath` lines 124-133

## Tests

- components/authz-agent/cmd/snapshot-corpus/main_test.go (+46), added 1-46: uses declarations of components/authz-agent/internal/snapshot/subject.go
- components/authz-agent/config_test.go (+126), added 18-19, 26, 29-38, 51, 55, 58, 68, 83, 97, 111-193, 195-218: uses declarations of components/authz-agent/config.go
- components/authz-agent/internal/corpus/subject_test.go (+62), added 1-62: uses declarations of components/authz-agent/internal/corpus/subject.go
- components/authz-agent/internal/engine/engine_test.go (+7), added 19, 98-99, 109, 111, 113-114: uses declarations of components/authz-agent/internal/engine/engine.go
- components/authz-agent/internal/legacy/legacy_test.go (+126), added 19, 22-23, 26-34, 51-53, 57-63, 68-76, 78, 86, 114-118, 142-143, 150, 154-155, 157-158, 160-161, 174-175, 177-183, 186-187, 213-215, 217-218, 242-244, 246-251, 269, 271-274, 278, 298-299, 305, 311, 317, 323, 329, 334, 459-470, 473-476, 478-500, 502: uses declarations of components/authz-agent/internal/legacy/legacy.go; internal/jsonvalue/value.go
- components/authz-agent/internal/m2m/m2m_test.go (+153), added 33-37, 40-48, 56-82, 106, 121, 131-132, 150, 155-156, 172, 178, 181-182, 188, 200, 208-209, 234, 242-243, 360-361, 367-368, 373, 377, 382-383, 385-386, 421-504: uses declarations of components/authz-agent/internal/m2m/m2m.go; internal/jsonvalue/decimal.go
- components/authz-agent/internal/panics/panics_test.go (+89), added 1-89
- components/authz-agent/internal/pull/pull_test.go (+306), added 19, 24, 32, 52, 62-67, 70-74, 77-80, 85-86, 96-97, 122-128, 179-180, 183-184, 190-191, 196-199, 210, 227-229, 231-237, 242, 247-248, 251-252, 260-285, 293, 315-317, 322-323, 329-331, 333-340, 342-343, 347, 350-351, 375-376, 385, 399-400, 404, 406-408, 410, 412, 414, 417, 424-472, 476-615: uses declarations of components/authz-agent/internal/pull/pull.go
- components/authz-agent/internal/server/cost_test.go (+162), added 1-162: uses declarations of internal/jsonvalue/value.go
- components/authz-agent/internal/server/decide_test.go (+512), added 1-512
- components/authz-agent/internal/server/deep_test.go (+85), added 1-85
- components/authz-agent/internal/server/public_test.go (+169), added 33-34, 37-44, 46-51, 53-60, 62-67, 69-71, 73-81, 104-107, 109-134, 150-153, 189, 193, 210, 238, 313-314, 356, 358-367, 384-385, 388-389, 400-401, 445-478, 486, 491-525: uses declarations of components/authz-agent/internal/engine/engine.go; components/authz-agent/internal/server/{public.go, server.go}; components/authz-agent/internal/snapshot/subject.go; internal/jsonvalue/value.go; internal/legacyvalue/record.go; internal/regobuiltins/builtins.go; internal/regogen/tables.go; internal/token/keys/keys.go
- components/authz-agent/internal/server/server_test.go (+134), added 25, 29, 35, 39, 88, 124-155, 168-170, 250-252, 255, 264-265, 272-275, 279, 281, 284-287, 291, 295, 300-301, 303-333, 337-379: uses declarations of components/authz-agent/internal/engine/engine.go; components/authz-agent/internal/server/{public.go, server.go}; components/authz-agent/internal/snapshot/subject.go; internal/jsonvalue/value.go
- components/authz-agent/internal/server/specconform_test.go (+289), added 1-289: uses declarations of components/authz-agent/internal/engine/engine.go; internal/jsonvalue/value.go; internal/policyir/tree.go; internal/regogen/gen.go
- components/authz-agent/internal/snapshot/deep_test.go (+439), added 1-439: uses declarations of components/authz-agent/internal/snapshot/decide.go; internal/policyir/parse.go; internal/regogen/{pipreplay.go, subject.go}
- components/authz-agent/internal/snapshot/failedrail_test.go (+195), added 1-195
- components/authz-agent/internal/snapshot/filter_test.go (+1019), added 1-1019: uses declarations of internal/jsonvalue/value.go; internal/regogen/leaf.go
- components/authz-agent/internal/snapshot/known_violations_test.go (+41), added 1-41
- components/authz-agent/internal/snapshot/metrics_test.go (+43), added 1-43: uses declarations of components/authz-agent/internal/snapshot/metrics.go
- components/authz-agent/internal/snapshot/registry_test.go (+1782), added 1-1782: uses declarations of components/authz-agent/cmd/filter-corpus/main.go; components/authz-agent/cmd/snapshot-corpus/main.go; components/authz-agent/internal/snapshot/{decide.go, health.go, registry.go}; internal/jsonvalue/value.go; internal/policyir/export.go; internal/regobuiltins/httpsend.go; internal/regogen/tables.go
- components/authz-agent/internal/snapshot/subject_test.go (+93), added 1-93: uses declarations of components/authz-agent/internal/snapshot/subject.go
- components/authz-agent/internal/snapshot/treekey_test.go (+135), added 1-135
- components/authz-agent/main_test.go (+44), added 23, 26, 37, 48, 55-83, 86-89, 93-94, 98, 108, 111-113: uses declarations of components/authz-agent/internal/panics/panics.go; components/authz-agent/internal/pull/pull.go; components/authz-agent/{main.go, tenant.go}; internal/token/keys/keys.go
- components/authz-agent/settings_drift_test.go (+330), added 1-330: uses declarations of components/authz-agent/config.go
- components/authz-agent/tenant_test.go (+328), added 1-328: uses declarations of components/authz-agent/tenant.go
- components/authz-policy-admin/convert_test.go (+191), added 19-21, 24, 27-41, 43-62, 64-66, 68, 75-77, 79-104, 106, 108-123, 127-130, 132-133, 135-139, 145-206, 208, 210-215, 217-223, 227-240, 242: uses declarations of components/authz-policy-admin/convert.go; internal/policyir/{dump.go, export.go}
- components/authz-policy-admin/main_test.go (+35), added 84, 140, 242, 246, 272-302
- components/authz-policy-admin/store_test.go (+433), added 18, 20, 22, 40-43, 50-57, 66-68, 70-87, 90-92, 105-106, 110, 112, 120, 130-180, 185, 187, 201-203, 211, 230, 234, 240, 251, 254, 260, 275, 283, 288, 290, 305, 313, 329, 342, 364, 408, 416, 455, 464, 481, 508, 510, 520-522, 528-530, 537-839, 843: uses declarations of components/authz-agent/internal/legacy/legacy.go; components/authz-agent/internal/snapshot/subject.go; components/authz-policy-admin/{handlers.go, store.go}; internal/jsonvalue/value.go
- components/authz-policy-admin/totality_test.go (+730), added 1-730: uses declarations of components/authz-policy-admin/{handlers.go, store.go}; internal/policyir/export.go; internal/regobuiltins/httpsend.go; internal/regogen/{filter.go, gen.go, tables.go}
- components/authz-policy-admin/validate_test.go (+459), added 1-459
- internal/costcheck/subprocess_test.go (+109), added 1-109: uses declarations of internal/costcheck/subprocess.go
- internal/jsonpath/jayway_test.go (+5), added 257-261: uses declarations of internal/jsonvalue/{decimal.go, value.go}; internal/legacyvalue/javatext.go
- internal/jsonpath/jsonpath_test.go (+111), added 381, 391-427, 625-652, 760-804: uses declarations of internal/jsonpath/{filter.go, jsonpath.go}; internal/jsonvalue/value.go
- internal/jsonpath/rootkey_test.go (+74), added 1-74: uses declarations of internal/jsonvalue/value.go
- internal/jsonvalue/decimal_test.go (+20), added 131-150: uses declarations of internal/jsonvalue/decimal.go
- internal/jsonvalue/encode_test.go (+67), added 1-67: uses declarations of internal/jsonvalue/encode.go
- internal/jsonvalue/value_test.go (+14), added 85-98: uses declarations of internal/jsonvalue/value.go
- internal/legacyvalue/record_test.go (+74), added 20, 129-131, 143-144, 147, 172-175, 178-185, 201-255: uses declarations of internal/jsonvalue/{decimal.go, value.go}; internal/legacyvalue/record.go
- internal/legacyvalue/structuretext_test.go (+66), added 1-66: uses declarations of internal/jsonvalue/value.go; internal/legacyvalue/structuretext.go
- internal/policyir/cond_test.go (+6), added 54, 76-80: uses declarations of internal/policyir/{cond.go, dump.go}
- internal/policyir/dump_test.go (+48), added 21-24, 67, 90-96, 113, 151-185: uses declarations of internal/policyir/tree.go
- internal/policyir/export_test.go (+572), added 200-269, 381, 386-515, 559, 570-573, 578, 597-622, 632, 643-839, 855, 888-889, 905, 1020, 1078, 1122, 1152-1267, 1328-1333, 1373, 1525-1534, 1536: uses declarations of internal/policyir/{export.go, tree.go, unsupported.go}
- internal/policyir/key_test.go (+287), added 1-287: uses declarations of internal/jsonvalue/value.go; internal/policyir/key.go
- internal/policyir/parse_test.go (+113), added 35-45, 50, 59-80, 82, 142-145, 156-157, 160, 167-169, 173, 194, 197, 201-202, 204-208, 217, 222-223, 226, 230-233, 235-280, 351-352, 354-355: uses declarations of internal/policyir/{dump.go, parse.go}
- internal/policyir/pattern_test.go (+78), added 1-78: uses declarations of internal/policyir/pattern.go
- internal/policyir/tree_test.go (+2), added 137-138: uses declarations of internal/policyir/tree.go
- internal/policyir/unsupported_test.go (+37), added 42, 46, 57-58, 87-119: uses declarations of internal/policyir/tree.go
- internal/regobuiltins/httpsend_test.go (+666), added 1-666: uses declarations of components/authz-agent/internal/engine/engine.go; internal/regobuiltins/{builtins.go, httpsend.go}
- internal/regogen/bulk_test.go (+344), added 1-344: uses declarations of components/authz-agent/internal/engine/engine.go; internal/regogen/{bulk.go, gen.go, project.go, request.go, subject.go}
- internal/regogen/domain_test.go (+121), added 1-121: uses declarations of internal/regogen/gen.go; internal/regogen/spectables/load.go
- internal/regogen/entitlements_test.go (+309), added 1-309: uses declarations of components/authz-agent/internal/engine/engine.go; internal/regobuiltins/{builtins.go, httpsend.go}; internal/regogen/{bulk.go, entitlements.go, gen.go, local.go, pipcall.go, project.go, request.go}
- internal/regogen/filterdialect_test.go (+527), added 1-527: uses declarations of internal/jsonvalue/value.go
- internal/regogen/filterformula_test.go (+718), added 1-718
- internal/regogen/filtersub_test.go (+651), added 1-651: uses declarations of components/authz-agent/internal/engine/engine.go; internal/jsonvalue/{encode.go, value.go}; internal/policyir/{export.go, parse.go}; internal/regobuiltins/{builtins.go, httpsend.go}; internal/regogen/{filter.go, filtersub.go, gen.go, local.go, operand.go} and 3 more
- internal/regogen/filtertext_test.go (+193), added 1-193: uses declarations of internal/regogen/filtertext.go
- internal/regogen/filtertextmeaning_test.go (+449), added 1-449: uses declarations of internal/regogen/{filtertext.go, operand.go}
- internal/regogen/filterveto_test.go (+164), added 1-164: uses declarations of internal/policyir/export.go; internal/regogen/{filter.go, gen.go}
- internal/regogen/gen_test.go (+4346), added 1-4346: uses declarations of components/authz-agent/internal/engine/engine.go; components/authz-agent/internal/snapshot/metrics.go; internal/policyir/{export.go, tree.go}; internal/regobuiltins/{builtins.go, httpsend.go}; internal/regogen/{comment.go, gen.go, groups.go, jsonpath.go, pipreplay.go, project.go} and 3 more
- internal/regogen/jsonkey_test.go (+93), added 1-93
- internal/regogen/local_test.go (+163), added 1-163: uses declarations of internal/regogen/{gen.go, local.go}
- internal/regogen/mapping_test.go (+172), added 1-172: uses declarations of internal/regogen/{gen.go, local.go, subject.go}
- internal/regogen/metamorphic_test.go (+495), added 1-495: uses declarations of components/authz-agent/internal/engine/engine.go; internal/jsonpath/jsonpath.go; internal/regogen/{filter.go, gen.go, project.go}
- internal/regogen/pipcall_test.go (+677), added 1-677: uses declarations of components/authz-agent/internal/engine/engine.go; internal/regobuiltins/{builtins.go, httpsend.go}; internal/regogen/{gen.go, jsonpath.go, pipcall.go, pipreplay.go, project.go}
- internal/regogen/pipresponse_test.go (+503), added 1-503: uses declarations of internal/jsonvalue/encode.go; internal/legacyvalue/javatext.go; internal/regobuiltins/{builtins.go, httpsend.go}; internal/regogen/{entitlements.go, scope.go}
- internal/regogen/placement_test.go (+353), added 1-353: uses declarations of components/authz-agent/internal/engine/engine.go; internal/policyir/{cond.go, export.go, parse.go, tree.go}; internal/regogen/{filter.go, gen.go, project.go}
- internal/regogen/project_test.go (+388), added 1-388: uses declarations of internal/regogen/{deep.go, gen.go, operand.go, project.go}
- internal/regogen/request_test.go (+187), added 1-187: uses declarations of internal/regogen/{gen.go, operand.go, request.go}
- internal/regogen/rootkey_test.go (+130), added 1-130
- internal/regogen/rsql_test.go (+65), added 1-65: uses declarations of internal/regogen/rsql.go
- internal/regogen/scaling_test.go (+654), added 1-654: uses declarations of components/authz-agent/internal/engine/engine.go; internal/policyir/export.go; internal/regogen/{filter.go, gen.go, project.go, request.go, subject.go}
- internal/regogen/scope_test.go (+204), added 1-204: uses declarations of internal/regobuiltins/{builtins.go, httpsend.go}; internal/regogen/{gen.go, scope.go}
- internal/regogen/spectables/load_test.go (+951), added 1-951: uses declarations of internal/regogen/leaf.go; internal/regogen/spectables/load.go
- internal/regogen/spectables/schema_test.go (+87), added 1-87: uses declarations of internal/regogen/spectables/types.go
- internal/regogen/subject_test.go (+181), added 1-181: uses declarations of internal/regogen/{gen.go, subject.go}
- internal/regogen/treegen_test.go (+507), added 1-507
- policies/admission_test.rego (+70), added 1-70
- policies/embed_test.go (+2), added 22, 29
- policies/token_auth_contract_test.rego (+40), added 25, 28, 32, 70, 74, 141, 144, 149-150, 156, 159, 164-165, 174, 177, 182, 188, 191, 196-197, 207, 211-212, 222, 231, 234, 237, 242, 251, 254, 259, 269, 272, 277, 394, 400, 404, 411, 417, 421
- policies/token_taxonomy_test.rego (+143), added 25, 27, 35-36, 43-44, 47-48, 51-53, 100-101, 108-109, 112-113, 117-118, 125-126, 129-130, 133-135, 140-142, 151-152, 159-160, 163-164, 171-172, 180-181, 184-185, 199-200, 203, 208-209, 212, 215, 217-218, 221, 253-254, 262-263, 266-267, 270, 272-273, 281-282, 285, 288, 290-292, 295, 303, 311, 315, 323, 326, 328, 330-331, 334, 337-339, 433-434, 442-443, 446-447, 450, 452-453, 515-516, 525-526, 529-530, 533, 537-538, 634-635, 643-644, 647-648, 651, 654-655, 673-674, 683-684, 687-688, 691, 695-696, 714-715, 724-725, 728-729, 732, 736-737, 755-756, 765-766, 769-770, 773, 777-778, 794-795, 803-804, 807-808, 811, 814-815
- test/integration/pipstub/main.go (+19), added 20-22, 79-85, 327-333, 513, 634: uses declarations of components/authz-agent/internal/engine/engine.go; components/authz-agent/internal/legacy/legacy.go; internal/jsonvalue/encode.go; internal/regobuiltins/httpsend.go
- test/integration/pipstub/main_test.go (+31), added 19, 24, 261-289: uses declarations of components/authz-agent/internal/legacy/legacy.go; components/authz-agent/internal/snapshot/subject.go; internal/regobuiltins/httpsend.go
- test/integration/testify/catalog.go (+5), added 60, 85, 94, 96, 158
- test/integration/testify/check_filter_test.go (+26), added 24, 33, 38-39, 42, 45, 47-48, 50-51, 57, 66, 73, 76-77, 81, 86, 88-90, 93-95, 107-108, 113
- test/integration/testify/check_resource_bulk_test.go (+15), added 30, 40, 47, 54, 64, 79, 91, 101, 110, 112, 125, 132, 138-139, 147
- test/integration/testify/check_resource_test.go (+44), added 26, 48, 61, 69, 74-76, 83-84, 100, 110, 121, 123, 131, 153, 159-162, 173-176, 186-187, 197, 205, 222, 237, 253, 258-262, 272, 279, 282-288
- test/integration/testify/entitlements_test.go (+36), added 65-67, 74-75, 95-122, 220-221, 224: uses declarations of internal/regogen/gen.go
- test/integration/testify/helpers.go (+1), added 246
- test/integration/testify/lockdown_test.go (+4), added 19-22
- test/integration/testify/m2m_keycloak_test.go (+2), added 52, 75
- test/integration/testify/pip_admin_test.go (+3), added 81, 188, 270
- test/integration/testify/route_security_test.go (+1), added 113
- test/integration/testify/wildcard_access_test.go (+8), added 46, 64, 76, 78, 80-81, 93, 105
- test/parity/suite/pip_control.go (+13), added 70, 114-119, 123, 134-136, 142, 153
- test/parity/suite/wire_v1.go (+1), added 138
- test/parity/suite/wire_v2.go (+1), added 101
- test/scripts/test-chart-render.sh (+46), added 329-334, 374-399, 516-527, 565-566
- test/scripts/token-testkit/refresh-rego-fixtures.sh (+0), removes 38 lines
- test/svt/common/scripts/lib/svt-lib.sh (+4), added 88-91
- test/svt/scripts/build-mixed-flow-seeds.py (+4), added 20-22, 178: uses declarations of internal/regogen/rsql.go
- test/svt/scripts/build-per-scenario-jmx.py (+2), added 32, 177: uses declarations of internal/regogen/rsql.go
- test/svt/scripts/build-per-scenario-seeds.py (+3), added 433, 488, 500: uses declarations of internal/regogen/rsql.go
- test/svt/scripts/mixed-load-report (+5), added 14-16, 278-279
- test/svt/scripts/per-scenario-decision-time (+2), added 392-393
- tools/ruleguard/rules_test.go (+33), added 1-33
- tools/ruleguard/testdata/go.mod (+3), added 1-3
- tools/ruleguard/testdata/internal/jsonpath/jsonpath.go (+8), added 1-8
- tools/ruleguard/testdata/internal/regogen/other.go (+65), added 1-65
- tools/ruleguard/testdata/internal/regogen/other_test.go (+20), added 1-20
- tools/ruleguard/testdata/internal/regogen/project.go (+13), added 1-13

## Deleted

- internal/acconfig/convert.go (code)
- internal/acconfig/convert_targets_test.go (tests)
- internal/acconfig/convert_test.go (tests)
- internal/acconfig/export_bundle_test.go (tests)
- internal/acconfig/testdata/export-bundle/elements.json (data)
- internal/acconfig/testdata/export-bundle/exports/match.json (data)
- internal/acconfig/testdata/export-bundle/exports/mistyped.json (data)
- internal/acconfig/testdata/export-bundle/exports/refused.json (data)
- internal/acconfig/testdata/export-bundle/exports/wrong-policies.json (data)
- internal/acconfig/testdata/export-bundle/exports/wrong-stats.json (data)
- internal/acconfig/testdata/generate_synthetic_fixture.py (tests)
- internal/acconfig/testdata/pipsV3_1.json (data)
- internal/acconfig/testdata/pipsV3_2.json (data)
- internal/acconfig/testdata/pipsV3_3.json (data)
- internal/acconfig/testdata/policy_setsV3_1.json (data)
- internal/acconfig/testdata/policy_setsV3_2.json (data)
- internal/acconfig/testdata/policy_setsV3_3.json (data)
- internal/acconfig/testdata/policy_setsV3_real_dev4.json (data)
- internal/acconfig/testdata/simplified_policies.json (data)
- internal/acconfig/types.go (code)
- internal/pips/activation.go (code)
- internal/pips/activation_from_policies_test.go (tests)
- internal/pips/activation_test.go (tests)
- internal/pips/contract.go (code)
- internal/pips/contract_test.go (tests)
- internal/pips/entitlements.go (code)
- internal/pips/entitlements_test.go (tests)
- internal/pips/normalize.go (code)
- internal/pips/normalize_test.go (tests)
- internal/pips/types.go (code)
- internal/pips/validate.go (code)
- internal/pips/validate_test.go (tests)
- internal/policyir/token.go (code)
- internal/policyir/token_test.go (tests)
- internal/simplifiedpolicies/entfixture_test.go (tests)
- internal/simplifiedpolicies/normalize.go (code)
- internal/simplifiedpolicies/normalize_test.go (tests)
- internal/simplifiedpolicies/parser.go (code)
- internal/simplifiedpolicies/parser_test.go (tests)
- policies/authorize.rego (code)
- policies/authorize_contract_test.rego (tests)
- policies/entitlements_test.rego (tests)
- policies/fixtures/authorize/canonical_multi_resource_order_preserved/golden.json (data)
- policies/fixtures/authorize/canonical_multi_resource_order_preserved/input.json (data)
- policies/fixtures/authorize/canonical_multi_resource_order_preserved/policies.json (data)
- policies/fixtures/authorize/canonical_multi_resource_order_preserved/simplified-policies.json (data)
- policies/fixtures/authorize/canonical_rls_default_true_when_omitted/golden.json (data)
- policies/fixtures/authorize/canonical_rls_default_true_when_omitted/input.json (data)
- policies/fixtures/authorize/canonical_rls_default_true_when_omitted/policies.json (data)
- policies/fixtures/authorize/canonical_rls_default_true_when_omitted/simplified-policies.json (data)
- policies/fixtures/authorize/canonical_rls_true_allow_with_predicate/golden.json (data)
- policies/fixtures/authorize/canonical_rls_true_allow_with_predicate/input.json (data)
- policies/fixtures/authorize/canonical_rls_true_allow_with_predicate/policies.json (data)
- policies/fixtures/authorize/canonical_rls_true_allow_with_predicate/simplified-policies.json (data)
- policies/fixtures/authorize/canonical_rls_true_ols_allow_but_rls_deny/golden.json (data)
- policies/fixtures/authorize/canonical_rls_true_ols_allow_but_rls_deny/input.json (data)
- policies/fixtures/authorize/canonical_rls_true_ols_allow_but_rls_deny/policies.json (data)
- policies/fixtures/authorize/canonical_rls_true_ols_allow_but_rls_deny/simplified-policies.json (data)
- policies/fixtures/authorize/canonical_rls_true_ols_deny_short_circuit/golden.json (data)
- policies/fixtures/authorize/canonical_rls_true_ols_deny_short_circuit/input.json (data)
- policies/fixtures/authorize/canonical_rls_true_ols_deny_short_circuit/policies.json (data)
- policies/fixtures/authorize/canonical_rls_true_ols_deny_short_circuit/simplified-policies.json (data)
- policies/fixtures/policy_language/cases.json (data)
- policies/fixtures/policy_language/tokens.json (data)
- policies/normalization_contract_test.rego (tests)
- policies/ols.rego (code)
- policies/pip.rego (code)
- policies/pip_m2m_injection_test.rego (tests)
- policies/pip_request_args_test.rego (tests)
- policies/pip_resolution_test.rego (tests)
- policies/policy_language_contract_test.rego (tests)
- policies/rls.rego (code)
- policies/rls_multisegment_test.rego (tests)
- policies/rls_pip_negation_test.rego (tests)
- policies/rls_predicate_aggregation_test.rego (tests)
- policies/wildcard_access_contract_test.rego (tests)
- test/parity/suite/test_row29_validation_missing_rt_test.go (tests)
- test/svt/profiler/keys/setup-real-token.py (tests)
- test/svt/profiler/keys/sign-jwt.py (tests)
- test/svt/profiler/ols-bulk-100/bench-real-token.sh (tests)
- test/svt/profiler/ols-bulk-100/bench.sh (tests)
- test/svt/profiler/ols-bulk-100/data.json (data)
- test/svt/profiler/ols-bulk-100/input.json (data)
- test/svt/profiler/ols-bulk-100/profile-real-token.sh (tests)
- test/svt/profiler/ols-bulk-100/profile-trace.sh (tests)
- test/svt/profiler/ols-bulk-100/profile.sh (tests)
- test/svt/profiler/ols-bulk-1000/bench-real-token.sh (tests)
- test/svt/profiler/ols-bulk-1000/bench.sh (tests)
- test/svt/profiler/ols-bulk-1000/data.json (data)
- test/svt/profiler/ols-bulk-1000/input.json (data)
- test/svt/profiler/ols-bulk-1000/profile-real-token.sh (tests)
- test/svt/profiler/ols-bulk-1000/profile-trace.sh (tests)
- test/svt/profiler/ols-bulk-1000/profile.sh (tests)
- test/svt/profiler/ols-bulk-50/bench-real-token.sh (tests)
- test/svt/profiler/ols-bulk-50/bench.sh (tests)
- test/svt/profiler/ols-bulk-50/data.json (data)
- test/svt/profiler/ols-bulk-50/input.json (data)
- test/svt/profiler/ols-bulk-50/profile-real-token.sh (tests)
- test/svt/profiler/ols-bulk-50/profile-trace.sh (tests)
- test/svt/profiler/ols-bulk-50/profile.sh (tests)
- test/svt/profiler/ols-single-100roles/bench-real-token.sh (tests)
- test/svt/profiler/ols-single-100roles/bench.sh (tests)
- test/svt/profiler/ols-single-100roles/data.json (data)
- test/svt/profiler/ols-single-100roles/input.json (data)
- test/svt/profiler/ols-single-100roles/profile-real-token.sh (tests)
- test/svt/profiler/ols-single-100roles/profile-trace.sh (tests)
- test/svt/profiler/ols-single-100roles/profile.sh (tests)
- test/svt/profiler/ols-single-10roles/bench-real-token.sh (tests)
- test/svt/profiler/ols-single-10roles/bench.sh (tests)
- test/svt/profiler/ols-single-10roles/data.json (data)
- test/svt/profiler/ols-single-10roles/input.json (data)
- test/svt/profiler/ols-single-10roles/profile-real-token.sh (tests)
- test/svt/profiler/ols-single-10roles/profile-trace.sh (tests)
- test/svt/profiler/ols-single-10roles/profile.sh (tests)
- test/svt/profiler/ols-single-20roles/bench-real-token.sh (tests)
- test/svt/profiler/ols-single-20roles/bench.sh (tests)
- test/svt/profiler/ols-single-20roles/data.json (data)
- test/svt/profiler/ols-single-20roles/input.json (data)
- test/svt/profiler/ols-single-20roles/profile-real-token.sh (tests)
- test/svt/profiler/ols-single-20roles/profile-trace.sh (tests)
- test/svt/profiler/ols-single-20roles/profile.sh (tests)
- test/svt/profiler/ols-single-30roles/bench-real-token.sh (tests)
- test/svt/profiler/ols-single-30roles/bench.sh (tests)
- test/svt/profiler/ols-single-30roles/data.json (data)
- test/svt/profiler/ols-single-30roles/input.json (data)
- test/svt/profiler/ols-single-30roles/profile-real-token.sh (tests)
- test/svt/profiler/ols-single-30roles/profile-trace.sh (tests)
- test/svt/profiler/ols-single-30roles/profile.sh (tests)
- test/svt/profiler/ols-single-50roles/bench-real-token.sh (tests)
- test/svt/profiler/ols-single-50roles/bench.sh (tests)
- test/svt/profiler/ols-single-50roles/data.json (data)
- test/svt/profiler/ols-single-50roles/input.json (data)
- test/svt/profiler/ols-single-50roles/profile-real-token.sh (tests)
- test/svt/profiler/ols-single-50roles/profile-trace.sh (tests)
- test/svt/profiler/ols-single-50roles/profile.sh (tests)
- test/svt/profiler/ols-single/bench-real-token.sh (tests)
- test/svt/profiler/ols-single/bench.sh (tests)
- test/svt/profiler/ols-single/data.json (data)
- test/svt/profiler/ols-single/input.json (data)
- test/svt/profiler/ols-single/profile-real-token.sh (tests)
- test/svt/profiler/ols-single/profile-trace.sh (tests)
- test/svt/profiler/ols-single/profile.sh (tests)
- test/svt/profiler/rls-condition-2-expression/bench-real-token.sh (tests)
- test/svt/profiler/rls-condition-2-expression/bench.sh (tests)
- test/svt/profiler/rls-condition-2-expression/data.json (data)
- test/svt/profiler/rls-condition-2-expression/input.json (data)
- test/svt/profiler/rls-condition-2-expression/profile-real-token.sh (tests)
- test/svt/profiler/rls-condition-2-expression/profile-trace.sh (tests)
- test/svt/profiler/rls-condition-2-expression/profile.sh (tests)
- test/svt/profiler/rls-condition-3-expression/bench-real-token.sh (tests)
- test/svt/profiler/rls-condition-3-expression/bench.sh (tests)
- test/svt/profiler/rls-condition-3-expression/data.json (data)
- test/svt/profiler/rls-condition-3-expression/input.json (data)
- test/svt/profiler/rls-condition-3-expression/profile-real-token.sh (tests)
- test/svt/profiler/rls-condition-3-expression/profile-trace.sh (tests)
- test/svt/profiler/rls-condition-3-expression/profile.sh (tests)
- test/svt/profiler/rls-condition-5-expression/bench-real-token.sh (tests)
- test/svt/profiler/rls-condition-5-expression/bench.sh (tests)
- test/svt/profiler/rls-condition-5-expression/data.json (data)
- test/svt/profiler/rls-condition-5-expression/input.json (data)
- test/svt/profiler/rls-condition-5-expression/profile-real-token.sh (tests)
- test/svt/profiler/rls-condition-5-expression/profile-trace.sh (tests)
- test/svt/profiler/rls-condition-5-expression/profile.sh (tests)
- test/svt/profiler/rls-condition/bench-real-token.sh (tests)
- test/svt/profiler/rls-condition/bench.sh (tests)
- test/svt/profiler/rls-condition/data.json (data)
- test/svt/profiler/rls-condition/input.json (data)
- test/svt/profiler/rls-condition/profile-real-token.sh (tests)
- test/svt/profiler/rls-condition/profile-trace.sh (tests)
- test/svt/profiler/rls-condition/profile.sh (tests)
- test/svt/profiler/rls-predicate-pips-1-header-pip/bench-real-token.sh (tests)
- test/svt/profiler/rls-predicate-pips-1-header-pip/bench.sh (tests)
- test/svt/profiler/rls-predicate-pips-1-header-pip/data.json (data)
- test/svt/profiler/rls-predicate-pips-1-header-pip/input.json (data)
- test/svt/profiler/rls-predicate-pips-1-header-pip/profile-real-token.sh (tests)
- test/svt/profiler/rls-predicate-pips-1-header-pip/profile-trace.sh (tests)
- test/svt/profiler/rls-predicate-pips-1-header-pip/profile.sh (tests)
- test/svt/profiler/rls-predicate-pips-1-token-pip/bench-real-token.sh (tests)
- test/svt/profiler/rls-predicate-pips-1-token-pip/bench.sh (tests)
- test/svt/profiler/rls-predicate-pips-1-token-pip/data.json (data)
- test/svt/profiler/rls-predicate-pips-1-token-pip/input.json (data)
- test/svt/profiler/rls-predicate-pips-1-token-pip/profile-real-token.sh (tests)
- test/svt/profiler/rls-predicate-pips-1-token-pip/profile-trace.sh (tests)
- test/svt/profiler/rls-predicate-pips-1-token-pip/profile.sh (tests)
- test/svt/profiler/rls-predicate-pips-2-header-pip/bench-real-token.sh (tests)
- test/svt/profiler/rls-predicate-pips-2-header-pip/bench.sh (tests)
- test/svt/profiler/rls-predicate-pips-2-header-pip/data.json (data)
- test/svt/profiler/rls-predicate-pips-2-header-pip/input.json (data)
- test/svt/profiler/rls-predicate-pips-2-header-pip/profile-real-token.sh (tests)
- test/svt/profiler/rls-predicate-pips-2-header-pip/profile-trace.sh (tests)
- test/svt/profiler/rls-predicate-pips-2-header-pip/profile.sh (tests)
- test/svt/profiler/rls-predicate-pips-2-token-pip/bench-real-token.sh (tests)
- test/svt/profiler/rls-predicate-pips-2-token-pip/bench.sh (tests)
- test/svt/profiler/rls-predicate-pips-2-token-pip/data.json (data)
- test/svt/profiler/rls-predicate-pips-2-token-pip/input.json (data)
- test/svt/profiler/rls-predicate-pips-2-token-pip/profile-real-token.sh (tests)
- test/svt/profiler/rls-predicate-pips-2-token-pip/profile-trace.sh (tests)
- test/svt/profiler/rls-predicate-pips-2-token-pip/profile.sh (tests)
- test/svt/profiler/rls-predicate-pips-3-header-pip/bench-real-token.sh (tests)
- test/svt/profiler/rls-predicate-pips-3-header-pip/bench.sh (tests)
- test/svt/profiler/rls-predicate-pips-3-header-pip/data.json (data)
- test/svt/profiler/rls-predicate-pips-3-header-pip/input.json (data)
- test/svt/profiler/rls-predicate-pips-3-header-pip/profile-real-token.sh (tests)
- test/svt/profiler/rls-predicate-pips-3-header-pip/profile-trace.sh (tests)
- test/svt/profiler/rls-predicate-pips-3-header-pip/profile.sh (tests)
- test/svt/profiler/rls-predicate-pips-3-token-pip/bench-real-token.sh (tests)
- test/svt/profiler/rls-predicate-pips-3-token-pip/bench.sh (tests)
- test/svt/profiler/rls-predicate-pips-3-token-pip/data.json (data)
- test/svt/profiler/rls-predicate-pips-3-token-pip/input.json (data)
- test/svt/profiler/rls-predicate-pips-3-token-pip/profile-real-token.sh (tests)
- test/svt/profiler/rls-predicate-pips-3-token-pip/profile-trace.sh (tests)
- test/svt/profiler/rls-predicate-pips-3-token-pip/profile.sh (tests)
- test/svt/profiler/rls-predicate-pips/bench-real-token.sh (tests)
- test/svt/profiler/rls-predicate-pips/bench.sh (tests)
- test/svt/profiler/rls-predicate-pips/data.json (data)
- test/svt/profiler/rls-predicate-pips/input.json (data)
- test/svt/profiler/rls-predicate-pips/profile-real-token.sh (tests)
- test/svt/profiler/rls-predicate-pips/profile-trace.sh (tests)
- test/svt/profiler/rls-predicate-pips/profile.sh (tests)
- test/svt/profiler/rls-predicate-summary-10-predicates-3-token-pip/bench-real-token.sh (tests)
- test/svt/profiler/rls-predicate-summary-10-predicates-3-token-pip/bench.sh (tests)
- test/svt/profiler/rls-predicate-summary-10-predicates-3-token-pip/data.json (data)
- test/svt/profiler/rls-predicate-summary-10-predicates-3-token-pip/input.json (data)
- test/svt/profiler/rls-predicate-summary-10-predicates-3-token-pip/profile-real-token.sh (tests)
- test/svt/profiler/rls-predicate-summary-10-predicates-3-token-pip/profile-trace.sh (tests)
- test/svt/profiler/rls-predicate-summary-10-predicates-3-token-pip/profile.sh (tests)
- test/svt/profiler/rls-predicate-summary-10-predicates/bench-real-token.sh (tests)
- test/svt/profiler/rls-predicate-summary-10-predicates/bench.sh (tests)
- test/svt/profiler/rls-predicate-summary-10-predicates/data.json (data)
- test/svt/profiler/rls-predicate-summary-10-predicates/input.json (data)
- test/svt/profiler/rls-predicate-summary-10-predicates/profile-real-token.sh (tests)
- test/svt/profiler/rls-predicate-summary-10-predicates/profile-trace.sh (tests)
- test/svt/profiler/rls-predicate-summary-10-predicates/profile.sh (tests)
- test/svt/profiler/rls-predicate-summary-2-predicates/bench-real-token.sh (tests)
- test/svt/profiler/rls-predicate-summary-2-predicates/bench.sh (tests)
- test/svt/profiler/rls-predicate-summary-2-predicates/data.json (data)
- test/svt/profiler/rls-predicate-summary-2-predicates/input.json (data)
- test/svt/profiler/rls-predicate-summary-2-predicates/profile-real-token.sh (tests)
- test/svt/profiler/rls-predicate-summary-2-predicates/profile-trace.sh (tests)
- test/svt/profiler/rls-predicate-summary-2-predicates/profile.sh (tests)
- test/svt/profiler/rls-predicate-summary-3-predicates/bench-real-token.sh (tests)
- test/svt/profiler/rls-predicate-summary-3-predicates/bench.sh (tests)
- test/svt/profiler/rls-predicate-summary-3-predicates/data.json (data)
- test/svt/profiler/rls-predicate-summary-3-predicates/input.json (data)
- test/svt/profiler/rls-predicate-summary-3-predicates/profile-real-token.sh (tests)
- test/svt/profiler/rls-predicate-summary-3-predicates/profile-trace.sh (tests)
- test/svt/profiler/rls-predicate-summary-3-predicates/profile.sh (tests)
- test/svt/profiler/rls-predicate-summary-4-predicates/bench-real-token.sh (tests)
- test/svt/profiler/rls-predicate-summary-4-predicates/bench.sh (tests)
- test/svt/profiler/rls-predicate-summary-4-predicates/data.json (data)
- test/svt/profiler/rls-predicate-summary-4-predicates/input.json (data)
- test/svt/profiler/rls-predicate-summary-4-predicates/profile-real-token.sh (tests)
- test/svt/profiler/rls-predicate-summary-4-predicates/profile-trace.sh (tests)
- test/svt/profiler/rls-predicate-summary-4-predicates/profile.sh (tests)
- test/svt/profiler/rls-predicate-summary-5-predicates/bench-real-token.sh (tests)
- test/svt/profiler/rls-predicate-summary-5-predicates/bench.sh (tests)
- test/svt/profiler/rls-predicate-summary-5-predicates/data.json (data)
- test/svt/profiler/rls-predicate-summary-5-predicates/input.json (data)
- test/svt/profiler/rls-predicate-summary-5-predicates/profile-real-token.sh (tests)
- test/svt/profiler/rls-predicate-summary-5-predicates/profile-trace.sh (tests)
- test/svt/profiler/rls-predicate-summary-5-predicates/profile.sh (tests)
- test/svt/profiler/rls-predicate/bench-real-token.sh (tests)
- test/svt/profiler/rls-predicate/bench.sh (tests)
- test/svt/profiler/rls-predicate/data.json (data)
- test/svt/profiler/rls-predicate/input.json (data)
- test/svt/profiler/rls-predicate/profile-real-token.sh (tests)
- test/svt/profiler/rls-predicate/profile-trace.sh (tests)
- test/svt/profiler/rls-predicate/profile.sh (tests)
- test/svt/profiler/wildcard-all-single/bench-real-token.sh (tests)
- test/svt/profiler/wildcard-all-single/bench.sh (tests)
- test/svt/profiler/wildcard-all-single/data.json (data)
- test/svt/profiler/wildcard-all-single/input.json (data)
- test/svt/profiler/wildcard-all-single/profile-real-token.sh (tests)
- test/svt/profiler/wildcard-all-single/profile-trace.sh (tests)
- test/svt/profiler/wildcard-all-single/profile.sh (tests)
- test/svt/profiler/wildcard-mixed-bulk/bench-real-token.sh (tests)
- test/svt/profiler/wildcard-mixed-bulk/bench.sh (tests)
- test/svt/profiler/wildcard-mixed-bulk/data.json (data)
- test/svt/profiler/wildcard-mixed-bulk/input.json (data)
- test/svt/profiler/wildcard-mixed-bulk/profile-real-token.sh (tests)
- test/svt/profiler/wildcard-mixed-bulk/profile-trace.sh (tests)
- test/svt/profiler/wildcard-mixed-bulk/profile.sh (tests)
- test/svt/scripts/bench-report (tests)

