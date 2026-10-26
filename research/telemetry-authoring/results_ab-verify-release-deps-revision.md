# The revision of the verifyReleaseDependencies trial

Arms `gen`, `gen2`, `gen3`, and `gen4` are the revision that moved the rules into the caller's-channel subsection of section 2; `gen2` also carries the example's size branch and per-branch remedies; `gen3` adds a library example and general detections; `gen4` asks for the change to the request beside raising a limit, with a size-limit example. Judge 2 scored `old`, `new`, and `gen`; judge 3 scored `new`, `gen`, and `gen2`; judge 4 scored `gen2` and `gen3`; judge 5 scored `gen3` and `gen4`. Each judge saw only letter codes.

## Project instructions of arms gen and gen2

```markdown
Contents of CLAUDE.md (project instructions, checked into the codebase):

Security model: [SECURITY.md](./SECURITY.md)

## Building and testing

JMeter builds with Gradle. Use `./gradlew --quiet ...` to reduce output verbosity.

After modifying Java code, before reporting the change as done (handing
control back to the user), run `./gradlew --quiet classes style` and fix any
reported issues.

JMeter uses Gradle toolchains; JDKs are found locally or auto-provisioned. The
code targets JDK 17. To test under a specific JDK pass build parameters:

- `-PjdkTestVersion=<n>` — JDK to run **tests** with; `0` means "use the current Java"
- `-PjdkTestVendor=<vendor>` / `-PjdkTestImplementation=<impl>` — pin the vendor / VM implementation (jdkTestVersion is enough for most cases)

List every available build parameter with `./gradlew parameters`.

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

## Example of arm gen

```markdown
 the release jars with a committed list, with one module added:

```text
The external jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check
catches dependencies that enter the release unnoticed, often transitively.
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings it in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
If the module is not intended, exclude it or revert the dependency update that brought it in. If it is, run
./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, commit the file, and name the module and the
dependency update that brought it in in the pull request description.
```
```

## Example of arm gen2

```markdown
 the release jars with a committed list, with one module added and the size over its limit:

```text
The external jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check
catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings it in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The total size of external jars is 88080384 bytes (84 MiB), which exceeds total-size-limit=87031808 (83 MiB) in
src/dist/src/dist/expected_release_artifacts.txt. The largest jars now:
  12582912 bcprov-jdk18on-1.78.jar
  ...
If the module is not intended, exclude it or revert the dependency update that brought it in. If the growth is not
intended, revert the update that grew the jars. If both are intended, run ./gradlew :src:dist:verifyReleaseDependencies
-PupdateExpectedJars, which also raises total-size-limit, commit the file, and name the module, the size growth, and the
dependency update in the pull request description.
```
```

## Judge2


| code | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 | F10 | F11 | F12 | R1 | R2 | R3 | R4 | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AA | P | Y | P | Y | Y | N | N | Y | N | N | Y | Y | P | P | Y | N | F1: no reason for the check, only "Release dependencies do not match"; F3: "over total-size-limit=87031808" without the file it lives in; no dependencyInsight, no jar list, no not-intended or PR text. R1: says what it checks, not why; R2: no cause command, casts doubt on the accept command ("its path looks doubled ... confirm the path first"); R4: "Regenerating the list won't fix the size overage" is false (the update resets the limit). |
| BB | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| CC | P | Y | P | Y | Y | N | Y | Y | N | N | Y | Y | Y | P | Y | Y | F1: no reason for the check; F3: "exceeds total-size-limit=87031808" without the file; no dependencyInsight, no not-intended or PR text. R2: accept command given, no cause command ("Read the CSV first"). |
| DD | P | Y | P | Y | Y | N | N | Y | N | N | Y | Y | P | P | Y | Y | F1: no reason for the check; F3: key without its file; no cause command, no jar list, no not-intended or PR text. R1: "compares release jars with a reviewed list" is what, not why; R2: no cause command. |
| EE | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| FF | P | Y | P | Y | Y | N | N | N | N | N | Y | N | Y | N | Y | Y | F1: no reason for the check; F3: key without its file; F8/F12: "./gradlew :src:dist -PupdateExpectedJars" names the project, not the task, and does not run as printed. R2: copies that wrong accept command and offers no cause command. |
| GG | Y | Y | Y | Y | Y | P | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | F6: the command carries a placeholder "--dependency <group:module>" and the module only follows as "for example org.example:foo". R4: "This directory isn't a git repo" comes from the reader's environment, not the output; not counted. |
| HH | Y | Y | P | Y | Y | Y | N | Y | Y | Y | P | Y | Y | Y | Y | Y | F3: "over total-size-limit=87031808" without the file; F7: no jar list or CSV path; F11: a removed module would get only a bare "  - module" line, and the remedies are shared. |
| II | Y | Y | P | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | F3: "exceeds total-size-limit=87031808" without saying the key is in the expected file. |
| JJ | P | Y | P | Y | Y | N | N | Y | N | N | Y | Y | Y | P | Y | Y | F1: no reason for the check; F3: key without its file; no cause command, jar list, not-intended or PR text. R2: accept command only, no cause command. |
| KK | Y | Y | Y | Y | Y | Y | N | Y | P | Y | Y | Y | Y | Y | Y | Y | F7: no jar list or CSV path; F9: only "If the growth is not intended, revert ..."; an added module that is not intended gets no remedy of its own. |
| LL | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | Y | Y | Y | Y | Y | Y | F7: no jar list or CSV path. |
| MM | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| NN | P | Y | P | Y | Y | N | Y | Y | N | N | Y | Y | Y | P | Y | Y | F1: no reason for the check; F3: key without its file; no dependencyInsight, no not-intended or PR text. R2: accept command, but the next step offered is "Check ... release_jars.csv", not a cause command for foo. |
| OO | P | Y | P | Y | Y | N | N | N | N | N | Y | N | Y | N | Y | N | F1: no reason for the check; F3: key without its file; F8/F12: "./gradlew :src:dist -PupdateExpectedJars" is not the task. R2: copies the wrong command as the only next step; R4: rewrites the path as "src/dist/expected_release_artifacts.txt", which is wrong. |
| PP | Y | Y | P | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | F3: "exceeds total-size-limit=87031808" without the file ("not in the file" refers to modules only). Code: dependencyInsight takes `added.first()` raw, so a classifier or @extension key would print an invalid --dependency; not triggered here. |
| QQ | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| RR | Y | Y | P | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | F3: "exceeds total-size-limit=87031808" without the file; F5: the overflow is not printed but is computable from total and limit. |

Best:

- BB: covers every ledger row, prints the largest jars, and states how the regenerated limit is computed, which let its reader predict the new 89 MiB limit correctly.
- EE: covers every row with a separate paragraph per branch, the largest jars, and the CSV path, and its reader's reply is clean and complete.
- QQ: covers every row, including MiB conversions, the largest jars and the CSV path, and its reader gave both commands and the PR content without a single guess.

MM ties with these three on the score; it leaves out the size of the added jar.

Worst:

- OO: a one-line message with a wrong accept command (`./gradlew :src:dist -PupdateExpectedJars`), no reason for the check, and no cause command; its reader repeated the wrong command and misquoted the expected-file path.
- FF: the same wrong accept command, no reason for the check, and no cause command or remedy for an unintended change; its reader could offer only the broken command.
- AA: one sentence with no reason for the check, no cause command, and no not-intended or PR guidance; its reader concluded, wrongly, that regenerating would not fix the size overage.

### Key

| code | run |
| --- | --- |
| AA | r2/haiku-old-2 |
| BB | r2/haiku-new-1 |
| CC | r2/sonnet-old-3 |
| DD | r2/sonnet-old-2 |
| EE | r2/sonnet-new-2 |
| FF | r2/haiku-old-3 |
| GG | r2/sonnet-new-1 |
| HH | r2/haiku-gen-1 |
| II | r2/sonnet-gen-3 |
| JJ | r2/haiku-old-1 |
| KK | r2/haiku-gen-3 |
| LL | r2/sonnet-gen-1 |
| MM | r2/haiku-new-2 |
| NN | r2/sonnet-old-1 |
| OO | r2/haiku-new-3 |
| PP | r2/sonnet-gen-2 |
| QQ | r2/sonnet-new-3 |
| RR | r2/haiku-gen-2 |

### Aggregates

| run | code | ledger /12 | F1 F3 F6 F7 F9 F10 | reader /4 |
| --- | --- | ---: | --- | ---: |
| haiku-gen-1 | HH | 10 | Y P Y N Y Y | 4 |
| haiku-gen-2 | RR | 11.5 | Y P Y Y Y Y | 4 |
| haiku-gen-3 | KK | 10.5 | Y Y Y N P Y | 4 |
| haiku-new-1 | BB | 12 | Y Y Y Y Y Y | 4 |
| haiku-new-2 | MM | 12 | Y Y Y Y Y Y | 4 |
| haiku-new-3 | OO | 5 | P P N N N N | 2 |
| haiku-old-1 | JJ | 7 | P P N N N N | 3.5 |
| haiku-old-2 | AA | 7 | P P N N N N | 2 |
| haiku-old-3 | FF | 5 | P P N N N N | 3 |
| sonnet-gen-1 | LL | 11 | Y Y Y N Y Y | 4 |
| sonnet-gen-2 | PP | 11.5 | Y P Y Y Y Y | 4 |
| sonnet-gen-3 | II | 11.5 | Y P Y Y Y Y | 4 |
| sonnet-new-1 | GG | 11.5 | Y Y P Y Y Y | 4 |
| sonnet-new-2 | EE | 12 | Y Y Y Y Y Y | 4 |
| sonnet-new-3 | QQ | 12 | Y Y Y Y Y Y | 4 |
| sonnet-old-1 | NN | 8 | P P N Y N N | 3.5 |
| sonnet-old-2 | DD | 7 | P P N N N N | 3 |
| sonnet-old-3 | CC | 8 | P P N Y N N | 3.5 |

| model | arm | mean ledger /12 | all 12 | mean reader /4 | F3 (key with its file) Y | F7 (growth) Y |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| haiku | gen | 10.7 | 0/3 | 4.0 | 1/3 | 1/3 |
| haiku | new | 9.7 | 2/3 | 3.3 | 2/3 | 2/3 |
| haiku | old | 6.3 | 0/3 | 2.8 | 0/3 | 0/3 |
| sonnet | gen | 11.3 | 0/3 | 4.0 | 1/3 | 2/3 |
| sonnet | new | 11.8 | 2/3 | 4.0 | 3/3 | 3/3 |
| sonnet | old | 7.7 | 0/3 | 3.3 | 0/3 | 2/3 |

## Judge3


| code | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 | F10 | F11 | F12 | R1 | R2 | R3 | R4 | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| XA | P | Y | Y | Y | Y | Y | P | Y | Y | Y | P | Y | Y | Y | Y | Y | F1: purpose is "dependencies that enter or leave the release unnoticed", nothing on size; F7: only the added jar's size, no list, file, or command; F11: size-only branch prints `--dependency <group:module>` and "exclude the module" |
| XB | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | P | Y | Y | Y | Y | F12: "The total size of external jars is 88080384 bytes", but the total sums every artifact, JMeter jars included |
| XC | Y | Y | P | Y | Y | Y | Y | Y | Y | Y | P | Y | Y | Y | Y | Y | F3: "exceeds total-size-limit=87031808 by 1048576 bytes" names no file ("not in the file"); F11: one shared remedy for added, removed, and size |
| XD | Y | Y | P | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | F3: "exceeds total-size-limit=87031808 (83.00 MiB (87031808 bytes))" without the file it lives in |
| XE | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| XF | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| XG | P | Y | P | Y | Y | Y | Y | Y | Y | Y | P | Y | Y | Y | Y | Y | F1: purpose covers only dependencies, not size; F3: "total size 88080384 bytes exceeds total-size-limit=87031808" without the file; F11: branches differ only in a summary clause, one shared remedy |
| XH | Y | Y | Y | Y | Y | Y | Y | Y | Y | P | Y | Y | Y | Y | Y | Y | F10: "name each added or removed module and the size growth", not the dependency update; reader says "The output doesn't name the task", which is false but harmless |
| XI | Y | Y | Y | Y | Y | P | N | Y | Y | P | P | Y | Y | Y | Y | Y | F6: "./gradlew :src:dist:dependencies --configuration runtimeClasspath" runs but has no module; F7: no jar sizes, file, or size command; F10: "name the added or removed modules and the size change", no dependency update; F11: removed modules get the added-module remedy |
| XJ | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| XK | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| XL | P | Y | P | Y | Y | N | N | N | N | N | P | N | Y | N | Y | N | F1: no reason for the check; F3: key without file; F6/F7: no command or file; F8/F12: "./gradlew :src:dist -PupdateExpectedJars" names the project, not the task; F9/F10: nothing; R2: repeats the wrong command as the only next step; R4: "missing from `src/dist/expected_release_artifacts.txt`", a path the output does not give |
| XM | Y | Y | P | Y | Y | Y | N | Y | Y | P | P | Y | Y | Y | Y | Y | F3: "1048576 bytes over total-size-limit=87031808" without the file; F7: no list, file, or size command; F10: "name the changed modules and the dependency update", no size; F11: one shared remedy |
| XN | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| XO | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| XP | Y | Y | Y | Y | Y | P | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | F6: printed command is "--dependency <group:module>", filled only by "for example org.example:foo" |
| XQ | Y | Y | P | Y | Y | Y | N | Y | P | P | P | Y | Y | Y | Y | Y | F3: "exceeds total-size-limit=87031808" without the file, only implied by the rewrite sentence; F7: no list, file, or size command; F9: only "If the growth is not intended", no remedy for the added module; F10: "name the added and removed modules and the dependency update", no size; F11: added branch has no remedy |
| XR | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | P | Y | Y | Y | Y | Y | F11: removed modules get no remedy of their own; one shared "revert ... or exclude the module" |

Best three:

- XN: every branch has its own cause, list, and remedy, the largest jars are printed with units, and it states the exact regeneration rule (plus 5 MiB, rounded up), which the reader turned into a correct 89 MiB.
- XF: separate paragraphs per branch with module jar sizes, the largest jars, the CSV path, and a removed-module hint, with the key located in its file.
- XE: same coverage as XF (list, CSV, per-branch remedies, overflow in bytes) with no wrong or invented text.

Worst three:

- XL: the accept command `./gradlew :src:dist -PupdateExpectedJars` does not run the task, and the message gives no cause command, no not-intended guidance, and no pull request guidance; its reader also misquoted the path.
- XQ: no way to find which jars grew, no remedy for the added module, and pull request guidance omits the size.
- XI: the cause command lists the whole tree without the module, nothing shows jar sizes, and removed modules share the added-module remedy.

### Key

| code | run |
| --- | --- |
| XA | r2/sonnet-gen-1 |
| XB | r2/haiku-gen2-2 |
| XC | r2/sonnet-gen-2 |
| XD | r2/sonnet-gen-3 |
| XE | r2/sonnet-new-2 |
| XF | r2/sonnet-new-3 |
| XG | r2/haiku-gen-2 |
| XH | r2/haiku-gen2-1 |
| XI | r2/haiku-gen2-3 |
| XJ | r2/haiku-new-2 |
| XK | r2/sonnet-gen2-3 |
| XL | r2/haiku-new-3 |
| XM | r2/haiku-gen-1 |
| XN | r2/haiku-new-1 |
| XO | r2/sonnet-gen2-1 |
| XP | r2/sonnet-new-1 |
| XQ | r2/haiku-gen-3 |
| XR | r2/sonnet-gen2-2 |

### Aggregates

| run | code | ledger /12 | F1 F3 F6 F7 F9 F10 F11 F12 | reader /4 |
| --- | --- | ---: | --- | ---: |
| haiku-gen-1 | XM | 9.5 | Y P Y N Y P P Y | 4 |
| haiku-gen-2 | XG | 10.5 | P P Y Y Y Y P Y | 4 |
| haiku-gen-3 | XQ | 9 | Y P Y N P P P Y | 4 |
| haiku-gen2-1 | XH | 11.5 | Y Y Y Y Y P Y Y | 4 |
| haiku-gen2-2 | XB | 11.5 | Y Y Y Y Y Y Y P | 4 |
| haiku-gen2-3 | XI | 9.5 | Y Y P N Y P P Y | 4 |
| haiku-new-1 | XN | 12 | Y Y Y Y Y Y Y Y | 4 |
| haiku-new-2 | XJ | 12 | Y Y Y Y Y Y Y Y | 4 |
| haiku-new-3 | XL | 4.5 | P P N N N N P N | 2 |
| sonnet-gen-1 | XA | 10.5 | P Y Y P Y Y P Y | 4 |
| sonnet-gen-2 | XC | 11 | Y P Y Y Y Y P Y | 4 |
| sonnet-gen-3 | XD | 11.5 | Y P Y Y Y Y Y Y | 4 |
| sonnet-gen2-1 | XO | 12 | Y Y Y Y Y Y Y Y | 4 |
| sonnet-gen2-2 | XR | 11.5 | Y Y Y Y Y Y P Y | 4 |
| sonnet-gen2-3 | XK | 12 | Y Y Y Y Y Y Y Y | 4 |
| sonnet-new-1 | XP | 11.5 | Y Y P Y Y Y Y Y | 4 |
| sonnet-new-2 | XE | 12 | Y Y Y Y Y Y Y Y | 4 |
| sonnet-new-3 | XF | 12 | Y Y Y Y Y Y Y Y | 4 |

| model | arm | mean ledger /12 | all 12 | mean reader /4 | F3 Y | F7 Y | F11 Y |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| haiku | gen | 9.7 | 0/3 | 4.0 | 0/3 | 1/3 | 0/3 |
| haiku | gen2 | 10.8 | 0/3 | 4.0 | 3/3 | 2/3 | 2/3 |
| haiku | new | 9.5 | 2/3 | 3.3 | 2/3 | 2/3 | 2/3 |
| sonnet | gen | 11.0 | 0/3 | 4.0 | 1/3 | 2/3 | 1/3 |
| sonnet | gen2 | 11.8 | 2/3 | 4.0 | 3/3 | 3/3 | 2/3 |
| sonnet | new | 11.8 | 2/3 | 4.0 | 3/3 | 3/3 | 3/3 |

## r2/haiku-gen-1 (judge 3 code XM)

### Rendered message

```text
Release dependencies do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches external modules that enter or leave the binary release unnoticed, and jars that outgrow total-size-limit.
  + org.example:foo
  total size of the jars is 88080384 bytes, which is 1048576 bytes over total-size-limit=87031808
To see which dependency brings in org.example:foo, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
If a change is not intended, exclude the module or revert the dependency update that caused it.
If it is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, commit src/dist/src/dist/expected_release_artifacts.txt, and name the changed modules and the dependency update behind them in the pull request description.
```

### Reader reply

```markdown
1. **Failed:** `verifyReleaseDependencies`. The release's external modules differ from `expected_release_artifacts.txt`, and jar size exceeds `total-size-limit`. The check catches modules entering or leaving the release unnoticed, and size growth.

2. **Changed:** `org.example:foo` was added. Total size is 88,080,384 bytes, 1,048,576 over the 87,031,808 limit. The output doesn't name the responsible dependency or the prior size.

3. **Next (not run):** `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo` to find what pulls in `foo`.

4. **If intended:** run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit the expected-artifacts file. The output doesn't say whether this clears the size overage, so re-run the build to confirm. **If not:** exclude `org.example:foo` or revert the dependency update.

5. **PR description:** name `org.example:foo`, the dependency update behind it (once confirmed), the size overage, and the expected-artifacts change.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,26 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val lines = mutableListOf(
+            "Release dependencies do not match ${expectedFile.relativeTo(rootDir)}. " +
+                "The check catches external modules that enter or leave the binary release unnoticed, " +
+                "and jars that outgrow total-size-limit.",
+        )
+        val addedSorted = added.sortedWith(caseInsensitive)
+        addedSorted.forEach { lines.add("  + $it") }
+        removed.forEach { lines.add("  - $it") }
+        if (totalSize > sizeLimit) {
+            lines.add("  total size of the jars is $totalSize bytes, which is ${totalSize - sizeLimit} bytes over total-size-limit=$sizeLimit")
+        }
+        for (module in addedSorted) {
+            lines.add("To see which dependency brings in $module, run ./gradlew $projectPath:dependencyInsight --configuration runtimeClasspath --dependency $module")
+        }
+        lines.add("If a change is not intended, exclude the module or revert the dependency update that caused it.")
+        lines.add(
+            "If it is intended, run ./gradlew $path -PupdateExpectedJars, commit ${expectedFile.relativeTo(rootDir)}, " +
+                "and name the changed modules and the dependency update behind them in the pull request description."
+        )
+        throw GradleException(lines.joinToString(newline))
     }
 }
```

## r2/haiku-gen-2 (judge 3 code XG)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt: modules added: org.example:foo; total size 88080384 bytes exceeds total-size-limit=87031808.
The check catches dependencies that enter the release unnoticed, often transitively.
The size of each jar is in src/dist/build/dist/release_jars.csv.
To see which dependency brings in org.example:foo, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
If the change is not intended, exclude the module or revert the dependency update that brought it in.
If it is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, commit src/dist/src/dist/expected_release_artifacts.txt,
and name the changed modules or the size growth and the dependency update that caused it in the pull request description.
```

### Reader reply

```markdown
**1. Failure:** The release-jar check failed. It compares the release jars against `src/dist/src/dist/expected_release_artifacts.txt` to catch dependencies that enter the release unnoticed, often transitively. Module `org.example:foo` was added, and total size is 88,080,384 bytes, 1,048,576 over the 87,031,808 limit.

**2. What changed:** The release gained `org.example:foo` and exceeds the size limit. The output doesn't say which update introduced it or how large its jar is.

**3. Next command:** `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo` to find the path. Per-jar sizes are in `src/dist/build/dist/release_jars.csv`.

**4. Actions:**
- **Not intended:** Exclude `org.example:foo` or revert the dependency update that brought it in.
- **Intended:** Run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit `src/dist/src/dist/expected_release_artifacts.txt`. The output doesn't say whether this also raises `total-size-limit`, so check before assuming it does.

**5. PR description:** Name `org.example:foo`, the 1,048,576-byte overage, and the dependency update that caused it.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,37 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val problems = buildList {
+            if (added.isNotEmpty()) {
+                add("modules added: ${added.sortedWith(caseInsensitive).joinToString()}")
+            }
+            if (removed.isNotEmpty()) {
+                add("modules removed: ${removed.joinToString()}")
+            }
+            if (totalSize > sizeLimit) {
+                add("total size $totalSize bytes exceeds total-size-limit=$sizeLimit")
+            }
+        }
+        val details = buildList {
+            if (totalSize > sizeLimit) {
+                add("The size of each jar is in ${actualJars.get().asFile.relativeTo(rootDir)}.")
+            }
+            added.firstOrNull()?.let {
+                add("To see which dependency brings in $it, run ./gradlew $projectPath:dependencyInsight --configuration runtimeClasspath --dependency $it")
+            }
+        }
+        throw GradleException(
+            listOf(
+                "The jars of the binary release do not match ${expectedFile.relativeTo(rootDir)}: ${problems.joinToString("; ")}.",
+                "The check catches dependencies that enter the release unnoticed, often transitively.",
+            ).plus(details).plus(
+                listOf(
+                    "If the change is not intended, exclude the module or revert the dependency update that brought it in.",
+                    "If it is intended, run ./gradlew $projectPath:verifyReleaseDependencies -PupdateExpectedJars, commit ${expectedFile.relativeTo(rootDir)},",
+                    "and name the changed modules or the size growth and the dependency update that caused it in the pull request description.",
+                ),
+            ).joinToString(newline)
+        )
     }
 }
```

## r2/haiku-gen-3 (judge 3 code XQ)

### Rendered message

```text
The external modules or the total jar size of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt.
The check keeps a dependency from entering, leaving, or growing the release unnoticed, including one brought in transitively.
  added    org.example:foo
  total size 88080384 bytes exceeds total-size-limit=87031808 by 1048576 bytes
To see which dependency brings in org.example:foo, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
If the growth is not intended, revert the dependency update that grew the release.
If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars. It rewrites src/dist/src/dist/expected_release_artifacts.txt with the current modules and sets total-size-limit to the current size plus 5 MiB.
Commit src/dist/src/dist/expected_release_artifacts.txt, and name the added and removed modules and the dependency update behind them in the pull request description.
```

### Reader reply

```markdown
**1. Failure.** `verifyReleaseDependencies` failed because the release's modules or total jar size don't match `expected_release_artifacts.txt`. The check catches dependencies added, removed, or grown, including transitive ones. `org.example:foo` was added, and the total is 1048576 bytes over the limit.

**2. Changes.** The output shows only that addition and the overrun. It doesn't show the update's diff or any removed module.

**3. Next.** `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`. It's read-only and shows what pulls in `foo`.

**4. Action.** If intended, run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and review the rewritten file. Its new limit is current size plus 5 MiB, so growth up to that goes unchecked. If not, revert the dependency update. The output doesn't name it.

**5. PR description.** Name `org.example:foo` as added, the update that brings it in, and the size overrun. The output doesn't say whether anything was removed. Commit the regenerated file. This environment reports no git repository, so that step may not apply here.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,40 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedName = expectedFile.relativeTo(rootDir)
+        val regenerate = "$projectPath:verifyReleaseDependencies -PupdateExpectedJars"
+        throw GradleException(
+            buildString {
+                appendLine("The external modules or the total jar size of the binary release do not match $expectedName.")
+                appendLine("The check keeps a dependency from entering, leaving, or growing the release unnoticed, including one brought in transitively.")
+                for (module in added.sortedWith(caseInsensitive)) {
+                    appendLine("  added    $module")
+                }
+                for (module in removed) {
+                    appendLine("  removed  $module")
+                }
+                if (totalSize > sizeLimit) {
+                    appendLine("  total size $totalSize bytes exceeds total-size-limit=$sizeLimit by ${totalSize - sizeLimit} bytes")
+                }
+                for (module in added.sortedWith(caseInsensitive)) {
+                    appendLine("To see which dependency brings in $module, run ./gradlew $projectPath:dependencyInsight --configuration runtimeClasspath --dependency $module")
+                }
+                if (removed.isNotEmpty()) {
+                    appendLine("If a removal is not intended, restore the dependency or the change that dropped the module.")
+                }
+                if (totalSize > sizeLimit) {
+                    appendLine("If the growth is not intended, revert the dependency update that grew the release.")
+                }
+                appendLine(
+                    "If the change is intended, run ./gradlew $regenerate. It rewrites $expectedName with the current modules " +
+                        "and sets total-size-limit to the current size plus ${releaseJarsSizeHeadroom / mib} MiB."
+                )
+                append(
+                    "Commit $expectedName, and name the added and removed modules and the dependency update behind them " +
+                        "in the pull request description."
+                )
+            }
+        )
     }
 }
```

## r2/haiku-gen2-1 (judge 3 code XH)

### Rendered message

```text
The external jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt.
The check catches a dependency that enters or leaves the release unnoticed, often through a transitive dependency, and a release that grows past its size limit without review.
  + org.example:foo (foo-1.2.jar)
    To see which dependency brings it in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The total size of the release jars, JMeter jars included, is 88080384 bytes (about 84 MiB). It exceeds total-size-limit=87031808 bytes (83 MiB) in src/dist/src/dist/expected_release_artifacts.txt.
The largest jars now:
  12582912 bytes bcprov-jdk18on-1.78.jar
  9437184 bytes groovy-4.0.21.jar
  5242880 bytes jmeter-core.jar
  4194304 bytes xstream-1.4.20.jar
  3145728 bytes rhino-1.7.14.jar
If a module change or the growth is not intended, revert the update that brought it in. Then run this task again.
If the changes are intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars. It rewrites src/dist/src/dist/expected_release_artifacts.txt and sets total-size-limit to the current total size plus 5 MiB. Review the rewritten file in the diff, commit it, and name each added or removed module and the size growth in the pull request description.
Do not run that command to clear a failure whose cause you cannot explain.
```

### Reader reply

```markdown
**1. Failure:** `org.example:foo` (foo-1.2.jar) is a new external jar missing from `expected_release_artifacts.txt`. The total, 88080384 bytes, also exceeds the limit by 1 MiB. The check catches unreviewed dependencies, including transitive ones, and unreviewed size growth.

**2. Changes:** The output shows one addition and no removals. It doesn't show which part of your update added foo or the prior total, so the growth is unknown.

**3. Next command** (from the output):
`./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`

**4. Next steps:**
- **Intended:** run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars`, review the diff, and commit. This raises the limit to 93323264 bytes.
- **Not intended:** revert the update that added foo, then run the task again. The output doesn't name the task.

**5. PR description:** Name `org.example:foo` as added, give its dependency path from dependencyInsight, and state the size growth (prior total unknown).
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,53 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        throw GradleException(
+            buildString {
+                val expectedPath = expectedFile.relativeTo(rootDir)
+                appendLine("The external jars of the binary release do not match $expectedPath.")
+                appendLine(
+                    "The check catches a dependency that enters or leaves the release unnoticed, often through a transitive " +
+                        "dependency, and a release that grows past its size limit without review."
+                )
+                for (module in added) {
+                    val jarNames = jarsByModule.getValue(module).joinToString { it.file.name }
+                    appendLine("  + $module ($jarNames)")
+                    appendLine(
+                        "    To see which dependency brings it in, run " +
+                            "./gradlew $projectPath:dependencyInsight --configuration runtimeClasspath --dependency $module"
+                    )
+                }
+                for (module in removed) {
+                    appendLine("  - $module")
+                    appendLine(
+                        "    No jar of the release resolves to it now. If that is not intended, a dependency declaration was lost. " +
+                            "Search for it with grep -rn '${module.split(':')[1]}' --include='*.kts' ."
+                    )
+                }
+                if (totalSize > sizeLimit) {
+                    appendLine(
+                        "The total size of the release jars, JMeter jars included, is $totalSize bytes " +
+                            "(about ${totalSize / mib} MiB). It exceeds total-size-limit=$sizeLimit bytes " +
+                            "(${sizeLimit / mib} MiB) in $expectedPath."
+                    )
+                    appendLine("The largest jars now:")
+                    for (artifact in artifacts.sortedByDescending { it.file.length() }.take(5)) {
+                        appendLine("  ${artifact.file.length()} bytes ${artifact.file.name}")
+                    }
+                }
+                appendLine(
+                    "If a module change or the growth is not intended, revert the update that brought it in. " +
+                        "Then run this task again."
+                )
+                appendLine(
+                    "If the changes are intended, run ./gradlew $projectPath:verifyReleaseDependencies -PupdateExpectedJars. " +
+                        "It rewrites $expectedPath and sets total-size-limit to the current total size plus " +
+                        "${releaseJarsSizeHeadroom / mib} MiB. Review the rewritten file in the diff, commit it, and name each " +
+                        "added or removed module and the size growth in the pull request description."
+                )
+                append("Do not run that command to clear a failure whose cause you cannot explain.")
+            }
+        )
     }
 }
```

## r2/haiku-gen2-2 (judge 3 code XB)

### Rendered message

```text
The external jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt.
The check catches a dependency that enters the release unnoticed, often transitively, and a release that grows past its limit.
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings in org.example:foo, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The total size of external jars is 88080384 bytes (84 MiB), which exceeds total-size-limit=87031808 bytes (83 MiB) in src/dist/src/dist/expected_release_artifacts.txt. The largest jars now:
  12582912 bcprov-jdk18on-1.78.jar
  9437184 groovy-4.0.21.jar
  4194304 xstream-1.4.20.jar
  3145728 rhino-1.7.14.jar
  2097152 httpclient-4.5.14.jar
If an added module is not intended, exclude it or revert the dependency update that brought it in.
If a removed module is not intended, restore its dependency.
If the size growth is not intended, revert the dependency update that grew the jars.
To accept the current release, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars. It also raises total-size-limit, so commit src/dist/src/dist/expected_release_artifacts.txt and name the changed modules, the size growth, and the dependency update in the pull request description.
```

### Reader reply

```markdown
**1. Failure:** The release check found external jars that don't match `src/dist/src/dist/expected_release_artifacts.txt`. It catches dependencies that enter the release unnoticed and releases that outgrow their size limit. The total is 88080384 bytes, 1048576 over the 87031808 limit, which is exactly foo's size.

**2. Change:** Added `org.example:foo` (`foo-1.2.jar`, 1048576 bytes). The output doesn't name the update that added it or give the previous total, so I can't tell whether other jars changed.

**3. Next command:**
`./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`

**4. If intended:** run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars`, then commit `expected_release_artifacts.txt`. **If not:** exclude foo, or revert the update that brought it in.

**5. PR description:** Name `org.example:foo` as added, its size (about 1 MiB), the new 84 MiB total, the raised limit, and the dependency update responsible.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -267,11 +267,50 @@
 
         val added = jarsByModule.keys - expectedModules
         val removed = expectedModules.sortedWith(caseInsensitive) - jarsByModule.keys
-        if (added.isEmpty() && removed.isEmpty() && totalSize <= sizeLimit) {
+        val sizeExceeded = totalSize > sizeLimit
+        if (added.isEmpty() && removed.isEmpty() && !sizeExceeded) {
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val taskPath = path
+        throw GradleException(
+            buildString {
+                appendLine("The external jars of the binary release do not match $expectedPath.")
+                appendLine("The check catches a dependency that enters the release unnoticed, often transitively, and a release that grows past its limit.")
+                for (module in added) {
+                    val jarNames = jarsByModule.getValue(module).joinToString { "${it.file.name}, ${it.file.length()} bytes" }
+                    appendLine("  + $module ($jarNames)")
+                }
+                for (module in removed) {
+                    appendLine("  - $module")
+                }
+                for (module in added) {
+                    appendLine("To see which dependency brings in $module, run ./gradlew $projectPath:dependencyInsight --configuration runtimeClasspath --dependency $module")
+                }
+                if (sizeExceeded) {
+                    appendLine(
+                        "The total size of external jars is $totalSize bytes (${totalSize / mib} MiB), which exceeds " +
+                            "total-size-limit=$sizeLimit bytes (${sizeLimit / mib} MiB) in $expectedPath. The largest jars now:"
+                    )
+                    for (jar in jarsByModule.values.flatten().sortedByDescending { it.file.length() }.take(5)) {
+                        appendLine("  ${jar.file.length()} ${jar.file.name}")
+                    }
+                }
+                if (added.isNotEmpty() || removed.isNotEmpty()) {
+                    appendLine("If an added module is not intended, exclude it or revert the dependency update that brought it in.")
+                    appendLine("If a removed module is not intended, restore its dependency.")
+                }
+                if (sizeExceeded) {
+                    appendLine("If the size growth is not intended, revert the dependency update that grew the jars.")
+                }
+                appendLine(
+                    "To accept the current release, run ./gradlew $taskPath -PupdateExpectedJars. " +
+                        "It also raises total-size-limit, so commit $expectedPath and name the changed modules, the size growth, " +
+                        "and the dependency update in the pull request description."
+                )
+            }
+        )
     }
 }
```

## r2/haiku-gen2-3 (judge 3 code XI)

### Rendered message

```text
Release dependencies do not match src/dist/src/dist/expected_release_artifacts.txt.
The check catches external modules that enter or leave the binary release unnoticed, often transitively, and unexpected growth of the release.
  Added to the release, not listed in src/dist/src/dist/expected_release_artifacts.txt: org.example:foo
  The jars of the release total 88080384 bytes, which exceeds total-size-limit=87031808 in src/dist/src/dist/expected_release_artifacts.txt.
To see which dependency brings in an added module, run ./gradlew :src:dist:dependencies --configuration runtimeClasspath
If a module is not intended, exclude it or revert the dependency update that brought it in. If the size growth is not intended, revert the update that grew the jars.
If both are intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, commit src/dist/src/dist/expected_release_artifacts.txt, and name the added or removed modules and the size change in the pull request description.
```

### Reader reply

```markdown
**1. Failure.** `:src:dist:verifyReleaseDependencies` failed because the release dependencies don't match `expected_release_artifacts.txt`. The check catches external modules, including transitive ones, that enter or leave the release unnoticed, and unexpected size growth.

**2. Changes.** `org.example:foo` was added to the release but isn't listed. The jars total 88080384 bytes, which is 1048576 bytes (1 MiB) over the 87031808-byte limit. The output doesn't say which update brought in `foo` or what the previous total was.

**3. Next command.** To trace `foo`:
`./gradlew :src:dist:dependencies --configuration runtimeClasspath`
I haven't run it.

**4. Next steps.**
- **If intended:** run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars`, then commit `expected_release_artifacts.txt`.
- **If not intended:** exclude `foo` or revert the update that added it. If the size growth is unintended, revert the update that grew the jars.

**5. PR description.** Name `org.example:foo` as added and state the size change. The output doesn't say whether `-PupdateExpectedJars` also changes `total-size-limit`.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,33 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val problems = buildList {
+            if (added.isNotEmpty()) {
+                add("Added to the release, not listed in $expectedPath: ${added.joinToString()}")
+            }
+            if (removed.isNotEmpty()) {
+                add("Listed in $expectedPath, not in the release: ${removed.joinToString()}")
+            }
+            if (totalSize > sizeLimit) {
+                add("The jars of the release total $totalSize bytes, which exceeds total-size-limit=$sizeLimit in $expectedPath.")
+            }
+        }
+        throw GradleException(
+            (
+                listOf(
+                    "Release dependencies do not match $expectedPath.",
+                    "The check catches external modules that enter or leave the binary release unnoticed, often transitively, " +
+                        "and unexpected growth of the release.",
+                ) + problems.map { "  $it" } + listOf(
+                    "To see which dependency brings in an added module, run ./gradlew $projectPath:dependencies --configuration runtimeClasspath",
+                    "If a module is not intended, exclude it or revert the dependency update that brought it in. " +
+                        "If the size growth is not intended, revert the update that grew the jars.",
+                    "If both are intended, run ./gradlew $path -PupdateExpectedJars, commit $expectedPath, " +
+                        "and name the added or removed modules and the size change in the pull request description.",
+                )
+            ).joinToString(newline)
+        )
     }
 }
```

## r2/sonnet-gen-1 (judge 3 code XA)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter or leave the release unnoticed, often transitively.
  + org.example:foo (foo-1.2.jar, 1048576 bytes) is in the release and not in src/dist/src/dist/expected_release_artifacts.txt
  total size of the jars is 88080384 bytes, which exceeds total-size-limit=87031808 in src/dist/src/dist/expected_release_artifacts.txt
To see which dependency brings a module in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
If the change is not intended, exclude the module or revert the dependency update that caused it. If it is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, commit the regenerated src/dist/src/dist/expected_release_artifacts.txt, and name the changed modules or sizes and the dependency update behind them in the pull request description.
```

### Reader reply

```markdown
**1. Failure:** The release jars don't match `src/dist/src/dist/expected_release_artifacts.txt`. The check catches dependencies entering or leaving the release unnoticed, often transitively. `org.example:foo` (1048576 bytes) is new, and the total jar size (88080384 bytes) exceeds the 87031808-byte limit.

**2. Change:** `foo-1.2.jar` was added. The output doesn't say which update brought it in, or whether anything was removed.

**3. Next:** `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`. It's read-only, and I haven't run it.

**4. Action:** If intended, run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit the regenerated list. The output doesn't say whether the size limit updates too. If not intended, exclude foo or revert the update.

**5. PR description:** Name foo-1.2 (1048576 bytes), the dependency update behind it, and the new total of 88080384 bytes against the old limit of 87031808.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,29 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val problems = buildList {
+            added.forEach { module ->
+                val jars = jarsByModule.getValue(module).joinToString { "${it.file.name}, ${it.file.length()} bytes" }
+                add("  + $module ($jars) is in the release and not in $expectedPath")
+            }
+            removed.forEach { module ->
+                add("  - $module is listed in $expectedPath and not in the release")
+            }
+            if (totalSize > sizeLimit) {
+                add("  total size of the jars is $totalSize bytes, which exceeds total-size-limit=$sizeLimit in $expectedPath")
+            }
+        }
+        val insightModule = (added.firstOrNull() ?: removed.firstOrNull() ?: "<group:module>")
+            .substringBefore('@').split(':').take(2).joinToString(":")
+        throw GradleException(
+            buildString {
+                appendLine("The jars of the binary release do not match $expectedPath. The check catches dependencies that enter or leave the release unnoticed, often transitively.")
+                problems.forEach { appendLine(it) }
+                appendLine("To see which dependency brings a module in, run ./gradlew ${projectPath}:dependencyInsight --configuration runtimeClasspath --dependency $insightModule")
+                appendLine("If the change is not intended, exclude the module or revert the dependency update that caused it. If it is intended, run ./gradlew $path -PupdateExpectedJars, commit the regenerated $expectedPath, and name the changed modules or sizes and the dependency update behind them in the pull request description.")
+            }
+        )
     }
 }
```

## r2/sonnet-gen-2 (judge 3 code XC)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter the release unnoticed, often transitively, and a release that grows without review.
  + org.example:foo (foo-1.2.jar, 1048576 bytes) is in the release but not in the file
  The jars total 88080384 bytes, which exceeds total-size-limit=87031808 by 1048576 bytes.
To see which dependency brings a module in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The sizes of all jars are in src/dist/build/dist/release_jars.csv.
If the change is not intended, exclude the dependency or revert the update that caused it. If it is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, commit src/dist/src/dist/expected_release_artifacts.txt, and name the added and removed modules, the size change, and the dependency update behind them in the pull request description.
```

### Reader reply

```markdown
**1. Failed:** The release-jar check. The jars don't match `expected_release_artifacts.txt`, which catches dependencies (often transitive) entering the release unreviewed. `org.example:foo` 1.2 (1,048,576 bytes) is new. The total, 88,080,384 bytes, exceeds `total-size-limit` by 1,048,576.

**2. Changed:** Only the addition of `foo-1.2.jar`. The output doesn't name the update that brought it in or list any removed modules.

**3. Next (not run):** `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`, then read `src/dist/build/dist/release_jars.csv` for all jar sizes.

**4. Unintended:** Exclude foo or revert the update. **Intended:** Run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit the expected file. The output doesn't say whether `total-size-limit` also needs raising, so check before merging.

**5. PR description:** Name `org.example:foo` 1.2 as added, its size, the new total, and the update behind it. Removed modules aren't shown, so confirm before stating there are none.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,34 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val update = "./gradlew $path -PupdateExpectedJars"
+        val message = StringBuilder()
+        message.append("The jars of the binary release do not match $expectedPath. ")
+            .append("The check catches dependencies that enter the release unnoticed, often transitively, and a release that grows without review.")
+            .append(newline)
+        for (module in added) {
+            val jars = jarsByModule.getValue(module)
+            message.append("  + $module (${jars.joinToString { "${it.file.name}, ${it.file.length()} bytes" }}) is in the release but not in the file")
+                .append(newline)
+        }
+        for (module in removed) {
+            message.append("  - $module is in the file but not in the release").append(newline)
+        }
+        if (totalSize > sizeLimit) {
+            message.append("  The jars total $totalSize bytes, which exceeds total-size-limit=$sizeLimit by ${totalSize - sizeLimit} bytes.")
+                .append(newline)
+        }
+        if (added.isNotEmpty()) {
+            message.append("To see which dependency brings a module in, run ")
+                .append("./gradlew $projectPath:dependencyInsight --configuration runtimeClasspath --dependency ${added.first()}")
+                .append(newline)
+        }
+        message.append("The sizes of all jars are in ${actualJars.get().asFile.relativeTo(rootDir)}.").append(newline)
+            .append("If the change is not intended, exclude the dependency or revert the update that caused it. ")
+            .append("If it is intended, run $update, commit $expectedPath, ")
+            .append("and name the added and removed modules, the size change, and the dependency update behind them in the pull request description.")
+        throw GradleException(message.toString())
     }
 }
```

## r2/sonnet-gen-3 (judge 3 code XD)

### Rendered message

```text
The external jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check keeps dependencies, often transitive ones, and growth in the release size from entering the release unnoticed.
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
  total size of all jars is 84.00 MiB (88080384 bytes), which exceeds total-size-limit=87031808 (83.00 MiB (87031808 bytes))
To see which dependency brings in an added module, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
To see which jars take the space, read src/dist/build/dist/release_jars.csv, which lists the size in bytes and the name of every jar in the release.
If the change is not intended, revert the dependency update, or exclude the dependency, that caused it. If it is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, commit src/dist/src/dist/expected_release_artifacts.txt, and name the changed modules or the new total size, and the dependency update behind them, in the pull request description. The update sets total-size-limit to the current total size plus 5 MiB, rounded up to a whole MiB.
```

### Reader reply

```markdown
**1. Failure:** The release-dependency check failed. It compares release jars against `expected_release_artifacts.txt` and caps total size, so new transitive dependencies or growth can't slip in silently. Here `org.example:foo` (`foo-1.2.jar`, 1 MiB) was added, bringing the total to 84.00 MiB, over the 83.00 MiB limit.

**2. Change:** Added `foo-1.2.jar`. The output doesn't show whether it's direct or transitive, or the prior total.

**3. Next:**
```
./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
```
Then read `src/dist/build/dist/release_jars.csv` for jar sizes.

**4. If intended:** run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit `expected_release_artifacts.txt`. By the stated rule, the limit becomes 89 MiB (84 + 5). **If not:** revert or exclude the dependency that brought in `foo`.

**5. PR description:** Name `org.example:foo`, the new 84.00 MiB total, the responsible dependency update, and the new limit.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -23,6 +23,7 @@
 import com.github.vlsi.gradle.git.dsl.gitignore
 import com.github.vlsi.gradle.properties.dsl.props
 import org.gradle.api.internal.TaskOutputsInternal
+import java.util.Locale
 
 plugins {
     id("build-logic.build-params")
@@ -271,7 +272,44 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        fun sizeText(bytes: Long) = "%.2f MiB (%d bytes)".format(Locale.ROOT, bytes.toDouble() / mib, bytes)
+
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val message = buildString {
+            append("The external jars of the binary release do not match ").append(expectedPath).append(". ")
+            append("The check keeps dependencies, often transitive ones, and growth in the release size from entering the release unnoticed.")
+            for (module in added) {
+                val jars = jarsByModule.getValue(module)
+                append(newline).append("  + ").append(module).append(" (")
+                    .append(jars.joinToString { "${it.file.name}, ${it.file.length()} bytes" }).append(')')
+            }
+            for (module in removed) {
+                append(newline).append("  - ").append(module)
+            }
+            if (totalSize > sizeLimit) {
+                append(newline).append("  total size of all jars is ").append(sizeText(totalSize))
+                    .append(", which exceeds total-size-limit=").append(sizeLimit).append(" (").append(sizeText(sizeLimit)).append(')')
+            }
+            if (added.isNotEmpty()) {
+                // A module key is group:module, optionally followed by :classifier or @extension
+                val firstAdded = added.first().substringBefore('@').split(':').take(2).joinToString(":")
+                append(newline).append("To see which dependency brings in an added module, run ./gradlew ")
+                    .append(projectPath).append(":dependencyInsight --configuration runtimeClasspath --dependency ").append(firstAdded)
+            }
+            if (totalSize > sizeLimit) {
+                append(newline).append("To see which jars take the space, read ")
+                    .append(actualJars.get().asFile.relativeTo(rootDir)).append(", which lists the size in bytes and the name of every jar in the release.")
+            }
+            if (removed.isNotEmpty()) {
+                append(newline).append("A removed module is no longer on runtimeClasspath of ").append(projectPath)
+                    .append("; check whether a dependency update or an exclude dropped it.")
+            }
+            append(newline).append("If the change is not intended, revert the dependency update, or exclude the dependency, that caused it. ")
+            append("If it is intended, run ./gradlew ").append(path).append(" -PupdateExpectedJars, commit ").append(expectedPath)
+                .append(", and name the changed modules or the new total size, and the dependency update behind them, in the pull request description. ")
+            append("The update sets total-size-limit to the current total size plus ").append(releaseJarsSizeHeadroom / mib).append(" MiB, rounded up to a whole MiB.")
+        }
+        throw GradleException(message)
     }
 }
```

## r2/sonnet-gen2-1 (judge 3 code XO)

### Rendered message

```text
The external jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings in an added module, run:
  ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The total size of the jars is 88080384 bytes (84 MiB), which exceeds total-size-limit=87031808 (83 MiB) in src/dist/src/dist/expected_release_artifacts.txt. The largest jars now:
  12582912 bcprov-jdk18on-1.78.jar
  9437184 groovy-4.0.21.jar
  5242880 jmeter-core.jar
  4194304 xstream-1.4.20.jar
  3145728 rhino-1.7.14.jar
  2097152 httpclient-4.5.14.jar
  2097152 caffeine-3.1.8.jar
  1572864 jackson-databind-2.17.0.jar
  1048576 foo-1.2.jar
  1048576 xalan-2.7.3.jar
If the module changes are not intended, exclude the dependency or revert the update that caused them.
If the growth is not intended, revert the update that grew the jars.
If the changes are intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, which rewrites src/dist/src/dist/expected_release_artifacts.txt and raises total-size-limit, then commit the file. Name the added and removed modules, the size growth, and the dependency update in the pull request description.
```

### Reader reply

```markdown
**1. Failure:** `verifyReleaseDependencies` failed because the release's external jars don't match `expected_release_artifacts.txt`. The check catches unnoticed (often transitive) dependencies and unexpected growth. It found one added module, `org.example:foo` (1,048,576 bytes), which pushed the total to 88,080,384 bytes, over the 87,031,808-byte limit.

**2. Change:** Added `org.example:foo` 1.2. No removals are listed. The output doesn't say which update brought it in, whether it's direct or transitive, or what the previous total was.

**3. Next command** (from the output, not run):
`./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`

**4. If intended:** run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars`, review the rewritten file, and commit it. **If not:** exclude `foo` or revert the update that added it.

**5. PR description:** Name the added module and its size, the size growth and raised limit, and the dependency update responsible. Confirm that update with the insight output first.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,55 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val updateCommand = "./gradlew $path -PupdateExpectedJars"
+        throw GradleException(
+            buildString {
+                appendLine(
+                    "The external jars of the binary release do not match $expectedPath. " +
+                        "The check catches dependencies that enter the release unnoticed, often transitively, " +
+                        "and unexpected growth of the release."
+                )
+                for (module in added) {
+                    val bytes = jarsByModule.getValue(module).sumOf { it.file.length() }
+                    appendLine("  + $module (${jarsByModule.getValue(module).joinToString { it.file.name }}, $bytes bytes)")
+                }
+                for (module in removed) {
+                    appendLine("  - $module")
+                }
+                if (added.isNotEmpty()) {
+                    appendLine("To see which dependency brings in an added module, run:")
+                    for (module in added) {
+                        val (group, name) = module.split(':')
+                        appendLine("  ./gradlew $projectPath:dependencyInsight --configuration runtimeClasspath --dependency $group:$name")
+                    }
+                }
+                if (removed.isNotEmpty()) {
+                    appendLine("A removed module is no longer on runtimeClasspath of $projectPath. Find the dependency change that dropped it.")
+                }
+                if (totalSize > sizeLimit) {
+                    appendLine(
+                        "The total size of the jars is $totalSize bytes (${totalSize / mib} MiB), which exceeds " +
+                            "total-size-limit=$sizeLimit (${sizeLimit / mib} MiB) in $expectedPath. The largest jars now:"
+                    )
+                    artifacts.sortedByDescending { it.file.length() }.take(10).forEach {
+                        appendLine("  ${it.file.length()} ${it.file.name}")
+                    }
+                }
+                appendLine("If the module changes are not intended, exclude the dependency or revert the update that caused them.")
+                if (totalSize > sizeLimit) {
+                    appendLine("If the growth is not intended, revert the update that grew the jars.")
+                }
+                append(
+                    "If the changes are intended, run $updateCommand, which rewrites $expectedPath" +
+                        (if (totalSize > sizeLimit) " and raises total-size-limit" else "") +
+                        ", then commit the file. " +
+                        "Name the added and removed modules" +
+                        (if (totalSize > sizeLimit) ", the size growth," else "") +
+                        " and the dependency update in the pull request description."
+                )
+            }
+        )
     }
 }
```

## r2/sonnet-gen2-2 (judge 3 code XR)

### Rendered message

```text
The external jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.
Modules in the release but not in the file:
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings in a module, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The total size of all jars in the release, JMeter jars included, is 88080384 bytes (84 MiB), which exceeds total-size-limit=87031808 (83 MiB) in src/dist/src/dist/expected_release_artifacts.txt. The largest jars now:
  12582912 bcprov-jdk18on-1.78.jar
  9437184 groovy-4.0.21.jar
  5242880 jmeter-core.jar
  4194304 xstream-1.4.20.jar
  3145728 rhino-1.7.14.jar
If the change is not intended, revert the dependency update that caused it or exclude the module. If it is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, which also sets total-size-limit to the current total size plus 5 MiB. Commit the updated file, and name the added and removed modules, the size growth, and the dependency update in the pull request description so a reviewer can check them.
```

### Reader reply

```markdown
1. **Failed:** the release-dependency check, which catches unnoticed (often transitive) dependencies and unexpected release growth. It found an unlisted module, `org.example:foo` (1 MiB). The total size, 88080384 bytes, exceeds the limit of 87031808 by exactly 1 MiB.

2. **Changed:** `org.example:foo` 1.2 was added. The output lists no removals. It doesn't say which dependency update introduced it or what the previous total was.

3. **Next:** `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`

4. **If unintended:** revert the update that brings in foo, or exclude the module. **If intended:** run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars`, then commit the updated expected-artifacts file. This also sets the size limit to the current total plus 5 MiB, so review that value.

5. **PR description:** name the added module, the dependency update that caused it, the size growth, and the new limit.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,43 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        fun describe(module: String) = jarsByModule.getValue(module).joinToString { "${it.file.name}, ${it.file.length()} bytes" }
+        val message = buildString {
+            append("The external jars of the binary release do not match $expectedPath. ")
+            append("The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.")
+            append(newline)
+            if (added.isNotEmpty()) {
+                append("Modules in the release but not in the file:").append(newline)
+                for (module in added) {
+                    append("  + $module (${describe(module)})").append(newline)
+                }
+                val coordinates = added.first().substringBefore('@').split(':').take(2).joinToString(":")
+                append("To see which dependency brings in a module, run ")
+                append("./gradlew $projectPath:dependencyInsight --configuration runtimeClasspath --dependency $coordinates")
+                append(newline)
+            }
+            if (removed.isNotEmpty()) {
+                append("Modules in the file but not in the release:").append(newline)
+                for (module in removed) {
+                    append("  - $module").append(newline)
+                }
+            }
+            if (totalSize > sizeLimit) {
+                append("The total size of all jars in the release, JMeter jars included, is $totalSize bytes (${totalSize / mib} MiB), ")
+                append("which exceeds total-size-limit=$sizeLimit (${sizeLimit / mib} MiB) in $expectedPath. The largest jars now:")
+                append(newline)
+                for (artifact in artifacts.sortedByDescending { it.file.length() }.take(5)) {
+                    append("  ${artifact.file.length()} ${artifact.file.name}").append(newline)
+                }
+            }
+            append("If the change is not intended, revert the dependency update that caused it or exclude the module. ")
+            append("If it is intended, run ./gradlew $path -PupdateExpectedJars, which also sets total-size-limit ")
+            append("to the current total size plus ${releaseJarsSizeHeadroom / mib} MiB. ")
+            append("Commit the updated file, and name the added and removed modules, the size growth, ")
+            append("and the dependency update in the pull request description so a reviewer can check them.")
+        }
+        throw GradleException(message)
     }
 }
```

## r2/sonnet-gen2-3 (judge 3 code XK)

### Rendered message

```text
The external jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.
  + org.example:foo (foo-1.2.jar, 1048576 bytes) is in the release and not in the file
To see which dependency brings in an added module, run:
  ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The total size of all jars is 88080384 bytes (84.0 MiB), which exceeds total-size-limit=87031808 (83.0 MiB) in src/dist/src/dist/expected_release_artifacts.txt. The largest jars now:
  12582912 bcprov-jdk18on-1.78.jar
  9437184 groovy-4.0.21.jar
  5242880 jmeter-core.jar
  4194304 xstream-1.4.20.jar
  3145728 rhino-1.7.14.jar
If an added or removed module is not intended, exclude the dependency or revert the update that changed it. If the growth is not intended, revert the update that grew the jars. If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, which also resets total-size-limit= to the current total size plus 5 MiB, and commit src/dist/src/dist/expected_release_artifacts.txt. In the pull request description, name the modules added or removed, the size growth, and the dependency update behind them.
```

### Reader reply

```markdown
**1. Failure:** The release's external jars no longer match `expected_release_artifacts.txt`, and their total size exceeds the limit. The check catches dependencies that enter the release unnoticed, often transitively, and unplanned growth.

**2. Change:** `org.example:foo` (foo-1.2.jar, 1,048,576 bytes) was added. The total is now 88,080,384 bytes, 1,048,576 over the 87,031,808-byte limit. The output doesn't give the previous total, identify the dependency update, or report any removals.

**3. Next command (not run):**
`./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`

**4. If intended:** Run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars`, then commit `expected_release_artifacts.txt`. This also raises the limit to 93,323,264 bytes, about 5 MiB above the current total, so review that. **If not:** exclude `org.example:foo` or revert the update that added it.

**5. PR description:** Name `org.example:foo` as added, the 1 MiB size growth, and the dependency update that brought it in. Find that update with the insight command first.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,46 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        fun formatMib(bytes: Long) = "%.1f MiB".format(java.util.Locale.ROOT, bytes.toDouble() / mib)
+        throw GradleException(
+            buildString {
+                appendLine(
+                    "The external jars of the binary release do not match $expectedPath. " +
+                        "The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release."
+                )
+                for (module in added) {
+                    val jar = jarsByModule.getValue(module).first().file
+                    appendLine("  + $module (${jar.name}, ${jar.length()} bytes) is in the release and not in the file")
+                }
+                for (module in removed) {
+                    appendLine("  - $module is in the file and not in the release")
+                }
+                if (added.isNotEmpty()) {
+                    appendLine("To see which dependency brings in an added module, run:")
+                    for (module in added) {
+                        val coordinates = module.substringBefore('@').split(':').take(2).joinToString(":")
+                        appendLine("  ./gradlew $projectPath:dependencyInsight --configuration runtimeClasspath --dependency $coordinates")
+                    }
+                }
+                if (totalSize > sizeLimit) {
+                    appendLine(
+                        "The total size of all jars is $totalSize bytes (${formatMib(totalSize)}), which exceeds " +
+                            "$sizeLimitPrefix$sizeLimit (${formatMib(sizeLimit)}) in $expectedPath. The largest jars now:"
+                    )
+                    for (artifact in artifacts.sortedByDescending { it.file.length() }.take(5)) {
+                        appendLine("  ${artifact.file.length()} ${artifact.file.name}")
+                    }
+                }
+                append(
+                    "If an added or removed module is not intended, exclude the dependency or revert the update that changed it. " +
+                        "If the growth is not intended, revert the update that grew the jars. " +
+                        "If the change is intended, run ./gradlew $path -PupdateExpectedJars, which also resets $sizeLimitPrefix " +
+                        "to the current total size plus ${releaseJarsSizeHeadroom / mib} MiB, and commit $expectedPath. " +
+                        "In the pull request description, name the modules added or removed, the size growth, and the dependency update behind them."
+                )
+            }
+        )
     }
 }
```

## Skills each revision writer invoked

```text
haiku-gen-1     cost=0.016806010000000003 turns=11 error=False diff_lines=30 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
haiku-gen-2     cost=0.013733350000000002 turns=7 error=False diff_lines=41 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
haiku-gen-3     cost=0.01761252 turns=9 error=False diff_lines=44 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
sonnet-gen-1    cost=0.2085841 turns=10 error=False diff_lines=33 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
sonnet-gen-2    cost=0.19455869999999997 turns=8 error=False diff_lines=38 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
sonnet-gen-3    cost=0.21901230000000002 turns=10 error=False diff_lines=56 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
haiku-gen2-1    cost=0.017709410000000002 turns=9 error=False diff_lines=57 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
haiku-gen2-2    cost=0.019507439999999997 turns=10 error=False diff_lines=55 skills=['telemetry-authoring', 'english-developer-style'] reads=['telemetry-authoring/references/jvm.md']
haiku-gen2-3    cost=0.01771655 turns=11 error=False diff_lines=37 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
sonnet-gen2-1   cost=0.188927 turns=8 error=False diff_lines=59 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
sonnet-gen2-2   cost=0.1898311 turns=8 error=False diff_lines=47 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
sonnet-gen2-3   cost=0.21244979999999997 turns=11 error=False diff_lines=50 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
haiku-gen3-1    cost=0.01854846 turns=11 error=False diff_lines=38 skills=['telemetry-authoring', 'english-developer-style'] reads=['telemetry-authoring/references/jvm.md']
haiku-gen3-2    cost=0.01663868 turns=9 error=False diff_lines=39 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
haiku-gen3-3    cost=0.01946368 turns=10 error=False diff_lines=50 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
sonnet-gen3-1   cost=0.20023380000000002 turns=8 error=False diff_lines=51 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
sonnet-gen3-2   cost=0.22414800000000001 turns=13 error=False diff_lines=61 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
sonnet-gen3-3   cost=0.19165030000000002 turns=8 error=False diff_lines=49 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
```

## Example of arm gen3

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
The external jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check
catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings it in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The total size of external jars is 88080384 bytes (84 MiB), which exceeds total-size-limit=87031808 (83 MiB) in
src/dist/src/dist/expected_release_artifacts.txt. The largest jars now:
  12582912 bcprov-jdk18on-1.78.jar
  ...
If the module is not intended, exclude it or revert the dependency update that brought it in. If the growth is not
intended, revert the update that grew the jars. If both are intended, run ./gradlew :src:dist:verifyReleaseDependencies
-PupdateExpectedJars, which also raises total-size-limit, commit the file, and name the module, the size growth, and the
dependency update in the pull request description.
```

The examples show what each row looks like, not text to reuse. Every fact in them, down to "external jars", is true of
that check only; check each phrase taken from them against the code the new message reports on.
```

## Judge 4


| code | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 | F10 | F11 | F12 | R1 | R2 | R3 | R4 | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ZA | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | Y | Y | Y | Y | Y | Y | F7: only "1048576 bytes over total-size-limit=87031808"; no jar list, no `release_jars.csv`, no command to find the growth. Reader hedges that `src/dist/src/dist/...` "looks doubled" (the path is correct), but invents nothing. |
| ZB | Y | Y | Y | Y | Y | Y | P | Y | Y | Y | Y | N | Y | Y | Y | Y | F12: "The total size of external jars is 88080384 bytes" is wrong; the code sums every artifact of runtimeClasspath, JMeter jars included. F7: the largest-jars list comes from `jarsByModule`, so it omits JMeter's own jars, which count toward the total. |
| ZC | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | F7 met by "The jar sizes in bytes, by file name, are listed in src/dist/build/dist/release_jars.csv" (a file to compare, no list printed). |
| ZD | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | P | Y | Y | Y | Y | Y | F11: `val (group, name) = module.split(':')` throws IndexOutOfBoundsException for an added artifact keyed by file name (no colon), replacing the message with a crash; "If the module changes are not intended" is printed even when only the size limit fails. |
| ZE | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Removed branch gets its own list and `dependencies` command; colon guard before dependencyInsight. Minor: "If the growth is not intended" is printed unconditionally. |
| ZF | Y | Y | Y | Y | Y | Y | P | Y | Y | Y | Y | N | P | Y | Y | Y | F12: "The total size of external jars is 88080384 bytes (84.0 MiB)" is wrong; JMeter jars are in the total. F7: the list filters out `ProjectComponentIdentifier` artifacts, so jmeter-core.jar (5242880) is missing. R1: reader repeats "external jars total 84.0 MiB" from the output. |
| ZG | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | "The total size of all jars, JMeter jars included" plus the top five and a pointer to `release_jars.csv`. |
| ZH | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | No per-module jar size and the PR advice omits the dependency update; neither falls below Y. Reader hedges that the path "looks doubled", invents nothing. |
| ZI | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | P | Y | Y | Y | Y | Y | F11: removed branch runs `module.split(':')[1]`, which throws for a module keyed by file name; the added branch passes the raw key (with classifier or `@ext`) to `--dependency`. Reader's "The output doesn't name the task" is odd but not an invention. |
| ZJ | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | "The total size of all jars", top five incl. jmeter-core.jar, headroom stated; every added module gets its own insight command. |
| ZK | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | "all jars in the release, JMeter jars included"; insight command only for the first added module (fine here). |
| ZL | Y | Y | Y | Y | Y | P | N | Y | Y | Y | P | Y | Y | Y | Y | Y | F6: "run ./gradlew :src:dist:dependencies --configuration runtimeClasspath", module not filled in, not dependencyInsight. F7: nothing points at the jars that grew. F11: the "added module" command line is printed on every branch, removed-only and size-only included. |

Best three:

- ZG: every fact the scenario needs is present and correct, the total is labeled "all jars, JMeter jars included", and the
  largest jars are listed with a pointer to the full `release_jars.csv`.
- ZE: complete and correct, states the 5 MiB headroom of the accept command, and gives the removed branch its own list
  and a runnable `dependencies` command.
- ZJ: complete and correct with the headroom stated, a size per added jar, and an insight command for every added
  module; the reader computed the new limit correctly from it.

Worst three:

- ZL: points at `:src:dist:dependencies` with no module instead of dependencyInsight, gives nothing to find the jars that
  grew, and prints the added-module hint on every branch.
- ZF: calls the total "external jars", which is false, and its largest-jars list drops JMeter's own jars, so the reader
  passed the false claim on.
- ZB: the same false "external jars" total and the same external-only list, though otherwise complete.

### Key

| code | run |
| --- | --- |
| ZA | r2/haiku-gen3-1 |
| ZB | r2/haiku-gen2-2 |
| ZC | r2/haiku-gen3-2 |
| ZD | r2/sonnet-gen2-1 |
| ZE | r2/sonnet-gen3-1 |
| ZF | r2/sonnet-gen3-2 |
| ZG | r2/sonnet-gen3-3 |
| ZH | r2/haiku-gen3-3 |
| ZI | r2/haiku-gen2-1 |
| ZJ | r2/sonnet-gen2-3 |
| ZK | r2/sonnet-gen2-2 |
| ZL | r2/haiku-gen2-3 |

### Aggregates

| run | code | ledger /12 | F7 F11 F12 | reader /4 |
| --- | --- | ---: | --- | ---: |
| haiku-gen2-1 | ZI | 11.5 | Y P Y | 4 |
| haiku-gen2-2 | ZB | 10.5 | P Y N | 4 |
| haiku-gen2-3 | ZL | 10 | N P Y | 4 |
| haiku-gen3-1 | ZA | 11 | N Y Y | 4 |
| haiku-gen3-2 | ZC | 12 | Y Y Y | 4 |
| haiku-gen3-3 | ZH | 12 | Y Y Y | 4 |
| sonnet-gen2-1 | ZD | 11.5 | Y P Y | 4 |
| sonnet-gen2-2 | ZK | 12 | Y Y Y | 4 |
| sonnet-gen2-3 | ZJ | 12 | Y Y Y | 4 |
| sonnet-gen3-1 | ZE | 12 | Y Y Y | 4 |
| sonnet-gen3-2 | ZF | 10.5 | P Y N | 3.5 |
| sonnet-gen3-3 | ZG | 12 | Y Y Y | 4 |

| model | arm | mean ledger /12 | all 12 | mean reader /4 | F12 Y |
| --- | --- | ---: | ---: | ---: | ---: |
| haiku | gen2 | 10.7 | 0/3 | 4.0 | 2/3 |
| haiku | gen3 | 11.7 | 2/3 | 4.0 | 3/3 |
| sonnet | gen2 | 11.8 | 2/3 | 4.0 | 3/3 |
| sonnet | gen3 | 11.5 | 2/3 | 3.8 | 2/3 |

## r2/haiku-gen3-1 (judge 4 code ZA)

### Rendered message

```text
The external jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.
  Modules in the release but missing from src/dist/src/dist/expected_release_artifacts.txt: org.example:foo
  The total size of the jars is 88080384 bytes, which is 1048576 bytes over total-size-limit=87031808 in src/dist/src/dist/expected_release_artifacts.txt
To find the dependency that brings in org.example:foo, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
If a module or the size growth is not intended, exclude the dependency or revert the dependency update that brought it in. If all of it is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, commit src/dist/src/dist/expected_release_artifacts.txt, and name the modules, the size change, and the dependency update in the pull request description.
```

### Reader reply

```markdown
1. **Failed:** the release dependency check. It compares the release's external jars to `expected_release_artifacts.txt`, catching dependencies (often transitive) that enter unnoticed and unplanned size growth. Here, `org.example:foo` is unexpected, and the jars are 1,048,576 bytes over the limit.

2. **Changed:** Unknown. The output doesn't say which update added `org.example:foo`, and I can't see your diff.

3. **Next:** `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`

4. **If intended:** run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars`, then commit the expected file. **If not:** exclude `org.example:foo` or revert the update that brought it in.

5. **PR description:** the added module, the 1,048,576-byte increase, and the responsible update. The output doesn't say whether that list is complete.

The paths in the output read `src/dist/src/dist/...`, which looks doubled. I couldn't verify them, so confirm the real path before running commands.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,34 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val reasons = mutableListOf<String>()
+        if (added.isNotEmpty()) {
+            reasons += "Modules in the release but missing from $expectedPath: ${added.joinToString()}"
+        }
+        if (removed.isNotEmpty()) {
+            reasons += "Modules listed in $expectedPath but missing from the release: ${removed.joinToString()}"
+        }
+        if (totalSize > sizeLimit) {
+            reasons += "The total size of the jars is $totalSize bytes, which is ${totalSize - sizeLimit} bytes over " +
+                "$sizeLimitPrefix$sizeLimit in $expectedPath"
+        }
+        val firstAdded = added.firstOrNull()
+        throw GradleException(
+            "The external jars of the binary release do not match $expectedPath. " +
+                "The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.\n" +
+                reasons.joinToString("\n") { "  $it" } + "\n" +
+                (if (firstAdded != null) {
+                    "To find the dependency that brings in $firstAdded, run " +
+                        "./gradlew $projectPath:dependencyInsight --configuration runtimeClasspath --dependency $firstAdded\n"
+                } else {
+                    ""
+                }) +
+                "If a module or the size growth is not intended, exclude the dependency or revert the dependency update " +
+                "that brought it in. If all of it is intended, run ./gradlew $projectPath:verifyReleaseDependencies " +
+                "-PupdateExpectedJars, commit $expectedPath, and name the modules, the size change, and the dependency " +
+                "update in the pull request description."
+        )
     }
 }
```

## r2/haiku-gen3-2 (judge 4 code ZC)

### Rendered message

```text
The external modules or the total jar size of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt.
The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.
Added modules, not listed in src/dist/src/dist/expected_release_artifacts.txt:
  org.example:foo
  To see which dependency brings it in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The total size of the jars is 88080384 bytes (about 84 MiB), which exceeds total-size-limit=87031808 in src/dist/src/dist/expected_release_artifacts.txt.
The jar sizes in bytes, by file name, are listed in src/dist/build/dist/release_jars.csv.
If a change is not intended, exclude the module or revert the dependency update that brought it in. If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, commit src/dist/src/dist/expected_release_artifacts.txt, and name the modules, the size growth, and the dependency update in the pull request description.
```

### Reader reply

```markdown
**1. Failure:** The `src/dist` release check failed. Unlisted module `org.example:foo` entered the release, and the jars total 88,080,384 bytes, 1 MiB over the 87,031,808-byte limit. The check catches dependencies that enter unnoticed, often transitively, and unplanned size growth.

**2. Change:** The output shows only the new module and the size overage. It doesn't say what caused either, or what the previous size was.

**3. Next:** `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`. Per-jar sizes are in `src/dist/build/dist/release_jars.csv`.

**4. If intended:** Run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit `src/dist/src/dist/expected_release_artifacts.txt`. **If not:** Exclude `org.example:foo` or revert the update that brought it in.

**5. PR description:** Name `org.example:foo`, the 1 MiB size growth, and the dependency update responsible. The output doesn't identify that update, so confirm it with `dependencyInsight` first.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,35 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val lines = mutableListOf(
+            "The external modules or the total jar size of the binary release do not match $expectedPath.",
+            "The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.",
+        )
+        if (added.isNotEmpty()) {
+            lines.add("Added modules, not listed in $expectedPath:")
+            for (module in added) {
+                lines.add("  $module")
+                lines.add("  To see which dependency brings it in, run ./gradlew ${projectPath}:dependencyInsight --configuration runtimeClasspath --dependency $module")
+            }
+        }
+        if (removed.isNotEmpty()) {
+            lines.add("Removed modules, listed in $expectedPath but absent from the release:")
+            removed.forEach { lines.add("  $it") }
+        }
+        if (totalSize > sizeLimit) {
+            lines.add(
+                "The total size of the jars is $totalSize bytes (about ${totalSize / mib} MiB), " +
+                    "which exceeds total-size-limit=$sizeLimit in $expectedPath."
+            )
+            lines.add("The jar sizes in bytes, by file name, are listed in ${actualJars.get().asFile.relativeTo(rootDir)}.")
+        }
+        lines.add(
+            "If a change is not intended, exclude the module or revert the dependency update that brought it in. " +
+                "If the change is intended, run ./gradlew $path -PupdateExpectedJars, commit $expectedPath, " +
+                "and name the modules, the size growth, and the dependency update in the pull request description."
+        )
+        throw GradleException(lines.joinToString(newline))
     }
 }
```

## r2/haiku-gen3-3 (judge 4 code ZH)

### Rendered message

```text
Release dependencies differ from src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.
Modules in the release but not in src/dist/src/dist/expected_release_artifacts.txt:
  + org.example:foo
The total size of all jars in the release is 88080384 bytes (84.0 MiB), which exceeds total-size-limit=87031808 bytes (83.0 MiB) in src/dist/src/dist/expected_release_artifacts.txt. The largest jars now:
  12582912 bcprov-jdk18on-1.78.jar
  9437184 groovy-4.0.21.jar
  5242880 jmeter-core.jar
  4194304 xstream-1.4.20.jar
  3145728 rhino-1.7.14.jar
To see which dependency brings in an added module, run:
  ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
If a change is not intended, exclude an added module or restore a removed one, and revert the dependency update that caused it.
If the growth is not intended, revert the update that grew the jars.
If all of it is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars. It rewrites src/dist/src/dist/expected_release_artifacts.txt, including total-size-limit. Commit the file, and name the added or removed modules and the size growth in the pull request description.
```

### Reader reply

```markdown
1. The release's dependency set doesn't match `expected_release_artifacts.txt`. The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth in release size.

2. One module was added: `org.example:foo`. The total is 88080384 bytes, exactly 1 MiB over the 87031808-byte limit. The output doesn't say which update added `foo`, its version, or the previous total.

3. Next: `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`. I haven't run it.

4. If unintended, revert the update that added `foo` or exclude it. If intended, run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit the rewritten file. The output's path, `src/dist/src/dist/...`, looks doubled, so confirm it before committing.

5. Name `org.example:foo` as added, give the size growth and new limit, and explain why the update pulled it in.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,46 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val sizeExceeded = totalSize > sizeLimit
+        val addedSorted = added.sortedWith(caseInsensitive)
+        fun mibText(bytes: Long) = "%.1f MiB".format(java.util.Locale.ROOT, bytes.toDouble() / mib)
+
+        val report = mutableListOf(
+            "Release dependencies differ from $expectedPath. The check catches dependencies that enter the release " +
+                "unnoticed, often transitively, and unexpected growth of the release.",
+        )
+        if (addedSorted.isNotEmpty()) {
+            report += "Modules in the release but not in $expectedPath:"
+            report += addedSorted.map { "  + $it" }
+        }
+        if (removed.isNotEmpty()) {
+            report += "Modules in $expectedPath but not in the release:"
+            report += removed.map { "  - $it" }
+        }
+        if (sizeExceeded) {
+            report += "The total size of all jars in the release is $totalSize bytes (${mibText(totalSize)}), which " +
+                "exceeds total-size-limit=$sizeLimit bytes (${mibText(sizeLimit)}) in $expectedPath. The largest jars now:"
+            report += artifacts.sortedByDescending { it.file.length() }.take(5)
+                .map { "  ${it.file.length()} ${it.file.name}" }
+        }
+        val insightCommands = addedSorted.filter { ':' in it }.map {
+            val coordinates = it.substringBefore('@').split(':').take(2).joinToString(":")
+            "  ./gradlew $projectPath:dependencyInsight --configuration runtimeClasspath --dependency $coordinates"
+        }
+        if (insightCommands.isNotEmpty()) {
+            report += "To see which dependency brings in an added module, run:"
+            report += insightCommands
+        }
+        report += "If a change is not intended, exclude an added module or restore a removed one, and revert the " +
+            "dependency update that caused it."
+        if (sizeExceeded) {
+            report += "If the growth is not intended, revert the update that grew the jars."
+        }
+        report += "If all of it is intended, run ./gradlew $path -PupdateExpectedJars. It rewrites $expectedPath, " +
+            "including total-size-limit. Commit the file, and name the added or removed modules and the size growth " +
+            "in the pull request description."
+        throw GradleException(report.joinToString(newline))
     }
 }
```

## r2/sonnet-gen3-1 (judge 4 code ZE)

### Rendered message

```text
The external jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.
Modules in the release but not in src/dist/src/dist/expected_release_artifacts.txt:
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
    To see which dependency brings it in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The total size of the jars is 88080384 bytes (84 MiB), which exceeds total-size-limit=87031808 (83 MiB) in src/dist/src/dist/expected_release_artifacts.txt. The largest jars now:
  12582912 bcprov-jdk18on-1.78.jar
  9437184 groovy-4.0.21.jar
  5242880 jmeter-core.jar
  4194304 xstream-1.4.20.jar
  3145728 rhino-1.7.14.jar
  2097152 httpclient-4.5.14.jar
  2097152 caffeine-3.1.8.jar
  1572864 jackson-databind-2.17.0.jar
  1048576 foo-1.2.jar
  1048576 xalan-2.7.3.jar
If a module is not intended, exclude it or revert the dependency update that brought it in.
If the growth is not intended, revert the dependency update that grew the jars.
If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, which also resets total-size-limit= to the current total size plus 5 MiB, and commit src/dist/src/dist/expected_release_artifacts.txt. Name the added and removed modules, the size change, and the dependency update in the pull request description.
```

### Reader reply

```markdown
1. **Failed:** the release-artifact check. The release jars no longer match `expected_release_artifacts.txt`. The check catches unreviewed dependencies, often transitive ones, and unexpected size growth.

2. **Changed:** new module `org.example:foo` (foo-1.2.jar, 1 MiB). The total of 88080384 bytes exceeds the 87031808-byte limit by exactly foo's size. The output shows no removals.

3. **Next:** `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`. The output doesn't name the dependency that brings in foo.

4. **If intended:** run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit the expected-artifacts file. The limit resets to 93323264 bytes. **If not:** exclude foo or revert the update that brought it in.

5. **PR description:** foo added, the size change (+1048576 bytes), the responsible dependency update, and the new limit if it was reset.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,47 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val insightTask = "$projectPath:dependencyInsight --configuration runtimeClasspath"
+        throw GradleException(
+            buildString {
+                append("The external jars of the binary release do not match $expectedPath. ")
+                appendLine("The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.")
+                if (added.isNotEmpty()) {
+                    appendLine("Modules in the release but not in $expectedPath:")
+                    for (module in added) {
+                        val jars = jarsByModule.getValue(module)
+                        appendLine("  + $module (${jars.joinToString { "${it.file.name}, ${it.file.length()} bytes" }})")
+                        if (!module.contains(':')) {
+                            continue
+                        }
+                        val coordinates = module.substringBefore('@').split(':').take(2).joinToString(":")
+                        appendLine("    To see which dependency brings it in, run ./gradlew $insightTask --dependency $coordinates")
+                    }
+                }
+                if (removed.isNotEmpty()) {
+                    appendLine("Modules in $expectedPath but not in the release:")
+                    for (module in removed) {
+                        appendLine("  - $module")
+                    }
+                    appendLine("To see what the release resolves now, run ./gradlew $projectPath:dependencies --configuration runtimeClasspath")
+                }
+                if (totalSize > sizeLimit) {
+                    appendLine(
+                        "The total size of the jars is $totalSize bytes (${totalSize / mib} MiB), which exceeds " +
+                            "$sizeLimitPrefix$sizeLimit (${sizeLimit / mib} MiB) in $expectedPath. The largest jars now:"
+                    )
+                    for (artifact in artifacts.sortedByDescending { it.file.length() }.take(10)) {
+                        appendLine("  ${artifact.file.length()} ${artifact.file.name}")
+                    }
+                }
+                appendLine("If a module is not intended, exclude it or revert the dependency update that brought it in.")
+                appendLine("If the growth is not intended, revert the dependency update that grew the jars.")
+                append("If the change is intended, run ./gradlew $path -PupdateExpectedJars, which also resets $sizeLimitPrefix to the current total size ")
+                append("plus ${releaseJarsSizeHeadroom / mib} MiB, and commit $expectedPath. ")
+                append("Name the added and removed modules, the size change, and the dependency update in the pull request description.")
+            }
+        )
     }
 }
```

## r2/sonnet-gen3-2 (judge 4 code ZF)

### Rendered message

```text
The external jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.
Modules in the release that the file does not list:
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings a module in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The total size of external jars is 88080384 bytes (84.0 MiB), which exceeds total-size-limit=87031808 (83.0 MiB) in src/dist/src/dist/expected_release_artifacts.txt. The largest jars now:
  12582912 bcprov-jdk18on-1.78.jar
  9437184 groovy-4.0.21.jar
  4194304 xstream-1.4.20.jar
  3145728 rhino-1.7.14.jar
  2097152 httpclient-4.5.14.jar
If a change in the modules is not intended, exclude the module or revert the dependency update that added or removed it. If the growth is not intended, revert the update that grew the jars. If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, which also resets total-size-limit, commit src/dist/src/dist/expected_release_artifacts.txt, and name the modules, the size growth, and the dependency update in the pull request description.
```

### Reader reply

```markdown
**1. Failure:** `verifyReleaseDependencies` failed. Module `org.example:foo` (1 MiB) is missing from `expected_release_artifacts.txt`, and external jars total 84.0 MiB, over the 83.0 MiB limit. The check catches unnoticed dependencies, often transitive ones, and unexpected release growth.

**2. Change:** The update appears to add `org.example:foo`. The overage equals foo's 1048576 bytes exactly. I can't see the diff, so I can't confirm nothing else changed.

**3. Next:** `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`. I can't run it here.

**4. If intended:** Run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit `src/dist/src/dist/expected_release_artifacts.txt`. The output doesn't give the new limit. **If not:** exclude foo or revert the update that added it.

**5. PR description:** Name `org.example:foo` (foo-1.2.jar), the 1 MiB growth (total now 84.0 MiB), the dependency that brings it in (once `dependencyInsight` shows it), and the limit change.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -23,6 +23,7 @@
 import com.github.vlsi.gradle.git.dsl.gitignore
 import com.github.vlsi.gradle.properties.dsl.props
 import org.gradle.api.internal.TaskOutputsInternal
+import java.util.Locale
 
 plugins {
     id("build-logic.build-params")
@@ -271,7 +272,49 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        fun formatMib(bytes: Long) = String.format(Locale.ROOT, "%.1f MiB", bytes.toDouble() / mib)
+
+        val message = buildString {
+            append("The external jars of the binary release do not match ").append(expectedPath).append(". ")
+            append("The check catches dependencies that enter the release unnoticed, often transitively, ")
+            append("and unexpected growth of the release.").append(newline)
+            if (added.isNotEmpty()) {
+                append("Modules in the release that the file does not list:").append(newline)
+                for (module in added) {
+                    val jars = jarsByModule.getValue(module)
+                    append("  + ").append(module)
+                        .append(" (").append(jars.joinToString { "${it.file.name}, ${it.file.length()} bytes" }).append(')')
+                        .append(newline)
+                }
+                append("To see which dependency brings a module in, run ./gradlew ").append(projectPath)
+                    .append(":dependencyInsight --configuration runtimeClasspath --dependency ")
+                    .append(added.first().substringBefore('@').split(':').take(2).joinToString(":"))
+                    .append(newline)
+            }
+            if (removed.isNotEmpty()) {
+                append("Modules that the file lists and the release no longer contains:").append(newline)
+                for (module in removed) {
+                    append("  - ").append(module).append(newline)
+                }
+            }
+            if (totalSize > sizeLimit) {
+                append("The total size of external jars is $totalSize bytes (${formatMib(totalSize)}), which exceeds ")
+                    .append("$sizeLimitPrefix$sizeLimit (${formatMib(sizeLimit)}) in ").append(expectedPath)
+                    .append(". The largest jars now:").append(newline)
+                artifacts
+                    .filter { it.id.componentIdentifier !is ProjectComponentIdentifier }
+                    .sortedByDescending { it.file.length() }
+                    .take(5)
+                    .forEach { append("  ${it.file.length()} ${it.file.name}").append(newline) }
+            }
+            append("If a change in the modules is not intended, exclude the module or revert the dependency update ")
+                .append("that added or removed it. If the growth is not intended, revert the update that grew the jars. ")
+                .append("If the change is intended, run ./gradlew $projectPath:verifyReleaseDependencies -PupdateExpectedJars, ")
+                .append("which also resets total-size-limit, commit $expectedPath, and name the modules, ")
+                .append("the size growth, and the dependency update in the pull request description.")
+        }
+        throw GradleException(message)
     }
 }
```

## r2/sonnet-gen3-3 (judge 4 code ZG)

### Rendered message

```text
The external jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.
Modules in the release that src/dist/src/dist/expected_release_artifacts.txt does not list:
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings a module in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The total size of all jars, JMeter jars included, is 88080384 bytes (84 MiB), which exceeds total-size-limit=87031808 (83 MiB) in src/dist/src/dist/expected_release_artifacts.txt. The largest jars now, as listed in src/dist/build/dist/release_jars.csv:
  12582912 bcprov-jdk18on-1.78.jar
  9437184 groovy-4.0.21.jar
  5242880 jmeter-core.jar
  4194304 xstream-1.4.20.jar
  3145728 rhino-1.7.14.jar
If a module is not intended, exclude it or revert the dependency update that brought it in. If the growth is not intended, revert the update that grew the jars. If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, which also resets total-size-limit=, commit src/dist/src/dist/expected_release_artifacts.txt, and name the modules, the size growth, and the dependency update in the pull request description.
```

### Reader reply

```markdown
**1. Failure.** `verifyReleaseDependencies` found that the release jars don't match `expected_release_artifacts.txt`. The check catches dependencies that enter the release unnoticed, often transitively, and unexpected size growth. Here, unlisted `org.example:foo` (1 MiB) pushed the total to 88080384 bytes, over the limit by exactly 1048576 bytes.

**2. Change.** The dependency update added `foo-1.2.jar`. The output doesn't show the previous total or which dependency brought it in.

**3. Next.**
`./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`

**4. Action.** If intended, run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit the updated expected file. If not, exclude foo or revert the update that added it. The output doesn't say whether foo is intended; the dependencyInsight output should show its path.

**5. PR description (if intended).** Name `org.example:foo`, the 1 MiB growth (total now 84 MiB), and the dependency update. Also mention that the update resets `total-size-limit`.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,45 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val updateCommand = "./gradlew $path -PupdateExpectedJars"
+        val message = buildString {
+            append("The external jars of the binary release do not match $expectedPath. ")
+            append("The check catches dependencies that enter the release unnoticed, often transitively, ")
+            append("and unexpected growth of the release.")
+            if (added.isNotEmpty()) {
+                append(newline).append("Modules in the release that $expectedPath does not list:")
+                for (module in added) {
+                    val files = jarsByModule.getValue(module)
+                    append(newline).append("  + $module (${files.joinToString { it.file.name }}, ${files.sumOf { it.file.length() }} bytes)")
+                }
+                val example = added.first().split(':').take(2).joinToString(":")
+                append(newline).append("To see which dependency brings a module in, run ")
+                append("./gradlew $projectPath:dependencyInsight --configuration runtimeClasspath --dependency $example")
+            }
+            if (removed.isNotEmpty()) {
+                append(newline).append("Modules that $expectedPath lists and the release no longer contains:")
+                for (module in removed) {
+                    append(newline).append("  - $module")
+                }
+            }
+            if (totalSize > sizeLimit) {
+                append(newline).append("The total size of all jars, JMeter jars included, is $totalSize bytes (${totalSize / mib} MiB), ")
+                append("which exceeds $sizeLimitPrefix$sizeLimit (${sizeLimit / mib} MiB) in $expectedPath. ")
+                append("The largest jars now, as listed in ${actualJars.get().asFile.relativeTo(rootDir)}:")
+                for (artifact in artifacts.sortedByDescending { it.file.length() }.take(5)) {
+                    append(newline).append("  ${artifact.file.length()} ${artifact.file.name}")
+                }
+            }
+            append(newline)
+            append("If a module is not intended, exclude it or revert the dependency update that brought it in. ")
+            if (totalSize > sizeLimit) {
+                append("If the growth is not intended, revert the update that grew the jars. ")
+            }
+            append("If the change is intended, run $updateCommand, which also resets $sizeLimitPrefix, ")
+            append("commit $expectedPath, and name the modules, the size growth, and the dependency update in the pull request description.")
+        }
+        throw GradleException(message)
     }
 }
```

## Skills each gen4 writer invoked

```text
haiku-gen4-1    cost=0.0158795 turns=8 error=False diff_lines=53 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
haiku-gen4-2    cost=0.018004390000000002 turns=12 error=False diff_lines=39 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
haiku-gen4-3    cost=0.0160556 turns=10 error=False diff_lines=30 skills=['telemetry-authoring', 'english-developer-style'] reads=['telemetry-authoring/references/jvm.md']
sonnet-gen4-1   cost=0.1944302 turns=8 error=False diff_lines=45 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
sonnet-gen4-2   cost=0.19050490000000003 turns=8 error=False diff_lines=55 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
sonnet-gen4-3   cost=0.19312590000000002 turns=8 error=False diff_lines=46 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
```

## Judge 5


| code | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 | F10 | F11 | F12 | R1 | R2 | R3 | R4 | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VA | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| VB | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | P | Y | R3: reader says "Name the changed modules (the output doesn't list them)", though the output lists `+ org.example:foo`. |
| VC | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| VD | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | P | Y | Y | Y | Y | Y | F11: "If a module is not intended…" and "If the growth is not intended…" are printed unconditionally, even when that branch did not fire. |
| VE | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | P | Y | Y | Y | Y | Y | F11: "If a removed module is not intended, restore the dependency that provided it" and the growth advice print in every failure, including this one with no removal. |
| VF | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | Y | Y | Y | Y | Y | Y | F7: only "1048576 bytes over total-size-limit"; no jar list, no file, no command to find which jars grew. |
| VG | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| VH | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| VI | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| VJ | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | P | Y | Y | Y | Y | Y | F11: "If a module is not intended, exclude it…" is printed even for a size-only failure. |
| VK | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| VL | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | P | N | P | Y | Y | Y | F12: "The total size of external jars is 88080384 bytes" is false; the total and the limit cover every runtimeClasspath jar, JMeter's own included (the printed largest-jar list also drops jmeter-core.jar). F11: module and growth advice both unconditional. R1: reader repeats "external jars total 84.0 MiB". |

Best:

- VA: every branch gets its own conditional text, each added module carries its jar, size, and a dependencyInsight command with coordinates stripped of classifier, and the size branch prints MiB and the largest jars.
- VH: separate added, removed, and size sections, insight commands built from clean coordinates, growth advice only when the size branch fires, and it says the accept command rewrites the file including `total-size-limit`.
- VG: conditional advice per branch, including a separate "restore the dependency" line for removals, plus the largest jars and a clean accept command.

Worst:

- VL: it calls the total "the total size of external jars", which is wrong for this check, and the reader passed the false claim on.
- VF: it gives the overflow but nothing that shows which jars caused the growth.
- VE: its fixed advice block tells every reader what to do about a removed module and about growth whether or not either happened.

### Key

| code | run |
| --- | --- |
| VA | sonnet-gen4-1 |
| VB | sonnet-gen4-2 |
| VC | haiku-gen3-2 |
| VD | sonnet-gen3-1 |
| VE | sonnet-gen4-3 |
| VF | haiku-gen3-1 |
| VG | haiku-gen4-1 |
| VH | haiku-gen3-3 |
| VI | haiku-gen4-3 |
| VJ | sonnet-gen3-3 |
| VK | haiku-gen4-2 |
| VL | sonnet-gen3-2 |

### Aggregates

| run | code | ledger /12 | reader /4 |
| --- | --- | ---: | ---: |
| haiku-gen3-1 | VF | 11 | 4 |
| haiku-gen3-2 | VC | 12 | 4 |
| haiku-gen3-3 | VH | 12 | 4 |
| haiku-gen4-1 | VG | 12 | 4 |
| haiku-gen4-2 | VK | 12 | 4 |
| haiku-gen4-3 | VI | 12 | 4 |
| sonnet-gen3-1 | VD | 11.5 | 4 |
| sonnet-gen3-2 | VL | 10.5 | 3.5 |
| sonnet-gen3-3 | VJ | 11.5 | 4 |
| sonnet-gen4-1 | VA | 12 | 4 |
| sonnet-gen4-2 | VB | 12 | 3.5 |
| sonnet-gen4-3 | VE | 11.5 | 4 |

| model | arm | mean ledger /12 | all 12 | mean reader /4 |
| --- | --- | ---: | ---: | ---: |
| haiku | gen3 | 11.7 | 2/3 | 4.0 |
| haiku | gen4 | 12.0 | 3/3 | 4.0 |
| sonnet | gen3 | 11.2 | 0/3 | 3.8 |
| sonnet | gen4 | 11.8 | 2/3 | 3.8 |

## haiku-gen4-1 (judge 5 code VG)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter the release unnoticed, often transitively, and a release that grows past total-size-limit.
Modules added to the release, and not listed in the expected file:
  + org.example:foo
To see which dependency brings a module in, run:
  ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The total size of the jars is 88080384 bytes (about 84 MiB), which exceeds total-size-limit=87031808 in src/dist/src/dist/expected_release_artifacts.txt. The largest jars now:
  12582912 bcprov-jdk18on-1.78.jar
  9437184 groovy-4.0.21.jar
  5242880 jmeter-core.jar
  4194304 xstream-1.4.20.jar
  3145728 rhino-1.7.14.jar
If a module is not intended, exclude it or revert the dependency update that brought it in.
If the growth is not intended, revert the update that grew the jars.
If both are intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, commit src/dist/src/dist/expected_release_artifacts.txt, and name the modules, the size growth, and the dependency updates in the pull request description.
```

### Reader reply

```markdown
**1. Failure:** `verifyReleaseDependencies` failed. It compares the release jars with the expected-artifacts file, catching unnoticed (often transitive) dependencies and size growth. Two problems: the unexpected module `org.example:foo`, and total jar size of 88080384 bytes, 1048576 bytes over the 87031808-byte limit. The output doesn't say which update added `foo` or grew the jars. The expected-file path looks doubled (`src/dist/src/dist/...`); I can't tell whether that's real.

**2. Changed:** Your dependency update added `org.example:foo` and pushed the jars over the size limit. No earlier sizes are shown, so I can't say what grew.

**3. Next:** `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`

**4. If intended:** Run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit the expected-artifacts file. **If not intended:** exclude `foo`, or revert the update that brought it in.

**5. PR description:** Name the added module, the size growth, and the dependency updates responsible.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,49 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val report = StringBuilder()
+        report.append("The jars of the binary release do not match ${expectedFile.relativeTo(rootDir)}. ")
+        report.append("The check catches dependencies that enter the release unnoticed, often transitively, ")
+        report.append("and a release that grows past total-size-limit.").append(newline)
+        if (added.isNotEmpty()) {
+            report.append("Modules added to the release, and not listed in the expected file:").append(newline)
+            added.forEach { report.append("  + $it").append(newline) }
+            report.append("To see which dependency brings a module in, run:").append(newline)
+            added.forEach {
+                report.append("  ./gradlew $projectPath:dependencyInsight --configuration runtimeClasspath --dependency $it")
+                    .append(newline)
+            }
+        }
+        if (removed.isNotEmpty()) {
+            report.append("Modules listed in the expected file, and no longer in the release:").append(newline)
+            removed.forEach { report.append("  - $it").append(newline) }
+        }
+        if (totalSize > sizeLimit) {
+            report.append(
+                "The total size of the jars is $totalSize bytes (about ${totalSize / mib} MiB), " +
+                    "which exceeds total-size-limit=$sizeLimit in ${expectedFile.relativeTo(rootDir)}. " +
+                    "The largest jars now:"
+            ).append(newline)
+            artifacts.sortedByDescending { it.file.length() }.take(5).forEach {
+                report.append("  ${it.file.length()} ${it.file.name}").append(newline)
+            }
+        }
+        if (added.isNotEmpty() || removed.isNotEmpty()) {
+            report.append("If a module is not intended, exclude it or revert the dependency update that brought it in.")
+                .append(newline)
+        }
+        if (removed.isNotEmpty()) {
+            report.append("If a removal is not intended, restore the dependency.").append(newline)
+        }
+        if (totalSize > sizeLimit) {
+            report.append("If the growth is not intended, revert the update that grew the jars.").append(newline)
+        }
+        report.append(
+            "If both are intended, run ./gradlew ${projectPath}:verifyReleaseDependencies -PupdateExpectedJars, " +
+                "commit ${expectedFile.relativeTo(rootDir)}, and name the modules, the size growth, " +
+                "and the dependency updates in the pull request description."
+        )
+        throw GradleException(report.toString())
     }
 }
```

## haiku-gen4-2 (judge 5 code VK)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.
The release contains modules that src/dist/src/dist/expected_release_artifacts.txt does not list:
  + org.example:foo
    To see what brings it in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The total size of the jars is 88080384 bytes (about 84 MiB), which exceeds total-size-limit=87031808 bytes (about 83 MiB) in src/dist/src/dist/expected_release_artifacts.txt. The largest jars are:
  12582912 bcprov-jdk18on-1.78.jar
  9437184 groovy-4.0.21.jar
  5242880 jmeter-core.jar
  4194304 xstream-1.4.20.jar
  3145728 rhino-1.7.14.jar
If a module or a size change is not intended, remove the dependency or revert the dependency update that brought it in. If it is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars. That rewrites src/dist/src/dist/expected_release_artifacts.txt and sets total-size-limit to the current total size plus 5 MiB. Then commit the file, and name the added or removed modules and the size change in the pull request description.
```

### Reader reply

```markdown
1. **Failure:** The release jars don't match `expected_release_artifacts.txt`. The check catches unnoticed (often transitive) dependencies and size growth. Here, the new module `org.example:foo` appeared, and the total is 1 MiB over the limit.

2. **Changed:** The output doesn't say which edit caused this. It shows only the new module and the size overage.

3. **Next:** `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo` to find what pulls in `foo`. The expected-file path prints as `src/dist/src/dist/...`, which looks doubled, so confirm it before rewriting anything.

4. **Action:** If unintended, remove `foo` or revert the update that brought it in. If intended, run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars`, review the diff, and commit. That sets the limit to the current size plus 5 MiB, a loosening to accept deliberately.

5. **PR description:** Name `org.example:foo`, its origin once found, and the size change. The output gives no previous total, so state only the current figures.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,35 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val problems = mutableListOf<String>()
+        if (added.isNotEmpty()) {
+            problems += "The release contains modules that $expectedPath does not list:\n" +
+                added.joinToString("\n") {
+                    "  + $it\n    To see what brings it in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency $it"
+                }
+        }
+        if (removed.isNotEmpty()) {
+            problems += "$expectedPath lists modules that the release no longer contains:\n" +
+                removed.joinToString("\n") { "  - $it" }
+        }
+        if (totalSize > sizeLimit) {
+            problems += "The total size of the jars is $totalSize bytes (about ${totalSize / mib} MiB), which exceeds " +
+                "total-size-limit=$sizeLimit bytes (about ${sizeLimit / mib} MiB) in $expectedPath. The largest jars are:\n" +
+                artifacts.sortedByDescending { it.file.length() }.take(5).joinToString("\n") {
+                    "  ${it.file.length()} ${it.file.name}"
+                }
+        }
+        throw GradleException(
+            "The jars of the binary release do not match $expectedPath. The check catches dependencies that enter " +
+                "the release unnoticed, often transitively, and unexpected growth of the release.\n" +
+                problems.joinToString("\n") +
+                "\nIf a module or a size change is not intended, remove the dependency or revert the dependency update " +
+                "that brought it in. If it is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars. " +
+                "That rewrites $expectedPath and sets total-size-limit to the current total size plus " +
+                "${releaseJarsSizeHeadroom / mib} MiB. Then commit the file, and name the added or removed modules and " +
+                "the size change in the pull request description."
+        )
     }
 }
```

## haiku-gen4-3 (judge 5 code VI)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt.
The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.
  + org.example:foo, not listed in the file
The total size of the jars is 88080384 bytes (about 84 MiB), which exceeds total-size-limit=87031808 (about 83 MiB) in src/dist/src/dist/expected_release_artifacts.txt.
The size of every jar is listed in src/dist/build/dist/release_jars.csv.
To see what brings in org.example:foo, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
If the change is not intended, exclude an added module or restore a removed one, or revert the dependency update that caused it.
If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, which also resets total-size-limit, commit the regenerated file, and name the modules and the size growth in the pull request description.
```

### Reader reply

```markdown
**1. Failure.** The release-jar check failed because the jars don't match `expected_release_artifacts.txt`. It catches dependencies that enter unnoticed, often transitively, and unexpected release growth. Found: unlisted `org.example:foo`, and total jar size 88,080,384 bytes, over the 87,031,808-byte limit by 1 MiB.

**2. Change.** The output shows only `org.example:foo` added and the size overage. It doesn't give the cause or say whether anything was removed.

**3. Next.** `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`. Per-jar sizes are in `src/dist/build/dist/release_jars.csv`, which I couldn't read.

**4. Action.**
- Intended: `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars`, which also resets the size limit. Review the regenerated file, then commit it.
- Not intended: exclude `org.example:foo` or revert the update that brought it in.

**5. PR description.** Name `org.example:foo`, the 1 MiB growth, and the dependency that introduced it (not identifiable from this output).
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,26 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val problems = buildString {
+            appendLine("The jars of the binary release do not match ${expectedFile.relativeTo(rootDir)}.")
+            appendLine("The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.")
+            for (module in added) {
+                appendLine("  + $module, not listed in the file")
+            }
+            for (module in removed) {
+                appendLine("  - $module, listed in the file but absent from the release")
+            }
+            if (totalSize > sizeLimit) {
+                appendLine("The total size of the jars is $totalSize bytes (about ${totalSize / mib} MiB), which exceeds total-size-limit=$sizeLimit (about ${sizeLimit / mib} MiB) in ${expectedFile.relativeTo(rootDir)}.")
+            }
+            appendLine("The size of every jar is listed in ${actualJars.get().asFile.relativeTo(rootDir)}.")
+            for (module in added) {
+                appendLine("To see what brings in $module, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency $module")
+            }
+            appendLine("If the change is not intended, exclude an added module or restore a removed one, or revert the dependency update that caused it.")
+            appendLine("If the change is intended, run ./gradlew $path -PupdateExpectedJars, which also resets total-size-limit, commit the regenerated file, and name the modules and the size growth in the pull request description.")
+        }
+        throw GradleException(problems.trimEnd())
     }
 }
```

## sonnet-gen4-1 (judge 5 code VA)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
    To see which dependency brings it in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The total size of the jars is 88080384 bytes (84 MiB), which exceeds total-size-limit=87031808 (83 MiB) in src/dist/src/dist/expected_release_artifacts.txt. The largest jars now:
  12582912 bcprov-jdk18on-1.78.jar
  9437184 groovy-4.0.21.jar
  5242880 jmeter-core.jar
  4194304 xstream-1.4.20.jar
  3145728 rhino-1.7.14.jar
If the module change is not intended, exclude the module or revert the dependency update that caused it. If the growth is not intended, revert the update that grew the jars. If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, which also resets total-size-limit, and commit src/dist/src/dist/expected_release_artifacts.txt. Name the added and removed modules, the size growth, and the dependency update in the pull request description, so that the reviewer sees what changed in the release.
```

### Reader reply

```markdown
1. **Failure:** `./gradlew build` failed its release-artifact check. The release jars don't match `expected_release_artifacts.txt`. `org.example:foo` (`foo-1.2.jar`, 1,048,576 bytes) was added, and total jar size (88,080,384 bytes, 84 MiB) exceeds the 83 MiB limit. The check catches dependencies that enter unnoticed, often transitively, and unexpected release growth.

2. **Changed:** `org.example:foo` was added. The output shows no removals and doesn't give the previous total size.

3. **Next:**
   `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`

4. **Action:**
   - Not intended: exclude the module or revert the dependency update.
   - Intended: run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars`, then commit `expected_release_artifacts.txt`. This also resets the size limit.

5. **PR description:** Name the added module, the growth to 84 MiB, the size-limit reset, and the dependency update responsible. The output doesn't identify that update, so confirm it with `dependencyInsight`.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,41 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedFileName = expectedFile.relativeTo(rootDir)
+        val message = buildString {
+            append("The jars of the binary release do not match $expectedFileName. ")
+            append("The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.")
+            for (module in added) {
+                val jars = jarsByModule.getValue(module)
+                append(newline).append("  + ").append(module)
+                    .append(" (").append(jars.joinToString { "${it.file.name}, ${it.file.length()} bytes" }).append(")")
+                val coordinates = module.split(':').take(2).joinToString(":")
+                append(newline).append("    To see which dependency brings it in, run ./gradlew $projectPath:dependencyInsight")
+                    .append(" --configuration runtimeClasspath --dependency $coordinates")
+            }
+            for (module in removed) {
+                append(newline).append("  - ").append(module).append(" (no longer in the release)")
+            }
+            if (totalSize > sizeLimit) {
+                append(newline).append("The total size of the jars is $totalSize bytes (${totalSize / mib} MiB), ")
+                append("which exceeds total-size-limit=$sizeLimit (${sizeLimit / mib} MiB) in $expectedFileName. The largest jars now:")
+                artifacts.sortedByDescending { it.file.length() }.take(5).forEach {
+                    append(newline).append("  ${it.file.length()} ${it.file.name}")
+                }
+            }
+            append(newline)
+            if (added.isNotEmpty() || removed.isNotEmpty()) {
+                append("If the module change is not intended, exclude the module or revert the dependency update that caused it. ")
+            }
+            if (totalSize > sizeLimit) {
+                append("If the growth is not intended, revert the update that grew the jars. ")
+            }
+            append("If the change is intended, run ./gradlew $path -PupdateExpectedJars, which also resets total-size-limit, ")
+            append("and commit $expectedFileName. ")
+            append("Name the added and removed modules, the size growth, and the dependency update in the pull request description, ")
+            append("so that the reviewer sees what changed in the release.")
+        }
+        throw GradleException(message)
     }
 }
```

## sonnet-gen4-2 (judge 5 code VB)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings in org.example:foo, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The total size of the jars is 88080384 bytes (84 MiB), which exceeds total-size-limit=87031808 (83 MiB) in src/dist/src/dist/expected_release_artifacts.txt. The largest jars now:
  12582912 bcprov-jdk18on-1.78.jar
  9437184 groovy-4.0.21.jar
  5242880 jmeter-core.jar
  4194304 xstream-1.4.20.jar
  3145728 rhino-1.7.14.jar
If the module change is not intended, exclude the added modules, or revert the dependency update that changed them. If the growth is not intended, revert the update that grew the jars. If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, which also resets total-size-limit, commit src/dist/src/dist/expected_release_artifacts.txt, and name the changed modules, the size growth, and the dependency update in the pull request description.
```

### Reader reply

```markdown
**1. Failure.** The release-artifact check found that the distribution jars no longer match `expected_release_artifacts.txt`. It catches unnoticed dependencies and size growth. `org.example:foo` (1 MiB) was added, pushing the total to 84 MiB against an 83 MiB limit.

**2. Change.** Added `org.example:foo` (`foo-1.2.jar`). The output doesn't say whether it's transitive or which update caused it.

**3. Next.** `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo` shows what pulls it in. I can't run it here.

**4. Action.** If intended, run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit the expected file. This also resets the size limit, so review that change. If not, exclude foo or revert the dependency update.

**5. PR description.** Name the changed modules (the output doesn't list them), the 1 MiB growth, the dependency update, and the reset size limit.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,51 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val message = StringBuilder()
+        message.append("The jars of the binary release do not match $expectedPath. ")
+            .append("The check catches dependencies that enter the release unnoticed, often transitively, ")
+            .append("and unexpected growth of the release.")
+        for (module in added) {
+            val jars = jarsByModule.getValue(module)
+            message.append(newline).append("  + $module (")
+                .append(jars.joinToString { "${it.file.name}, ${it.file.length()} bytes" })
+                .append(")")
+        }
+        for (module in removed) {
+            message.append(newline).append("  - $module")
+        }
+        for (module in added) {
+            // dependencyInsight takes group:module, without the classifier and the extension
+            val dependency = module.substringBefore('@').split(':').take(2).joinToString(":")
+            message.append(newline)
+                .append("To see which dependency brings in $module, run ")
+                .append("./gradlew $projectPath:dependencyInsight --configuration runtimeClasspath --dependency $dependency")
+        }
+        if (removed.isNotEmpty()) {
+            message.append(newline)
+                .append("A removed module is listed in $expectedPath and is no longer on runtimeClasspath.")
+        }
+        if (totalSize > sizeLimit) {
+            message.append(newline)
+                .append("The total size of the jars is $totalSize bytes (${totalSize / mib} MiB), ")
+                .append("which exceeds total-size-limit=$sizeLimit (${sizeLimit / mib} MiB) in $expectedPath. ")
+                .append("The largest jars now:")
+            for (artifact in artifacts.sortedByDescending { it.file.length() }.take(5)) {
+                message.append(newline).append("  ${artifact.file.length()} ${artifact.file.name}")
+            }
+        }
+        message.append(newline)
+        if (added.isNotEmpty() || removed.isNotEmpty()) {
+            message.append("If the module change is not intended, exclude the added modules, or revert the dependency update that changed them. ")
+        }
+        if (totalSize > sizeLimit) {
+            message.append("If the growth is not intended, revert the update that grew the jars. ")
+        }
+        message.append("If the change is intended, run ./gradlew $path -PupdateExpectedJars, ")
+            .append("which also resets total-size-limit, commit $expectedPath, ")
+            .append("and name the changed modules, the size growth, and the dependency update in the pull request description.")
+        throw GradleException(message.toString())
     }
 }
```

## sonnet-gen4-3 (judge 5 code VE)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings in an added module, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The total size of the jars is 88080384 bytes (84 MiB), which exceeds total-size-limit=87031808 (83 MiB) in src/dist/src/dist/expected_release_artifacts.txt. The largest jars now:
  12582912 bcprov-jdk18on-1.78.jar
  9437184 groovy-4.0.21.jar
  5242880 jmeter-core.jar
  4194304 xstream-1.4.20.jar
  3145728 rhino-1.7.14.jar
If an added module is not intended, exclude it or revert the dependency update that brought it in. If a removed module is not intended, restore the dependency that provided it. If the growth is not intended, revert the update that grew the jars. If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, which also resets total-size-limit, commit src/dist/src/dist/expected_release_artifacts.txt, and name the added and removed modules, the size growth, and the dependency update in the pull request description.
```

### Reader reply

```markdown
**1. Failure:** The release-artifact check found that the binary release's jars don't match `src/dist/src/dist/expected_release_artifacts.txt`. It catches dependencies that enter the release unnoticed, often transitively, and unexpected growth.

**2. Change:** One module was added: `org.example:foo` (`foo-1.2.jar`, 1,048,576 bytes). The total is 88,080,384 bytes, which exceeds the 87,031,808-byte limit by exactly that jar's size. The output doesn't show the previous total, whether `foo` is direct or transitive, or which update brought it in.

**3. Next:** `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`

**4. Intended:** Run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars`, which also resets total-size-limit. Then commit `src/dist/src/dist/expected_release_artifacts.txt`.
**Not intended:** Exclude `foo` or revert the update that brought it in, then rerun the build.

**5. PR description:** Name `org.example:foo`, the 1 MiB size growth (total now 84 MiB), the dependency update responsible, and the reset size limit. The output lists no removed modules.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,42 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val message = StringBuilder()
+        message.append("The jars of the binary release do not match $expectedPath. ")
+            .append("The check catches dependencies that enter the release unnoticed, often transitively, ")
+            .append("and unexpected growth of the release.")
+            .append(newline)
+        for (module in added) {
+            val jars = jarsByModule.getValue(module)
+            message.append("  + $module (${jars.joinToString { "${it.file.name}, ${it.file.length()} bytes" }})")
+                .append(newline)
+        }
+        for (module in removed) {
+            message.append("  - $module").append(newline)
+        }
+        if (added.isNotEmpty()) {
+            val example = added.first().substringBefore('@').split(':').take(2).joinToString(":")
+            message.append("To see which dependency brings in an added module, run ")
+                .append("./gradlew ${projectPath}:dependencyInsight --configuration runtimeClasspath --dependency $example")
+                .append(newline)
+        }
+        if (totalSize > sizeLimit) {
+            message.append("The total size of the jars is $totalSize bytes (${totalSize / mib} MiB), ")
+                .append("which exceeds total-size-limit=$sizeLimit (${sizeLimit / mib} MiB) in $expectedPath. ")
+                .append("The largest jars now:")
+                .append(newline)
+            artifacts.sortedByDescending { it.file.length() }.take(5).forEach {
+                message.append("  ${it.file.length()} ${it.file.name}").append(newline)
+            }
+        }
+        message.append("If an added module is not intended, exclude it or revert the dependency update that brought it in. ")
+            .append("If a removed module is not intended, restore the dependency that provided it. ")
+            .append("If the growth is not intended, revert the update that grew the jars. ")
+            .append("If the change is intended, run ./gradlew $path -PupdateExpectedJars, which also resets total-size-limit, ")
+            .append("commit $expectedPath, and name the added and removed modules, the size growth, ")
+            .append("and the dependency update in the pull request description.")
+        throw GradleException(message.toString())
     }
 }
```
