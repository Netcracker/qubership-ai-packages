# Rendered messages, reader replies, and diffs of the verifyReleaseDependencies trial

Unblinded: each section names the blind code the judge saw. `r1` is round 1, `r2` round 2.

## r1/haiku-new-1 (code T)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter the release unnoticed, often transitively, and growth past total-size-limit.

Modules in the release that src/dist/src/dist/expected_release_artifacts.txt does not list:
  + org.example:foo (foo-1.2.jar)
To see which dependency brings a module in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency <module>. If a module is not intended, exclude it or revert the dependency update that brought it in.

The total size of all jars in the release, JMeter jars included, is 88080384 bytes, which exceeds total-size-limit=87031808 in src/dist/src/dist/expected_release_artifacts.txt by 1048576 bytes.
The largest jars are:
  12582912 bcprov-jdk18on-1.78.jar
  9437184 groovy-4.0.21.jar
  5242880 jmeter-core.jar
  4194304 xstream-1.4.20.jar
  3145728 rhino-1.7.14.jar
If the growth is not intended, revert the dependency update that grew the jars.

If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, then commit src/dist/src/dist/expected_release_artifacts.txt. In the pull request description, name the added or removed modules and the size growth, with the dependency update that caused them.
```

### Reader reply

```markdown
**1. Failure:** The release-artifact check failed because the release jars don't match `expected_release_artifacts.txt`. The check catches unnoticed dependencies (often transitive) and size growth.

**2. Changes:** A new module, `org.example:foo` (`foo-1.2.jar`), is in the release. Total jar size is 88,080,384 bytes, 1,048,576 bytes over the 87,031,808 limit. The output doesn't say which jars grew or whether your update brought in `foo`.

**3. Next:** `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`. The output shows `<module>`, so I filled in the module ID. I haven't verified it.

**4. If intended:** Run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars`, then commit the updated expected file. The output doesn't say whether this also updates the size limit. **If not intended:** Exclude `foo` or revert the dependency update.

**5. PR description:** Name `foo` as added, the 1 MiB size growth, and the dependency update responsible. The output's path is doubled (`src/dist/src/dist/...`). Confirm it's correct before committing.
```

### Diff

```diff
diff --git a/src/dist/build.gradle.kts b/src/dist/build.gradle.kts
index 8349f05..936a0dd 100644
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -267,11 +267,48 @@ val verifyReleaseDependencies by tasks.registering {
 
         val added = jarsByModule.keys - expectedModules
         val removed = expectedModules.sortedWith(caseInsensitive) - jarsByModule.keys
-        if (added.isEmpty() && removed.isEmpty() && totalSize <= sizeLimit) {
+        val sizeExceeded = totalSize > sizeLimit
+        if (added.isEmpty() && removed.isEmpty() && !sizeExceeded) {
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val problems = mutableListOf<String>()
+        if (added.isNotEmpty()) {
+            problems += buildString {
+                appendLine("Modules in the release that $expectedPath does not list:")
+                added.forEach { module ->
+                    appendLine("  + $module (${jarsByModule.getValue(module).joinToString { it.file.name }})")
+                }
+                append("To see which dependency brings a module in, run ./gradlew $projectPath:dependencyInsight --configuration runtimeClasspath --dependency <module>. ")
+                append("If a module is not intended, exclude it or revert the dependency update that brought it in.")
+            }
+        }
+        if (removed.isNotEmpty()) {
+            problems += buildString {
+                appendLine("Modules that $expectedPath lists but the release does not contain:")
+                removed.forEach { appendLine("  - $it") }
+                append("If a module was removed on purpose, accept the change below. Otherwise, restore the dependency that provided it.")
+            }
+        }
+        if (sizeExceeded) {
+            val largest = artifacts.sortedByDescending { it.file.length() }.take(5)
+            problems += buildString {
+                appendLine("The total size of all jars in the release, JMeter jars included, is $totalSize bytes, which exceeds total-size-limit=$sizeLimit in $expectedPath by ${totalSize - sizeLimit} bytes.")
+                appendLine("The largest jars are:")
+                largest.forEach { appendLine("  ${it.file.length()} ${it.file.name}") }
+                append("If the growth is not intended, revert the dependency update that grew the jars.")
+            }
+        }
+
+        throw GradleException(
+            "The jars of the binary release do not match $expectedPath. " +
+                "The check catches dependencies that enter the release unnoticed, often transitively, and growth past total-size-limit.\n\n" +
+                problems.joinToString("\n\n") + "\n\n" +
+                "If the change is intended, run ./gradlew $projectPath:verifyReleaseDependencies -PupdateExpectedJars, " +
+                "then commit $expectedPath. In the pull request description, name the added or removed modules and the size growth, " +
+                "with the dependency update that caused them."
+        )
     }
 }
```

## r1/haiku-new-2 (code X)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter the release unnoticed, often transitively, and growth of the release beyond its size limit.

Modules that are in the release but not in src/dist/src/dist/expected_release_artifacts.txt:
  + org.example:foo (foo-1.2.jar)
    To see which dependency brings it in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
If a module is not intended, exclude it or revert the dependency update that brought it in.

The total size of all jars in the release is 88080384 bytes (84 MiB), which exceeds total-size-limit=87031808 in src/dist/src/dist/expected_release_artifacts.txt by 1048576 bytes. The largest jars:
  12582912 bcprov-jdk18on-1.78.jar
  9437184 groovy-4.0.21.jar
  5242880 jmeter-core.jar
  4194304 xstream-1.4.20.jar
  3145728 rhino-1.7.14.jar
If the growth is not intended, revert the dependency update that grew the jars.

If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars and commit src/dist/src/dist/expected_release_artifacts.txt. Name the added or removed modules and the size growth in the pull request description, together with the dependency update that caused them.
```

### Reader reply

```markdown
1. **Failed:** The release jars don't match `src/dist/src/dist/expected_release_artifacts.txt`. The unlisted module `org.example:foo` (foo-1.2.jar) is in the release, and the jars total 88080384 bytes, 1048576 bytes over the 87031808-byte limit. The check catches unnoticed (often transitive) dependencies and size growth.

2. **What changed:** The output doesn't say which update added `foo` or grew the jars.

3. **Next:** `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`. I haven't run it.

4. **If intended:** Run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit the expected-artifacts file. **If not:** Exclude `foo` or revert the dependency update that caused it.

5. **PR description:** Name the added module `org.example:foo`, the 1048576-byte size growth, and the responsible dependency update. The output doesn't identify that update, so get it from the dependencyInsight result first.
```

### Diff

```diff
diff --git a/src/dist/build.gradle.kts b/src/dist/build.gradle.kts
index 8349f05..473259f 100644
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,48 @@ val verifyReleaseDependencies by tasks.registering {
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val sections = mutableListOf(
+            "The jars of the binary release do not match $expectedPath. The check catches dependencies that enter " +
+                "the release unnoticed, often transitively, and growth of the release beyond its size limit."
+        )
+        if (added.isNotEmpty()) {
+            sections += buildString {
+                appendLine("Modules that are in the release but not in $expectedPath:")
+                for (module in added.sortedWith(caseInsensitive)) {
+                    val files = jarsByModule.getValue(module).joinToString { it.file.name }
+                    appendLine("  + $module ($files)")
+                    appendLine("    To see which dependency brings it in, run ./gradlew $projectPath:dependencyInsight " +
+                        "--configuration runtimeClasspath --dependency $module")
+                }
+                append("If a module is not intended, exclude it or revert the dependency update that brought it in.")
+            }
+        }
+        if (removed.isNotEmpty()) {
+            sections += buildString {
+                appendLine("Modules that are in $expectedPath but not in the release:")
+                for (module in removed) {
+                    appendLine("  - $module")
+                }
+                append("If the removal is not intended, restore the dependency. Otherwise accept the change as described below.")
+            }
+        }
+        if (totalSize > sizeLimit) {
+            sections += buildString {
+                appendLine(
+                    "The total size of all jars in the release is $totalSize bytes (${totalSize / mib} MiB), which exceeds " +
+                        "total-size-limit=$sizeLimit in $expectedPath by ${totalSize - sizeLimit} bytes. The largest jars:"
+                )
+                for (artifact in artifacts.sortedByDescending { it.file.length() }.take(5)) {
+                    appendLine("  ${artifact.file.length()} ${artifact.file.name}")
+                }
+                append("If the growth is not intended, revert the dependency update that grew the jars.")
+            }
+        }
+        sections += "If the change is intended, run ./gradlew $projectPath:verifyReleaseDependencies -PupdateExpectedJars " +
+            "and commit $expectedPath. Name the added or removed modules and the size growth in the pull request " +
+            "description, together with the dependency update that caused them."
+        throw GradleException(sections.joinToString("\n\n"))
     }
 }
```

## r1/haiku-new-3 (code F)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check keeps a dependency change from entering or growing the release without a reviewer seeing it.

Modules in the release that are not in src/dist/src/dist/expected_release_artifacts.txt:
  + org.example:foo (foo-1.2.jar)
  To see which dependency brings it in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
  If a module is not intended, exclude it or revert the dependency update that brought it in.

The jars in the release total 88080384 bytes, which exceeds total-size-limit=87031808 in src/dist/src/dist/expected_release_artifacts.txt by 1048576 bytes.
The jars and their sizes are listed in src/dist/build/dist/release_jars.csv.
If the growth is not intended, revert the dependency update that grew the jars.

If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, commit src/dist/src/dist/expected_release_artifacts.txt, and name the added, removed, and grown modules in the pull request description, with the dependency update that caused them.
```

### Reader reply

```markdown
1. **Failure:** The release-artifact check in `src/dist` failed. Module `org.example:foo` (foo-1.2.jar) is in the release but not in the expected list, and the jars total 88080384 bytes, 1048576 over the 87031808 limit. The check keeps dependency changes from adding or growing the release without review.

2. **Changed:** The output doesn't say what the update changed. It shows foo added and total growth, but not which jars grew. Per-jar sizes are in `src/dist/build/dist/release_jars.csv`, which I can't read.

3. **Next:** `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`

4. **Action:** If intended, run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit `src/dist/src/dist/expected_release_artifacts.txt`. If not, exclude foo or revert the update that brought it in.

5. **PR description:** Name foo as added, each grown module with its size change, and the dependency update behind them. The output lists no removed modules, so don't claim any.
```

### Diff

```diff
diff --git a/src/dist/build.gradle.kts b/src/dist/build.gradle.kts
index 8349f05..cc7c0ad 100644
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,38 @@ val verifyReleaseDependencies by tasks.registering {
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val actualPath = actualJars.get().asFile.relativeTo(rootDir)
+        val message = mutableListOf(
+            "The jars of the binary release do not match $expectedPath. The check keeps a dependency change from entering or growing the release without a reviewer seeing it."
+        )
+        if (added.isNotEmpty()) {
+            message += ""
+            message += "Modules in the release that are not in $expectedPath:"
+            for (module in added) {
+                val jarNames = jarsByModule.getValue(module).joinToString { it.file.name }
+                message += "  + $module ($jarNames)"
+                message += "  To see which dependency brings it in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency $module"
+            }
+            message += "  If a module is not intended, exclude it or revert the dependency update that brought it in."
+        }
+        if (removed.isNotEmpty()) {
+            message += ""
+            message += "Modules listed in $expectedPath that are no longer in the release:"
+            for (module in removed) {
+                message += "  - $module"
+            }
+            message += "  If a removal is not intended, restore the dependency that provided the module."
+        }
+        if (totalSize > sizeLimit) {
+            message += ""
+            message += "The jars in the release total $totalSize bytes, which exceeds total-size-limit=$sizeLimit in $expectedPath by ${totalSize - sizeLimit} bytes."
+            message += "The jars and their sizes are listed in $actualPath."
+            message += "If the growth is not intended, revert the dependency update that grew the jars."
+        }
+        message += ""
+        message += "If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, commit $expectedPath, and name the added, removed, and grown modules in the pull request description, with the dependency update that caused them."
+        throw GradleException(message.joinToString(newline))
     }
 }
```

## r1/haiku-old-1 (code D)

### Rendered message

```text
Release dependencies do not match src/dist/src/dist/expected_release_artifacts.txt: modules added to the release: org.example:foo; the jars total 88080384 bytes, which exceeds total-size-limit=87031808 bytes. If the change is intended, regenerate the file with ./gradlew :src:dist -PupdateExpectedJars and commit the diff. Otherwise the binary release changes without review.
```

### Reader reply

```markdown
**1. Failure:** The release-artifact check in `:src:dist` failed. It compares release dependencies to `expected_release_artifacts.txt` and enforces a jar size limit, so changes to the binary release get reviewed.

**2. Change:** The update added `org.example:foo` (verify this coordinate). Jars total 88,080,384 bytes, 1 MiB over the 87,031,808 limit. The output doesn't show the version change or the diff.

**3. Next:** Only if intended: `./gradlew :src:dist -PupdateExpectedJars`. The output doesn't say whether it also changes `total-size-limit`, so check after running. I have not run anything.

**4. If intended:** Run that command, review the expected-file diff, and commit it. If the size check still fails, the limit needs its own decision. If not intended: revert the dependency update and don't regenerate.

**5. PR description:** Name the new module, the 1 MiB size increase, why the dependency is needed, and any size-limit change with its justification.
```

### Diff

```diff
diff --git a/src/dist/build.gradle.kts b/src/dist/build.gradle.kts
index 8349f05..fd68eeb 100644
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,21 @@ val verifyReleaseDependencies by tasks.registering {
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val problems = mutableListOf<String>()
+        if (added.isNotEmpty()) {
+            problems += "modules added to the release: ${added.joinToString()}"
+        }
+        if (removed.isNotEmpty()) {
+            problems += "modules missing from the release: ${removed.joinToString()}"
+        }
+        if (totalSize > sizeLimit) {
+            problems += "the jars total $totalSize bytes, which exceeds total-size-limit=$sizeLimit bytes"
+        }
+        throw GradleException(
+            "Release dependencies do not match ${expectedFile.relativeTo(rootDir)}: ${problems.joinToString("; ")}. " +
+                "If the change is intended, regenerate the file with ./gradlew $projectPath -PupdateExpectedJars " +
+                "and commit the diff. Otherwise the binary release changes without review."
+        )
     }
 }
```

## r1/haiku-old-2 (code O)

### Rendered message

```text
The binary release does not match src/dist/src/dist/expected_release_artifacts.txt: modules added to the release: org.example:foo; the jars total 88080384 bytes, which exceeds total-size-limit=87031808. If the change is intended, regenerate the file with ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars
```

### Reader reply

```markdown
1. **Failed:** `verifyReleaseDependencies`. The release contents differ from the committed `expected_release_artifacts.txt`, and the jars total 88,080,384 bytes, 1,048,576 bytes (1 MiB) over `total-size-limit=87031808`. The check guards against unreviewed dependencies and size growth.

2. **Changed:** A new module, `org.example:foo`, is in the release. The output doesn't say whether it's direct or transitive, or which change introduced it.

3. **Next:** I can't run anything now. If the change is intended: `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars`

4. **If intended:** Run that command and review the regenerated file. The output doesn't say whether it also changes the size limit, so check that separately. **If not intended:** Find what pulls in `org.example:foo` and remove or exclude it.

5. **PR description:** Note the new `org.example:foo` artifact, the 1 MiB size increase, and whether the expected-artifacts file was regenerated. Also note that the build currently fails.
```

### Diff

```diff
diff --git a/src/dist/build.gradle.kts b/src/dist/build.gradle.kts
index 8349f05..68edcac 100644
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,20 @@ val verifyReleaseDependencies by tasks.registering {
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val problems = mutableListOf<String>()
+        if (added.isNotEmpty()) {
+            problems.add("modules added to the release: ${added.sortedWith(caseInsensitive).joinToString()}")
+        }
+        if (removed.isNotEmpty()) {
+            problems.add("modules removed from the release: ${removed.joinToString()}")
+        }
+        if (totalSize > sizeLimit) {
+            problems.add("the jars total $totalSize bytes, which exceeds total-size-limit=$sizeLimit")
+        }
+        throw GradleException(
+            "The binary release does not match ${expectedFile.relativeTo(rootDir)}: ${problems.joinToString("; ")}. " +
+                "If the change is intended, regenerate the file with ./gradlew $path -PupdateExpectedJars"
+        )
     }
 }
```

## r1/haiku-old-3 (code J)

### Rendered message

```text
Release dependencies do not match src/dist/src/dist/expected_release_artifacts.txt: modules added: org.example:foo; the jars total 88080384 bytes, above total-size-limit=87031808. If the change is intended, regenerate the file with ./gradlew :src:dist -PupdateExpectedJars
```

### Reader reply

```markdown
**1. Failure:** The release-artifact check in `src/dist` compares the bundled jars with `expected_release_artifacts.txt` and enforces a total size limit. It catches unreviewed dependency additions and release bloat. Two checks failed: new module `org.example:foo`, and jars totaling 88,080,384 bytes, 1 MiB over the 87,031,808-byte limit. The output's path is doubled, so the file is probably `src/dist/expected_release_artifacts.txt`.

**2. Change:** `org.example:foo` is now bundled. The output doesn't say whether it's direct or transitive, or where it's declared.

**3. Next commands:** I haven't run anything. If the change is intended: `./gradlew :src:dist -PupdateExpectedJars`, then `./gradlew build`. The output doesn't say whether the flag also changes the size limit, so the build may still fail on size.

**4. Actions:** If intended, confirm the artifact is wanted, regenerate, review the diff, and resolve the size limit. If not, find what pulls in `org.example:foo`, revert that update, and don't regenerate.

**5. PR description:** Note the new module, the 1 MiB size increase, why the dependency is needed, and the changed expected-artifacts file.
```

### Diff

```diff
diff --git a/src/dist/build.gradle.kts b/src/dist/build.gradle.kts
index 8349f05..96b7f1e 100644
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,21 @@ val verifyReleaseDependencies by tasks.registering {
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
+                add("the jars total $totalSize bytes, above total-size-limit=$sizeLimit")
+            }
+        }
+        throw GradleException(
+            "Release dependencies do not match ${expectedFile.relativeTo(rootDir)}: ${problems.joinToString("; ")}. " +
+                "If the change is intended, regenerate the file with ./gradlew $projectPath -PupdateExpectedJars"
+        )
     }
 }
```

## r1/sonnet-new-1 (code G)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter or leave the release unnoticed, often transitively, and unexpected growth of the release.

Modules that are in the release but not in src/dist/src/dist/expected_release_artifacts.txt:
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings a module in, run:
  ./gradlew --quiet :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
If a module is not intended, exclude it or revert the dependency update that brought it in.

The total size of all jars in the release, JMeter jars included, is 88080384 bytes (84.0 MiB). This exceeds total-size-limit=87031808 bytes (83.0 MiB) in src/dist/src/dist/expected_release_artifacts.txt by 1048576 bytes.
The largest jars now:
  12582912 bcprov-jdk18on-1.78.jar
     9437184 groovy-4.0.21.jar
     5242880 jmeter-core.jar
     4194304 xstream-1.4.20.jar
     3145728 rhino-1.7.14.jar
All jars are listed in src/dist/build/dist/release_jars.csv. If the growth is not intended, revert the dependency update that grew the jars.

If the change is intended, run ./gradlew --quiet :src:dist:verifyReleaseDependencies -PupdateExpectedJars and commit src/dist/src/dist/expected_release_artifacts.txt. The command sets total-size-limit= to the current total size plus 5 MiB, rounded up to a whole MiB. Name the added or removed modules and the size growth in the pull request description, with the dependency update that caused them.
```

### Reader reply

```markdown
**1. Failure:** The release-jar check in `src/dist` failed. `org.example:foo` (1 MiB) is in the release but not in the expected list, and total jar size is 84.0 MiB, 1 MiB over the 83.0 MiB limit. The check catches unnoticed dependencies, often transitive ones, and unexpected growth.

**2. Change:** `org.example:foo-1.2.jar` is now in the release. Nothing was reported removed. The output doesn't name the dependency update responsible or give the previous total.

**3. Next:**
```
./gradlew --quiet :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
```
I can't run it here.

**4. Intended:** Run `./gradlew --quiet :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit `expected_release_artifacts.txt`. The new limit will be 89 MiB (84 + 5). **Not intended:** Exclude `org.example:foo` or revert the update that added it. The output doesn't say how to write the exclusion.

**5. PR description:** Name `org.example:foo` as added (1 MiB), the size growth, and the dependency update that caused it.
```

### Diff

```diff
diff --git a/src/dist/build.gradle.kts b/src/dist/build.gradle.kts
index 8349f05..a7e5e5b 100644
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,56 @@ val verifyReleaseDependencies by tasks.registering {
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        fun mibs(bytes: Long) = "%.1f MiB".format(java.util.Locale.ROOT, bytes.toDouble() / mib)
+
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val acceptCommand = "./gradlew --quiet $path -PupdateExpectedJars"
+        val sections = mutableListOf(
+            "The jars of the binary release do not match $expectedPath. " +
+                "The check catches dependencies that enter or leave the release unnoticed, often transitively, " +
+                "and unexpected growth of the release."
+        )
+        if (added.isNotEmpty()) {
+            val insightCommands = added.filter { ':' in it }.joinToString(System.lineSeparator()) {
+                val coordinates = it.substringBefore('@').split(':').take(2).joinToString(":")
+                "  ./gradlew --quiet ${projectPath.removeSuffix(":")}:dependencyInsight --configuration runtimeClasspath --dependency $coordinates"
+            }
+            sections += buildString {
+                appendLine("Modules that are in the release but not in $expectedPath:")
+                added.forEach { appendLine("  + $it (${jarsByModule.getValue(it).single().file.name}, ${jarsByModule.getValue(it).single().file.length()} bytes)") }
+                if (insightCommands.isNotEmpty()) {
+                    appendLine("To see which dependency brings a module in, run:")
+                    appendLine(insightCommands)
+                }
+                append("If a module is not intended, exclude it or revert the dependency update that brought it in.")
+            }
+        }
+        if (removed.isNotEmpty()) {
+            sections += buildString {
+                appendLine("Modules that are listed in $expectedPath but are not in the release:")
+                removed.forEach { appendLine("  - $it") }
+                appendLine("To see what the release contains now, run: ./gradlew --quiet $projectPath:dependencies --configuration runtimeClasspath")
+                append("If a module is not intended to leave, restore the dependency or the transitive path that brought it in.")
+            }
+        }
+        if (totalSize > sizeLimit) {
+            sections += buildString {
+                appendLine(
+                    "The total size of all jars in the release, JMeter jars included, is $totalSize bytes (${mibs(totalSize)}). " +
+                        "This exceeds ${sizeLimitPrefix}$sizeLimit bytes (${mibs(sizeLimit)}) in $expectedPath by ${totalSize - sizeLimit} bytes."
+                )
+                appendLine("The largest jars now:")
+                artifacts.sortedByDescending { it.file.length() }.take(5).forEach {
+                    appendLine("  ${it.file.length().toString().padStart(10)} ${it.file.name}")
+                }
+                append("All jars are listed in ${actualJars.get().asFile.relativeTo(rootDir)}. If the growth is not intended, revert the dependency update that grew the jars.")
+            }
+        }
+        sections += "If the change is intended, run $acceptCommand and commit $expectedPath. " +
+            "The command sets $sizeLimitPrefix to the current total size plus ${releaseJarsSizeHeadroom / mib} MiB, rounded up to a whole MiB. " +
+            "Name the added or removed modules and the size growth in the pull request description, with the dependency update that caused them."
+
+        throw GradleException(sections.joinToString(System.lineSeparator() + System.lineSeparator()))
     }
 }
```

## r1/sonnet-new-2 (code U)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. :src:dist:verifyReleaseDependencies catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.

Modules that are in the release but not in src/dist/src/dist/expected_release_artifacts.txt:
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings a module in, run for example:
  ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
If a module is not intended, exclude it or revert the dependency update that brought it in.

The total size of all jars in the release, JMeter jars included, is 84.0 MiB (88080384 bytes), which exceeds total-size-limit=83.0 MiB (87031808 bytes) in src/dist/src/dist/expected_release_artifacts.txt by 1048576 bytes.
The largest jars now:
    12582912 bcprov-jdk18on-1.78.jar
     9437184 groovy-4.0.21.jar
     5242880 jmeter-core.jar
     4194304 xstream-1.4.20.jar
     3145728 rhino-1.7.14.jar
The sizes of all jars are in src/dist/build/dist/release_jars.csv.
If the growth is not intended, revert the dependency update that grew the jars.

If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars and commit src/dist/src/dist/expected_release_artifacts.txt. Name the added or removed modules and the size growth in the pull request description, with the dependency update that caused them.
```

### Reader reply

```markdown
**1. Failure:** `:src:dist:verifyReleaseDependencies` found that the release jars don't match `expected_release_artifacts.txt`. The check catches unnoticed dependencies, often transitive ones, and unexpected size growth.

**2. Change:** The release gained `org.example:foo` (foo-1.2.jar, 1048576 bytes), which is not in the expected list. The total is 84.0 MiB, over the 83.0 MiB limit by 1048576 bytes, which is likely foo's size. The output doesn't identify the update that added foo.

**3. Next:** `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`

**4. If intended:** Run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit `src/dist/src/dist/expected_release_artifacts.txt`. The output doesn't say whether this also changes the size limit. **If not:** Exclude foo, or revert the update that brought it in.

**5. PR description:** Name `org.example:foo` and the update that caused it, the 1 MiB growth, and the 84.0 MiB total against the 83.0 MiB limit.
```

### Diff

```diff
diff --git a/src/dist/build.gradle.kts b/src/dist/build.gradle.kts
index 8349f05..1456563 100644
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -23,6 +23,7 @@ import com.github.vlsi.gradle.git.FindGitAttributes
 import com.github.vlsi.gradle.git.dsl.gitignore
 import com.github.vlsi.gradle.properties.dsl.props
 import org.gradle.api.internal.TaskOutputsInternal
+import java.util.Locale
 
 plugins {
     id("build-logic.build-params")
@@ -271,7 +272,59 @@ val verifyReleaseDependencies by tasks.registering {
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        fun size(bytes: Long) = "%.1f MiB (%d bytes)".format(Locale.ROOT, bytes.toDouble() / mib, bytes)
+        fun dependencyInsight(module: String) =
+            "./gradlew $projectPath:dependencyInsight --configuration runtimeClasspath --dependency " +
+                module.substringBefore('@').split(':').take(2).joinToString(":")
+
+        val message = buildString {
+            appendLine(
+                "The jars of the binary release do not match $expectedPath. " +
+                    "$path catches dependencies that enter the release unnoticed, often transitively, " +
+                    "and unexpected growth of the release."
+            )
+            if (added.isNotEmpty()) {
+                appendLine()
+                appendLine("Modules that are in the release but not in $expectedPath:")
+                for (module in added) {
+                    val jars = jarsByModule.getValue(module)
+                    appendLine("  + $module (${jars.joinToString { "${it.file.name}, ${it.file.length()} bytes" }})")
+                }
+                appendLine("To see which dependency brings a module in, run for example:")
+                appendLine("  ${dependencyInsight(added.first())}")
+                appendLine("If a module is not intended, exclude it or revert the dependency update that brought it in.")
+            }
+            if (removed.isNotEmpty()) {
+                appendLine()
+                appendLine("Modules that are listed in $expectedPath but not in the release:")
+                for (module in removed) {
+                    appendLine("  - $module")
+                }
+                appendLine("To see what the release contains now, run ./gradlew $projectPath:dependencies --configuration runtimeClasspath")
+                appendLine("If a module is not meant to leave the release, restore the dependency that brought it in.")
+            }
+            if (totalSize > sizeLimit) {
+                appendLine()
+                appendLine(
+                    "The total size of all jars in the release, JMeter jars included, is ${size(totalSize)}, " +
+                        "which exceeds total-size-limit=${size(sizeLimit)} in $expectedPath by ${totalSize - sizeLimit} bytes."
+                )
+                appendLine("The largest jars now:")
+                for (artifact in artifacts.sortedByDescending { it.file.length() }.take(5)) {
+                    appendLine("  ${artifact.file.length().toString().padStart(10)} ${artifact.file.name}")
+                }
+                appendLine("The sizes of all jars are in ${actualJars.get().asFile.relativeTo(rootDir)}.")
+                appendLine("If the growth is not intended, revert the dependency update that grew the jars.")
+            }
+            appendLine()
+            appendLine(
+                "If the change is intended, run ./gradlew $path -PupdateExpectedJars and commit $expectedPath. " +
+                    "Name the added or removed modules and the size growth in the pull request description, " +
+                    "with the dependency update that caused them."
+            )
+        }
+        throw GradleException(message.trimEnd())
     }
 }
```

## r1/sonnet-new-3 (code S)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.

Modules that are in the release but not in src/dist/src/dist/expected_release_artifacts.txt:
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings a module in, run ./gradlew --quiet :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
If a module is not intended, exclude it or revert the dependency update that brought it in.

The total size of all jars in the release, JMeter jars included, is 88080384 bytes (84 MiB), which exceeds total-size-limit=87031808 (83 MiB) in src/dist/src/dist/expected_release_artifacts.txt by 1048576 bytes.
The largest jars now:
  12582912 bcprov-jdk18on-1.78.jar
  9437184 groovy-4.0.21.jar
  5242880 jmeter-core.jar
  4194304 xstream-1.4.20.jar
  3145728 rhino-1.7.14.jar
If the growth is not intended, revert the dependency update that grew the jars.

If the change is intended, run ./gradlew --quiet :src:dist:verifyReleaseDependencies -PupdateExpectedJars and commit src/dist/src/dist/expected_release_artifacts.txt. Name the added or removed modules and the size growth in the pull request description, with the dependency update that caused them.
```

### Reader reply

```markdown
**1. What failed:** The release contents don't match `src/dist/src/dist/expected_release_artifacts.txt`. The check catches dependencies that enter the release unnoticed (often transitively) and unexpected growth. Two things failed: module `org.example:foo` (foo-1.2.jar, 1048576 bytes) is in the release but not in the expected list, and the total is 1048576 bytes over the size limit.

**2. What changed:** The output doesn't say. It doesn't name the dependency update, and it doesn't show the previous total, so I can't confirm that `foo` alone caused the overage.

**3. Next command:**
`./gradlew --quiet :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`

**4. Next steps:** If intended, run `./gradlew --quiet :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit the updated expected-artifacts file. If not, exclude `foo` or revert the dependency update that brought it in. The environment reports this directory isn't a git repository, so do the commit in the actual JMeter checkout.

**5. PR description:** Name the added module and its size, state the size growth, and name the dependency update that caused them. The output doesn't say whether `foo` is direct or transitive.
```

### Diff

```diff
diff --git a/src/dist/build.gradle.kts b/src/dist/build.gradle.kts
index 8349f05..6bbb333 100644
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,50 @@ val verifyReleaseDependencies by tasks.registering {
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val message = StringBuilder()
+        message.append("The jars of the binary release do not match $expectedPath. ")
+            .append("The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.")
+            .append(newline)
+
+        if (added.isNotEmpty()) {
+            message.append(newline).append("Modules that are in the release but not in $expectedPath:").append(newline)
+            for (module in added) {
+                val jars = jarsByModule.getValue(module)
+                message.append("  + $module (${jars.joinToString { "${it.file.name}, ${it.file.length()} bytes" }})").append(newline)
+            }
+            val firstAdded = added.first().split(':').take(2).joinToString(":")
+            message.append("To see which dependency brings a module in, run ./gradlew --quiet $projectPath:dependencyInsight --configuration runtimeClasspath --dependency $firstAdded")
+                .append(newline)
+            message.append("If a module is not intended, exclude it or revert the dependency update that brought it in.").append(newline)
+        }
+
+        if (removed.isNotEmpty()) {
+            message.append(newline).append("Modules that are listed in $expectedPath but not in the release:").append(newline)
+            for (module in removed) {
+                message.append("  - $module").append(newline)
+            }
+            message.append("To see what the release contains now, run ./gradlew --quiet $projectPath:dependencies --configuration runtimeClasspath, or read ${actualJars.get().asFile.relativeTo(rootDir)}.")
+                .append(newline)
+            message.append("If a module is not meant to leave, restore the dependency that provided it.").append(newline)
+        }
+
+        if (totalSize > sizeLimit) {
+            message.append(newline)
+                .append("The total size of all jars in the release, JMeter jars included, is $totalSize bytes (${totalSize / mib} MiB), ")
+                .append("which exceeds $sizeLimitPrefix$sizeLimit (${sizeLimit / mib} MiB) in $expectedPath by ${totalSize - sizeLimit} bytes.")
+                .append(newline)
+                .append("The largest jars now:").append(newline)
+            artifacts.sortedByDescending { it.file.length() }.take(5).forEach {
+                message.append("  ${it.file.length()} ${it.file.name}").append(newline)
+            }
+            message.append("If the growth is not intended, revert the dependency update that grew the jars.").append(newline)
+        }
+
+        message.append(newline)
+            .append("If the change is intended, run ./gradlew --quiet $path -PupdateExpectedJars and commit $expectedPath. ")
+            .append("Name the added or removed modules and the size growth in the pull request description, with the dependency update that caused them.")
+        throw GradleException(message.toString())
     }
 }
```

## r1/sonnet-old-1 (code M)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt.
Modules in the release but not in the file: org.example:foo
The jars total 88080384 bytes, which exceeds total-size-limit=87031808 by 1048576 bytes.
The per-jar sizes are in src/dist/build/dist/release_jars.csv.
If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars and commit src/dist/src/dist/expected_release_artifacts.txt.
```

### Reader reply

```markdown
**1. Failure.** The release jars don't match the expected list: `org.example:foo` is unexpected. They also total 1,048,576 bytes (1 MiB) over `total-size-limit`. The check keeps unreviewed jars and size growth out of shipped releases.

**2. Changes.** The output doesn't say what the update changed or which dependency added `org.example:foo`. Per-jar sizes are in `src/dist/build/dist/release_jars.csv`, which I couldn't read.

**3. Next.** `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars`, then `./gradlew build`. The expected-file path in the output looks doubled (`src/dist/src/dist/...`), so confirm it. The output doesn't say whether this task changes the size limit.

**4. If intended:** run the update, review its diff, and commit. Then decide the overage: raise the limit with a stated reason, or trim jars. **If not:** find what pulls in `org.example:foo` and exclude it, or revert the update.

**5. PR description:** the new `org.example:foo` jar, the 1 MiB overage, the expected-file change, and any limit change with its reason.
```

### Diff

```diff
diff --git a/src/dist/build.gradle.kts b/src/dist/build.gradle.kts
index 8349f05..1668374 100644
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,23 @@ val verifyReleaseDependencies by tasks.registering {
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        throw GradleException(
+            buildString {
+                append("The jars of the binary release do not match $expectedPath.")
+                if (added.isNotEmpty()) {
+                    append(newline).append("Modules in the release but not in the file: ").append(added.joinToString())
+                }
+                if (removed.isNotEmpty()) {
+                    append(newline).append("Modules in the file but not in the release: ").append(removed.joinToString())
+                }
+                if (totalSize > sizeLimit) {
+                    append(newline).append("The jars total $totalSize bytes, which exceeds total-size-limit=$sizeLimit by ${totalSize - sizeLimit} bytes.")
+                }
+                append(newline).append("The per-jar sizes are in ${actualJars.get().asFile.relativeTo(rootDir)}.")
+                append(newline).append("If the change is intended, run ./gradlew $path -PupdateExpectedJars and commit $expectedPath.")
+            }
+        )
     }
 }
```

## r1/sonnet-old-2 (code E)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt:
  - Modules in the binary release but not in src/dist/src/dist/expected_release_artifacts.txt: org.example:foo
  - The jars of the binary release total 88080384 bytes, which exceeds total-size-limit=87031808 by 1048576 bytes. The per-jar sizes are in src/dist/build/dist/release_jars.csv
If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars and commit the regenerated file. Otherwise, remove the dependency that brought in the extra modules or size.
```

### Reader reply

```markdown
**1. Failure:** The release-artifact check failed. It compares the binary release's jars to the expected list and enforces a size limit, so unreviewed dependencies don't ship unnoticed.

**2. Change:** The release now includes `org.example:foo`, which is missing from the expected list. The jars total 1,048,576 bytes (1 MiB) over the limit. The output doesn't say which dependency added `foo`. Per-jar sizes are in `src/dist/build/dist/release_jars.csv`, which I couldn't read.

**3. Next commands:** None run. The output only suggests the update command below.

**4. If intended:** Run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit the regenerated file. The output doesn't say whether this raises the size limit, so the build may still fail.

**If not:** Remove the dependency that brings in `org.example:foo`. The output doesn't say which one that is.

**5. PR description:** Note the new module, the 1 MiB size increase, and whether the expected list was regenerated.
```

### Diff

```diff
diff --git a/src/dist/build.gradle.kts b/src/dist/build.gradle.kts
index 8349f05..e3a8fe4 100644
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,26 @@ val verifyReleaseDependencies by tasks.registering {
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val problems = buildList {
+            if (added.isNotEmpty()) {
+                add("Modules in the binary release but not in ${expectedFile.relativeTo(rootDir)}: ${added.joinToString()}")
+            }
+            if (removed.isNotEmpty()) {
+                add("Modules in ${expectedFile.relativeTo(rootDir)} but not in the binary release: ${removed.joinToString()}")
+            }
+            if (totalSize > sizeLimit) {
+                add(
+                    "The jars of the binary release total $totalSize bytes, which exceeds $sizeLimitPrefix$sizeLimit by ${totalSize - sizeLimit} bytes. " +
+                        "The per-jar sizes are in ${actualJars.get().asFile.relativeTo(rootDir)}"
+                )
+            }
+        }
+        throw GradleException(
+            "The jars of the binary release do not match ${expectedFile.relativeTo(rootDir)}:" + newline +
+                problems.joinToString(newline) { "  - $it" } + newline +
+                "If the change is intended, run ./gradlew $path -PupdateExpectedJars and commit the regenerated file. " +
+                "Otherwise, remove the dependency that brought in the extra modules or size."
+        )
     }
 }
```

## r1/sonnet-old-3 (code L)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt:
  - Modules in the release but not in the expected file: org.example:foo
  - The jars total 88080384 bytes, which exceeds total-size-limit=87031808 bytes
If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars and commit the updated file. The jars that were checked are listed in /home/user/jmeter/src/dist/build/dist/release_jars.csv.
```

### Reader reply

```markdown
**1. Failure:** The release-jar check failed. Shipped jars don't match `expected_release_artifacts.txt`, and total size exceeds the limit. The check keeps shipped contents and size reviewed.

**2. Changed:** The release now includes `org.example:foo`, which isn't expected. Total size is 1,048,576 bytes (1 MiB) over the limit. The output doesn't say what added `foo` or which version.

**3. Next:** I'd read `/home/user/jmeter/src/dist/build/dist/release_jars.csv` to trace `foo`. That path isn't in my working directory, so confirm it's your checkout.

**4. If intended:** Run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit the updated file. The output doesn't say that flag changes the size limit, so review that separately. If not intended: remove the dependency that added `foo`, then rerun `./gradlew build`.

**5. PR description:** Note the new `org.example:foo`, the 1 MiB size increase, and why the expected file or size limit changed.
```

### Diff

```diff
diff --git a/src/dist/build.gradle.kts b/src/dist/build.gradle.kts
index 8349f05..ee08ae7 100644
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,23 @@ val verifyReleaseDependencies by tasks.registering {
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val problems = buildList {
+            if (added.isNotEmpty()) {
+                add("Modules in the release but not in the expected file: ${added.joinToString()}")
+            }
+            if (removed.isNotEmpty()) {
+                add("Modules in the expected file but not in the release: ${removed.joinToString()}")
+            }
+            if (totalSize > sizeLimit) {
+                add("The jars total $totalSize bytes, which exceeds total-size-limit=$sizeLimit bytes")
+            }
+        }
+        throw GradleException(
+            "The jars of the binary release do not match ${expectedFile.relativeTo(rootDir)}:" + newline +
+                problems.joinToString(newline) { "  - $it" } + newline +
+                "If the change is intended, run ./gradlew $path -PupdateExpectedJars and commit the updated file. " +
+                "The jars that were checked are listed in ${actualJars.get().asFile}."
+        )
     }
 }
```

## r2/haiku-new-1 (code V)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt.
The check catches dependencies that enter the release unnoticed, often transitively, and growth of the release beyond its size limit.

Modules in the release that src/dist/src/dist/expected_release_artifacts.txt does not list:
  + org.example:foo (foo-1.2.jar (1048576 bytes))
To see which dependency brings it in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
If a module is not intended, exclude it or revert the dependency update that brought it in.

The total size of all jars in the release, JMeter jars included, is 88080384 bytes (about 84.0 MiB).
That exceeds total-size-limit=87031808 in src/dist/src/dist/expected_release_artifacts.txt by 1048576 bytes. The largest jars now:
  12582912 bytes  bcprov-jdk18on-1.78.jar
  9437184 bytes  groovy-4.0.21.jar
  5242880 bytes  jmeter-core.jar
  4194304 bytes  xstream-1.4.20.jar
  3145728 bytes  rhino-1.7.14.jar
If the growth is not intended, revert the dependency update that grew the jars.

If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars and commit src/dist/src/dist/expected_release_artifacts.txt. The command sets total-size-limit to the current total size plus 5 MiB, rounded up to a whole MiB. Name the added or removed modules and the size growth in the pull request description, with the dependency update that caused them.
```

### Reader reply

```markdown
**1. Failed:** The release-contents check compares release jars with `expected_release_artifacts.txt`. It catches unlisted, often transitive, dependencies and size growth. It flagged unlisted `org.example:foo` (1 MiB), and the total is 1048576 bytes over its limit.

**2. Changed:** The output doesn't show the diff or which update added `foo`.

**3. Next:** I can't run commands here. The output's suggested command is:
`./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`

**4. If intended:** Run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit the expected-artifacts file. The limit becomes 89 MiB under the stated rule. **If not:** Exclude `foo` or revert the update that brought it in.

**5. PR description:** List `org.example:foo` as added, the size growth, and the responsible update. The output gives no earlier total, so the growth beyond the 1 MiB overage is unknown.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -267,11 +267,67 @@
 
         val added = jarsByModule.keys - expectedModules
         val removed = expectedModules.sortedWith(caseInsensitive) - jarsByModule.keys
-        if (added.isEmpty() && removed.isEmpty() && totalSize <= sizeLimit) {
+        val sizeExceeded = totalSize > sizeLimit
+        if (added.isEmpty() && removed.isEmpty() && !sizeExceeded) {
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        // Each branch has its own cause and its own remedy, and one run can fire several branches
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val problems = mutableListOf<String>()
+        if (added.isNotEmpty()) {
+            problems += buildString {
+                appendLine("Modules in the release that $expectedPath does not list:")
+                for (module in added.sortedWith(caseInsensitive)) {
+                    val jars = jarsByModule.getValue(module).joinToString { "${it.file.name} (${it.file.length()} bytes)" }
+                    appendLine("  + $module ($jars)")
+                    appendLine(
+                        "To see which dependency brings it in, run " +
+                            "./gradlew $projectPath:dependencyInsight --configuration runtimeClasspath --dependency $module"
+                    )
+                }
+                append("If a module is not intended, exclude it or revert the dependency update that brought it in.")
+            }
+        }
+        if (removed.isNotEmpty()) {
+            problems += buildString {
+                appendLine("Modules that $expectedPath lists but the release no longer contains:")
+                removed.forEach { appendLine("  - $it") }
+                append(
+                    "If a removal is not intended, restore the dependency that provided the module. " +
+                        "Check the build files for a removed or narrowed declaration."
+                )
+            }
+        }
+        if (sizeExceeded) {
+            problems += buildString {
+                val mibText = String.format(java.util.Locale.ROOT, "%.1f", totalSize.toDouble() / mib)
+                appendLine("The total size of all jars in the release, JMeter jars included, is $totalSize bytes (about $mibText MiB).")
+                appendLine("That exceeds total-size-limit=$sizeLimit in $expectedPath by ${totalSize - sizeLimit} bytes. The largest jars now:")
+                artifacts.sortedByDescending { it.file.length() }.take(5).forEach {
+                    appendLine("  ${it.file.length()} bytes  ${it.file.name}")
+                }
+                append("If the growth is not intended, revert the dependency update that grew the jars.")
+            }
+        }
+
+        throw GradleException(
+            buildString {
+                appendLine("The jars of the binary release do not match $expectedPath.")
+                appendLine(
+                    "The check catches dependencies that enter the release unnoticed, often transitively, " +
+                        "and growth of the release beyond its size limit."
+                )
+                problems.forEach { appendLine(); appendLine(it) }
+                appendLine()
+                append(
+                    "If the change is intended, run ./gradlew $path -PupdateExpectedJars and commit $expectedPath. " +
+                        "The command sets total-size-limit to the current total size plus ${releaseJarsSizeHeadroom / mib} MiB, " +
+                        "rounded up to a whole MiB. Name the added or removed modules and the size growth " +
+                        "in the pull request description, with the dependency update that caused them."
+                )
+            }
+        )
     }
 }
```

## r2/haiku-new-2 (code H)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter or leave the release unnoticed, often transitively, and unexpected growth of the release. The full list of jars is in src/dist/build/dist/release_jars.csv.

Modules that are in the release but not in src/dist/src/dist/expected_release_artifacts.txt:
  + org.example:foo (foo-1.2.jar)
    To see which dependency brings it in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
If a module is not intended, exclude it or revert the dependency update that brought it in.

The total size of all jars in the release, JMeter jars included, is 88080384 bytes.
That exceeds total-size-limit=87031808 in src/dist/src/dist/expected_release_artifacts.txt by 1048576 bytes.
The largest jars are:
  12582912 bcprov-jdk18on-1.78.jar
  9437184 groovy-4.0.21.jar
  5242880 jmeter-core.jar
  4194304 xstream-1.4.20.jar
  3145728 rhino-1.7.14.jar
If the growth is not intended, revert the dependency update that grew the jars.

If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars and commit src/dist/src/dist/expected_release_artifacts.txt. In the pull request description, name the added or removed modules and the size growth, and the dependency update that caused them.
```

### Reader reply

```markdown
**1. Failure:** `verifyReleaseDependencies` failed because the release jars don't match `expected_release_artifacts.txt`. The check catches dependencies that enter or leave the release unnoticed, often transitively, and unexpected size growth.

**2. Changed:** `org.example:foo` (foo-1.2.jar) is in the release but not expected. The total is 88080384 bytes, 1048576 bytes (1 MiB) over the 87031808 limit. The output doesn't give the previous size, foo's jar size, or which update added foo.

**3. Next command (from output):**
`./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`
I'd run this to find what pulls in foo. I can't run it here.

**4. If intended:** run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit `src/dist/src/dist/expected_release_artifacts.txt`. Check that path first, since it looks doubled. **If not intended:** exclude foo or revert the dependency update.

**5. PR description:** name foo as added, the 1 MiB size growth over the limit, and the dependency update that caused them, once `dependencyInsight` identifies it.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,46 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        // Each branch that fires is reported, so one failure shows every mismatch and its remedy
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val problems = mutableListOf<String>()
+        if (added.isNotEmpty()) {
+            problems += buildString {
+                appendLine("Modules that are in the release but not in $expectedPath:")
+                for (module in added) {
+                    val files = jarsByModule.getValue(module).joinToString { it.file.name }
+                    appendLine("  + $module ($files)")
+                    appendLine("    To see which dependency brings it in, run ./gradlew $projectPath:dependencyInsight --configuration runtimeClasspath --dependency $module")
+                }
+                append("If a module is not intended, exclude it or revert the dependency update that brought it in.")
+            }
+        }
+        if (removed.isNotEmpty()) {
+            problems += buildString {
+                appendLine("Modules that are in $expectedPath but not in the release:")
+                removed.forEach { appendLine("  - $it") }
+                append("If the removal is not intended, restore the dependency that provided these modules.")
+            }
+        }
+        if (totalSize > sizeLimit) {
+            problems += buildString {
+                appendLine("The total size of all jars in the release, JMeter jars included, is $totalSize bytes.")
+                appendLine("That exceeds total-size-limit=$sizeLimit in $expectedPath by ${totalSize - sizeLimit} bytes.")
+                appendLine("The largest jars are:")
+                artifacts.sortedByDescending { it.file.length() }.take(5).forEach {
+                    appendLine("  ${it.file.length()} ${it.file.name}")
+                }
+                append("If the growth is not intended, revert the dependency update that grew the jars.")
+            }
+        }
+
+        val header = "The jars of the binary release do not match $expectedPath. The check catches dependencies that " +
+            "enter or leave the release unnoticed, often transitively, and unexpected growth of the release. " +
+            "The full list of jars is in ${actualJars.get().asFile.relativeTo(rootDir)}."
+        val accept = "If the change is intended, run ./gradlew $path -PupdateExpectedJars and commit $expectedPath. " +
+            "In the pull request description, name the added or removed modules and the size growth, " +
+            "and the dependency update that caused them."
+        throw GradleException((listOf(header) + problems + listOf(accept)).joinToString(newline + newline))
     }
 }
```

## r2/haiku-new-3 (code K)

### Rendered message

```text
Release dependencies do not match src/dist/src/dist/expected_release_artifacts.txt: modules added to the release: org.example:foo; total size of jars is 88080384 bytes, which exceeds total-size-limit=87031808 by 1048576 bytes. If the change is intended, regenerate the file with ./gradlew :src:dist -PupdateExpectedJars
```

### Reader reply

```markdown
**1. Failure:** The release-dependency check failed for two reasons. `org.example:foo` is newly in the release but missing from `src/dist/expected_release_artifacts.txt`, and total jar size is 1,048,576 bytes (1 MiB) over `total-size-limit`. The check catches unreviewed dependencies and distribution bloat.

**2. Changed:** The output doesn't show the diff, so I can't say which dependency brought in `org.example:foo` or whether it is direct or transitive.

**3. Next command:** Only the one in the output, which I have not run: `./gradlew :src:dist -PupdateExpectedJars`

**4. If intended:** Run that command and review the diff to `expected_release_artifacts.txt`. The output doesn't say whether regenerating fixes the size overage, or how to change `total-size-limit`. **If not intended:** Don't regenerate. Find what pulled in `org.example:foo` and exclude or revert it.

**5. PR description:** Name the added `org.example:foo` and the 1 MiB size increase. If you regenerated the list or changed the limit, say so and why.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -267,11 +267,25 @@
 
         val added = jarsByModule.keys - expectedModules
         val removed = expectedModules.sortedWith(caseInsensitive) - jarsByModule.keys
-        if (added.isEmpty() && removed.isEmpty() && totalSize <= sizeLimit) {
+        val sizeExceeded = totalSize > sizeLimit
+        if (added.isEmpty() && removed.isEmpty() && !sizeExceeded) {
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val problems = mutableListOf<String>()
+        if (added.isNotEmpty()) {
+            problems += "modules added to the release: ${added.joinToString()}"
+        }
+        if (removed.isNotEmpty()) {
+            problems += "modules missing from the release: ${removed.joinToString()}"
+        }
+        if (sizeExceeded) {
+            problems += "total size of jars is $totalSize bytes, which exceeds total-size-limit=$sizeLimit by ${totalSize - sizeLimit} bytes"
+        }
+        throw GradleException(
+            "Release dependencies do not match ${expectedFile.relativeTo(rootDir)}: ${problems.joinToString("; ")}. " +
+                "If the change is intended, regenerate the file with ./gradlew $projectPath -PupdateExpectedJars"
+        )
     }
 }
```

## r2/haiku-old-1 (code B)

### Rendered message

```text
Release dependencies do not match src/dist/src/dist/expected_release_artifacts.txt: modules added to the release: org.example:foo; total size of the jars is 88080384 bytes, which exceeds total-size-limit=87031808 by 1048576 bytes. If the change is intended, regenerate the file with ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars
```

### Reader reply

```markdown
1. **Failure:** `verifyReleaseDependencies` failed. It compares release jars against `expected_release_artifacts.txt` and a size budget, catching unreviewed dependencies.

2. **Change:** Module `org.example:foo` was added. Jars total 88,080,384 bytes, 1,048,576 bytes (1 MiB) over the 87,031,808 limit. The output omits foo's version and whether it's direct or transitive.

3. **Next:** Nothing yet. The only suggested command rewrites the expected file: `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars`.

4. **If intended:** Review foo's license and need, then run that command. The output doesn't say whether it changes `total-size-limit`, so the size overage may need a separate change. **If not:** Find what pulled in foo (I can't inspect the build), remove it, and rerun the build.

5. **PR description:** Name `org.example:foo` and its purpose, the 1 MiB size increase, any limit change, and the license review.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,22 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val problems = mutableListOf<String>()
+        if (added.isNotEmpty()) {
+            problems.add("modules added to the release: ${added.joinToString()}")
+        }
+        if (removed.isNotEmpty()) {
+            problems.add("modules removed from the release: ${removed.joinToString()}")
+        }
+        if (totalSize > sizeLimit) {
+            problems.add(
+                "total size of the jars is $totalSize bytes, which exceeds total-size-limit=$sizeLimit by ${totalSize - sizeLimit} bytes"
+            )
+        }
+        throw GradleException(
+            "Release dependencies do not match ${expectedFile.relativeTo(rootDir)}: ${problems.joinToString("; ")}. " +
+                "If the change is intended, regenerate the file with ./gradlew $path -PupdateExpectedJars"
+        )
     }
 }
```

## r2/haiku-old-2 (code W)

### Rendered message

```text
Release dependencies do not match: modules in the release but not in src/dist/src/dist/expected_release_artifacts.txt: org.example:foo; the jars total 88080384 bytes, over total-size-limit=87031808 by 1048576 bytes. If the change is intended, regenerate src/dist/src/dist/expected_release_artifacts.txt with ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars
```

### Reader reply

```markdown
**1. Failure:** `verifyReleaseDependencies` failed. It checks the release's jars against an expected-artifacts list and a size cap. `org.example:foo` is unexpected, and the jars exceed the limit by 1048576 bytes (1 MiB).

**2. Change:** The output doesn't show the diff, the version change, or whether `foo` is direct or transitive.

**3. Next:** Nothing has been run. The output suggests `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars`, but its path looks doubled (`src/dist/src/dist/`), so confirm the path first. Regenerating the list won't fix the size overage.

**4. If intended:** Regenerate the list, then trim the size or raise `total-size-limit`. The output doesn't say where that limit is set. If not intended: find what pulls in `foo` and exclude or revert it.

**5. PR description:** Note the new `foo` artifact and why it's needed, the 1 MiB overage and how it was resolved, any change to the list or limit, and that the build currently fails.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,21 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val problems = mutableListOf<String>()
+        if (added.isNotEmpty()) {
+            problems += "modules in the release but not in $expectedPath: ${added.joinToString()}"
+        }
+        if (removed.isNotEmpty()) {
+            problems += "modules in $expectedPath but not in the release: ${removed.joinToString()}"
+        }
+        if (totalSize > sizeLimit) {
+            problems += "the jars total $totalSize bytes, over total-size-limit=$sizeLimit by ${totalSize - sizeLimit} bytes"
+        }
+        throw GradleException(
+            "Release dependencies do not match: " + problems.joinToString("; ") +
+                ". If the change is intended, regenerate $expectedPath with ./gradlew $projectPath:verifyReleaseDependencies -PupdateExpectedJars"
+        )
     }
 }
```

## r2/haiku-old-3 (code P)

### Rendered message

```text
Release dependencies do not match:
  - modules are in the release but not in src/dist/src/dist/expected_release_artifacts.txt: org.example:foo
  - the jars total 88080384 bytes, which exceeds total-size-limit=87031808 by 1048576 bytes
If the change is intended, regenerate the expected file with ./gradlew :src:dist -PupdateExpectedJars
```

### Reader reply

```markdown
**1. Failure:** The release-contents check failed. It compares the distribution's jars against a checked-in list and a size cap, which likely exists to catch unreviewed additions and bloat (inferred; the output doesn't say). Two violations: `org.example:foo` is in the release but not in the expected list, and the jars are 1,048,576 bytes (1 MiB) over the limit. The expected-file path in the output reads `src/dist/src/dist/...`, which may be a typo.

**2. What changed:** I can't see the diff. The output doesn't say which change added `foo` or grew the jars.

**3. Next commands:** I haven't run anything. For an intended change: `./gradlew :src:dist -PupdateExpectedJars`

**4. If intended:** Run that command, review the expected-file diff, and commit it. The 1 MiB overage still needs a decision; the output doesn't say whether to raise `total-size-limit`.
**If not intended:** Find what pulls in `org.example:foo` (the output doesn't say), exclude or remove it, and rerun the build.

**5. PR description:** Mention the new `org.example:foo` module, the 1 MiB size increase, the regenerated expected list if applicable, and any limit change.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -267,11 +267,26 @@
 
         val added = jarsByModule.keys - expectedModules
         val removed = expectedModules.sortedWith(caseInsensitive) - jarsByModule.keys
-        if (added.isEmpty() && removed.isEmpty() && totalSize <= sizeLimit) {
+        val oversize = totalSize > sizeLimit
+        if (added.isEmpty() && removed.isEmpty() && !oversize) {
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val problems = buildList {
+            if (added.isNotEmpty()) {
+                add("modules are in the release but not in ${expectedFile.relativeTo(rootDir)}: " + added.sortedWith(caseInsensitive).joinToString())
+            }
+            if (removed.isNotEmpty()) {
+                add("modules are in ${expectedFile.relativeTo(rootDir)} but not in the release: " + removed.joinToString())
+            }
+            if (oversize) {
+                add("the jars total $totalSize bytes, which exceeds total-size-limit=$sizeLimit by ${totalSize - sizeLimit} bytes")
+            }
+        }
+        throw GradleException(
+            "Release dependencies do not match:" + problems.joinToString(prefix = newline, separator = newline) { "  - $it" } +
+                "${newline}If the change is intended, regenerate the expected file with ./gradlew $projectPath -PupdateExpectedJars"
+        )
     }
 }
```

## r2/sonnet-new-1 (code C)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.

Modules that are in the release but not in src/dist/src/dist/expected_release_artifacts.txt:
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings a module in, run
  ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency <group:module>
with the group and module from the list above, for example org.example:foo.
If a module is not intended, exclude it or revert the dependency update that brought it in.

The total size of all jars in the release, JMeter jars included, is 88080384 bytes (84 MiB), which exceeds total-size-limit=87031808 (83 MiB) in src/dist/src/dist/expected_release_artifacts.txt by 1048576 bytes.
The largest jars now:
  12582912 bcprov-jdk18on-1.78.jar
  9437184 groovy-4.0.21.jar
  5242880 jmeter-core.jar
  4194304 xstream-1.4.20.jar
  3145728 rhino-1.7.14.jar
The full list is in src/dist/build/dist/release_jars.csv.
If the growth is not intended, revert the dependency update that grew the jars.

If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars and commit src/dist/src/dist/expected_release_artifacts.txt. The regenerated total-size-limit is the current total size plus 5 MiB, rounded up to a whole MiB.
Name the added or removed modules and the size change in the pull request description, with the dependency update that caused them.
```

### Reader reply

```markdown
1. **Failed:** The release jars don't match `src/dist/src/dist/expected_release_artifacts.txt`. The check catches dependencies that enter the release unnoticed, often transitively, and unexpected size growth. It found an unexpected module, `org.example:foo` (1048576 bytes), and a total of 88080384 bytes, 1048576 bytes over the 83 MiB limit.

2. **Changed:** The output doesn't show the previous release contents or total, so I can't confirm exactly what the update changed.

3. **Next:**
   `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`
   The output doesn't say which dependency brings in `foo`.

4. **If intended:** Confirm `foo` is wanted, then run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit the regenerated expected-artifacts file. The new limit should be 89 MiB. This directory isn't a git repo, so check the commit step. **If not:** Exclude `foo` or revert the dependency update that added it.

5. **PR description:** Name `foo` as added (1048576 bytes), the size change to 84 MiB, and the dependency update that caused them. Confirm the cause with the dependency insight output first.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,63 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        fun inMib(bytes: Long) = "${bytes / mib} MiB"
+        val message = buildString {
+            appendLine(
+                "The jars of the binary release do not match $expectedPath. " +
+                    "The check catches dependencies that enter the release unnoticed, often transitively, " +
+                    "and unexpected growth of the release."
+            )
+            if (added.isNotEmpty()) {
+                appendLine()
+                appendLine("Modules that are in the release but not in $expectedPath:")
+                for (module in added) {
+                    val files = jarsByModule.getValue(module)
+                    appendLine("  + $module (${files.joinToString { "${it.file.name}, ${it.file.length()} bytes" }})")
+                }
+                appendLine("To see which dependency brings a module in, run")
+                appendLine(
+                    "  ./gradlew $projectPath:dependencyInsight --configuration runtimeClasspath --dependency <group:module>"
+                )
+                appendLine("with the group and module from the list above, for example ${added.first()}.")
+                appendLine("If a module is not intended, exclude it or revert the dependency update that brought it in.")
+            }
+            if (removed.isNotEmpty()) {
+                appendLine()
+                appendLine("Modules that are in $expectedPath but no longer in the release:")
+                for (module in removed) {
+                    appendLine("  - $module")
+                }
+                appendLine("To see the current dependency tree, run ./gradlew $projectPath:dependencies --configuration runtimeClasspath")
+                appendLine("If a module is not intended to go away, restore the dependency that provided it.")
+            }
+            if (totalSize > sizeLimit) {
+                appendLine()
+                appendLine(
+                    "The total size of all jars in the release, JMeter jars included, is $totalSize bytes (${inMib(totalSize)}), " +
+                        "which exceeds total-size-limit=$sizeLimit (${inMib(sizeLimit)}) in $expectedPath " +
+                        "by ${totalSize - sizeLimit} bytes."
+                )
+                appendLine("The largest jars now:")
+                for (artifact in artifacts.sortedByDescending { it.file.length() }.take(5)) {
+                    appendLine("  ${artifact.file.length()} ${artifact.file.name}")
+                }
+                appendLine("The full list is in ${actualJars.get().asFile.relativeTo(rootDir)}.")
+                appendLine("If the growth is not intended, revert the dependency update that grew the jars.")
+            }
+            appendLine()
+            appendLine(
+                "If the change is intended, run ./gradlew $projectPath:verifyReleaseDependencies -PupdateExpectedJars " +
+                    "and commit $expectedPath. The regenerated total-size-limit is the current total size plus " +
+                    "${releaseJarsSizeHeadroom / mib} MiB, rounded up to a whole MiB."
+            )
+            append(
+                "Name the added or removed modules and the size change in the pull request description, " +
+                    "with the dependency update that caused them."
+            )
+        }
+        throw GradleException(message)
     }
 }
```

## r2/sonnet-new-2 (code N)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.

Modules that are in the release but not in src/dist/src/dist/expected_release_artifacts.txt:
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings a module in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
If a module is not intended, exclude it or revert the dependency update that brought it in.

The total size of all jars in the release, JMeter jars included, is 88080384 bytes (84 MiB), which exceeds total-size-limit=87031808 (83 MiB) in src/dist/src/dist/expected_release_artifacts.txt by 1048576 bytes.
The largest jars now:
  12582912 bcprov-jdk18on-1.78.jar
  9437184 groovy-4.0.21.jar
  5242880 jmeter-core.jar
  4194304 xstream-1.4.20.jar
  3145728 rhino-1.7.14.jar
The full list is in src/dist/build/dist/release_jars.csv.
If the growth is not intended, revert the dependency update that grew the jars.

If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars and commit src/dist/src/dist/expected_release_artifacts.txt. Name the added or removed modules and the size growth in the pull request description, with the dependency update that caused them.
```

### Reader reply

```markdown
**1. Failure:** The release jars don't match `src/dist/src/dist/expected_release_artifacts.txt`. Unlisted module `org.example:foo` (1 MiB) entered the release, and total jar size exceeds the limit by 1048576 bytes. The check catches unnoticed, often transitive, dependencies and unplanned growth.

**2. Change:** The output doesn't show the dependency diff or which update caused it.

**3. Next:** `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`. I couldn't open `src/dist/build/dist/release_jars.csv`, so I can't confirm the full jar list.

**4. Intended:** Run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` and commit the updated expected list. **Not intended:** Exclude `org.example:foo` or revert the dependency update.

**5. PR description:** Name `org.example:foo` as added, state the 1048576-byte growth, and name the dependency update that caused them.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,59 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val message = StringBuilder()
+        message.append(
+            "The jars of the binary release do not match $expectedPath. " +
+                "The check catches dependencies that enter the release unnoticed, often transitively, " +
+                "and unexpected growth of the release."
+        ).append(newline)
+
+        if (added.isNotEmpty()) {
+            message.append(newline)
+                .append("Modules that are in the release but not in $expectedPath:").append(newline)
+            for (module in added) {
+                message.append("  + $module (")
+                    .append(jarsByModule.getValue(module).joinToString { "${it.file.name}, ${it.file.length()} bytes" })
+                    .append(')').append(newline)
+            }
+            val example = added.first().split(':').take(2).joinToString(":")
+            message.append("To see which dependency brings a module in, run ")
+                .append("./gradlew $projectPath:dependencyInsight --configuration runtimeClasspath --dependency $example")
+                .append(newline)
+                .append("If a module is not intended, exclude it or revert the dependency update that brought it in.")
+                .append(newline)
+        }
+
+        if (removed.isNotEmpty()) {
+            message.append(newline)
+                .append("Modules that are in $expectedPath but not in the release:").append(newline)
+            for (module in removed) {
+                message.append("  - $module").append(newline)
+            }
+            message.append("If a module should still be in the release, restore the dependency that brought it in.")
+                .append(newline)
+        }
+
+        if (totalSize > sizeLimit) {
+            message.append(newline)
+                .append("The total size of all jars in the release, JMeter jars included, is $totalSize bytes (${totalSize / mib} MiB), ")
+                .append("which exceeds $sizeLimitPrefix$sizeLimit (${sizeLimit / mib} MiB) in $expectedPath ")
+                .append("by ${totalSize - sizeLimit} bytes.").append(newline)
+                .append("The largest jars now:").append(newline)
+            artifacts.sortedByDescending { it.file.length() }.take(5).forEach {
+                message.append("  ${it.file.length()} ${it.file.name}").append(newline)
+            }
+            message.append("The full list is in ${actualJars.get().asFile.relativeTo(rootDir)}.").append(newline)
+                .append("If the growth is not intended, revert the dependency update that grew the jars.")
+                .append(newline)
+        }
+
+        message.append(newline)
+            .append("If the change is intended, run ./gradlew $path -PupdateExpectedJars and commit $expectedPath. ")
+            .append("Name the added or removed modules and the size growth in the pull request description, ")
+            .append("with the dependency update that caused them.")
+        throw GradleException(message.toString())
     }
 }
```

## r2/sonnet-new-3 (code Q)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.

Modules in the release that src/dist/src/dist/expected_release_artifacts.txt does not list:
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings a module in, run, for example:
  ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
If a module is not intended, exclude it or revert the dependency change that brought it in.

The total size of all jars in the release, JMeter jars included, is 88080384 bytes (84.0 MiB). That exceeds total-size-limit=87031808 (83.0 MiB) in src/dist/src/dist/expected_release_artifacts.txt by 1048576 bytes.
The largest jars now:
  12582912 bcprov-jdk18on-1.78.jar
  9437184 groovy-4.0.21.jar
  5242880 jmeter-core.jar
  4194304 xstream-1.4.20.jar
  3145728 rhino-1.7.14.jar
The sizes of all jars are in src/dist/build/dist/release_jars.csv. If the growth is not intended, revert the dependency change that grew the jars.

If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars and commit src/dist/src/dist/expected_release_artifacts.txt. In the pull request description, name the added or removed modules and the size growth, together with the dependency change that caused them.
```

### Reader reply

```markdown
1. **Failed:** the release-jar check in `:src:dist`. The release jars don't match `expected_release_artifacts.txt`. The check catches unnoticed (often transitive) dependencies and unexpected growth. It found an unlisted module, `org.example:foo` (1 MiB), and a total jar size over its limit by 1048576 bytes.

2. **Changed:** The output doesn't show the dependency change. It adds `org.example:foo` and grows the release by about 1 MiB. It doesn't identify the change responsible.

3. **Next:** `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo`, to find what pulls in foo.

4. **If intended:** run `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars`, then commit `src/dist/src/dist/expected_release_artifacts.txt`.
**If not:** exclude foo, or revert the dependency change that brought it in.

5. **PR description:** name `org.example:foo` as added, the 1 MiB growth, and the responsible dependency change. The output doesn't identify that change, so get it from dependencyInsight.
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
@@ -271,7 +272,52 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir).invariantSeparatorsPath
+        fun mibs(bytes: Long) = "%.1f MiB".format(Locale.ROOT, bytes.toDouble() / mib)
+        val paragraphs = mutableListOf(
+            "The jars of the binary release do not match $expectedPath. " +
+                "The check catches dependencies that enter the release unnoticed, often transitively, " +
+                "and unexpected growth of the release."
+        )
+        if (added.isNotEmpty()) {
+            paragraphs += buildString {
+                appendLine("Modules in the release that $expectedPath does not list:")
+                for (module in added) {
+                    val jars = jarsByModule.getValue(module)
+                    appendLine("  + $module (${jars.joinToString { "${it.file.name}, ${it.file.length()} bytes" }})")
+                }
+                appendLine("To see which dependency brings a module in, run, for example:")
+                appendLine("  ./gradlew $projectPath:dependencyInsight --configuration runtimeClasspath --dependency ${added.first().split(':').take(2).joinToString(":")}")
+                append("If a module is not intended, exclude it or revert the dependency change that brought it in.")
+            }
+        }
+        if (removed.isNotEmpty()) {
+            paragraphs += buildString {
+                appendLine("Modules that $expectedPath lists but the release no longer contains:")
+                for (module in removed) {
+                    appendLine("  - $module")
+                }
+                append("If a module is still needed, restore the dependency that provided it, or check that an exclude did not remove it.")
+            }
+        }
+        if (totalSize > sizeLimit) {
+            paragraphs += buildString {
+                appendLine(
+                    "The total size of all jars in the release, JMeter jars included, is $totalSize bytes (${mibs(totalSize)}). " +
+                        "That exceeds $sizeLimitPrefix$sizeLimit (${mibs(sizeLimit)}) in $expectedPath by ${totalSize - sizeLimit} bytes."
+                )
+                appendLine("The largest jars now:")
+                for (artifact in artifacts.sortedByDescending { it.file.length() }.take(5)) {
+                    appendLine("  ${artifact.file.length()} ${artifact.file.name}")
+                }
+                append("The sizes of all jars are in ${actualJars.get().asFile.relativeTo(rootDir).invariantSeparatorsPath}. ")
+                append("If the growth is not intended, revert the dependency change that grew the jars.")
+            }
+        }
+        paragraphs += "If the change is intended, run ./gradlew $path -PupdateExpectedJars and commit $expectedPath. " +
+            "In the pull request description, name the added or removed modules and the size growth, " +
+            "together with the dependency change that caused them."
+        throw GradleException(paragraphs.joinToString("$newline$newline"))
     }
 }
```

## r2/sonnet-old-1 (code A)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt:
  - Modules in the release but not in src/dist/src/dist/expected_release_artifacts.txt: org.example:foo
  - The release jars total 88080384 bytes, which exceeds total-size-limit=87031808 by 1048576 bytes (see src/dist/build/dist/release_jars.csv for the size of each jar)
If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars and commit the updated file.
```

### Reader reply

```markdown
**1. Failure.** The release jars don't match the expected-artifacts list. The check catches unreviewed dependencies and size growth. Two problems: `org.example:foo` is new, and the release is 1,048,576 bytes (1 MiB) over the size limit. The path `src/dist/src/dist/...` looks doubled, and I can't verify it.

**2. Change.** The output doesn't show it. I can't see the diff, so I don't know what pulled in `foo`.

**3. Next.** I can't run anything. Check `src/dist/build/dist/release_jars.csv` for the largest jar. If the change is intended, the output's command is `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars`.

**4. If intended:** run that command, review the expected-file diff, and commit it. The output doesn't say whether the size limit also needs raising. **If not:** revert the dependency update, find what introduced `foo`, and rebuild.

**5. PR description:** Why `foo` is needed, the 1 MiB size increase, the expected-list update, and any size-limit change.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,25 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val problems = buildList {
+            if (added.isNotEmpty()) {
+                add("Modules in the release but not in ${expectedFile.relativeTo(rootDir)}: ${added.joinToString()}")
+            }
+            if (removed.isNotEmpty()) {
+                add("Modules in ${expectedFile.relativeTo(rootDir)} but not in the release: ${removed.joinToString()}")
+            }
+            if (totalSize > sizeLimit) {
+                add(
+                    "The release jars total $totalSize bytes, which exceeds total-size-limit=$sizeLimit by ${totalSize - sizeLimit} bytes " +
+                        "(see ${actualJars.get().asFile.relativeTo(rootDir)} for the size of each jar)"
+                )
+            }
+        }
+        throw GradleException(
+            "The jars of the binary release do not match ${expectedFile.relativeTo(rootDir)}:" +
+                problems.joinToString("") { "$newline  - $it" } +
+                "${newline}If the change is intended, run ./gradlew $path -PupdateExpectedJars and commit the updated file."
+        )
     }
 }
```

## r2/sonnet-old-2 (code R)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt.
  - Modules in the release that src/dist/src/dist/expected_release_artifacts.txt does not list: org.example:foo
  - The jars total 88080384 bytes, which exceeds total-size-limit=87031808 by 1048576 bytes
If the change is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars to regenerate the file.
```

### Reader reply

```markdown
**1. Failure:** The release-contents check failed. It compares release jars with a reviewed list. Two problems: `org.example:foo` isn't listed, and the jars exceed `total-size-limit` by 1048576 bytes (1 MiB). The expected-file path looks doubled (`src/dist/src/dist/...`), and I can't confirm the real path.

**2. Change:** The dependency update added `org.example:foo` to the release. The output doesn't say whether it's direct or transitive.

**3. Next:** `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` (from the output, not run). It may not clear the size failure, since the output doesn't say whether it changes the limit.

**4. If intended:** Review `org.example:foo` for origin, license, and need. Run that command, then decide on the size limit; I can't see where it's set. Rebuild.
**If not:** Find what pulled in `org.example:foo`, revert or pin it, and rebuild.

**5. PR description:** Note the new `org.example:foo`, the 1 MiB overage, the reason for the update, and any change to the expected list or size limit.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,22 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val problems = buildList {
+            if (added.isNotEmpty()) {
+                add("Modules in the release that ${expectedFile.relativeTo(rootDir)} does not list: ${added.joinToString()}")
+            }
+            if (removed.isNotEmpty()) {
+                add("Modules listed in ${expectedFile.relativeTo(rootDir)} that are missing from the release: ${removed.joinToString()}")
+            }
+            if (totalSize > sizeLimit) {
+                add("The jars total $totalSize bytes, which exceeds total-size-limit=$sizeLimit by ${totalSize - sizeLimit} bytes")
+            }
+        }
+        throw GradleException(
+            "The jars of the binary release do not match ${expectedFile.relativeTo(rootDir)}." + newline +
+                problems.joinToString(newline) { "  - $it" } + newline +
+                "If the change is intended, run ./gradlew $path -PupdateExpectedJars to regenerate the file."
+        )
     }
 }
```

## r2/sonnet-old-3 (code I)

### Rendered message

```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt:
  - modules in the release that src/dist/src/dist/expected_release_artifacts.txt does not list: org.example:foo
  - the jars total 88080384 bytes, which exceeds total-size-limit=87031808 by 1048576 bytes
If the change is intended, regenerate the file with ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars and commit it. The list of the actual jars is in /home/user/jmeter/src/dist/build/dist/release_jars.csv.
```

### Reader reply

```markdown
**1. Failed:** The release-artifact check. It compares release jars against the reviewed list and enforces a size budget, so unreviewed dependencies or bloat don't ship unnoticed.

**2. Changed:** The release adds unlisted `org.example:foo` and exceeds the size limit by 1 MiB. The output doesn't show the cause or whether `foo` is direct or transitive. The paths look inconsistent (`src/dist/src/dist/...`, `/home/user/...`), and I can't verify them.

**3. Next:** Only if intended: `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars`. Read the CSV first, after confirming the path exists.

**4. If intended:** Run it, review the regenerated list, and commit. This may not clear the size error. Raising the limit is a policy call the output doesn't settle. If not intended: revert the update or exclude `foo`, then rebuild.

**5. PR description:** Why `org.example:foo` is added, the size increase and any limit change, and that the expected list was regenerated.
```

### Diff

```diff
--- a/src/dist/build.gradle.kts
+++ b/src/dist/build.gradle.kts
@@ -271,7 +271,24 @@
             return@doLast
         }
 
-        throw GradleException("Release dependencies do not match")
+        val expectedPath = expectedFile.relativeTo(rootDir)
+        val problems = buildList {
+            if (added.isNotEmpty()) {
+                add("modules in the release that $expectedPath does not list: ${added.joinToString()}")
+            }
+            if (removed.isNotEmpty()) {
+                add("modules listed in $expectedPath that the release does not contain: ${removed.joinToString()}")
+            }
+            if (totalSize > sizeLimit) {
+                add("the jars total $totalSize bytes, which exceeds total-size-limit=$sizeLimit by ${totalSize - sizeLimit} bytes")
+            }
+        }
+        throw GradleException(
+            "The jars of the binary release do not match $expectedPath:" +
+                problems.joinToString("") { "$newline  - $it" } +
+                "${newline}If the change is intended, regenerate the file with ./gradlew $path -PupdateExpectedJars " +
+                "and commit it. The list of the actual jars is in ${actualJars.get().asFile}."
+        )
     }
 }
```
