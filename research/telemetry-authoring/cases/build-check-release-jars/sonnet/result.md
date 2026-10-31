```text
Release dependencies do not match src/dist/src/dist/expected_release_artifacts.txt.

Added modules (1):
  org.example:foo  foo-1.2.jar  1048576 bytes (1 MiB)
Removed modules: none

The jars total 88080384 bytes (84 MiB). That exceeds total-size-limit=87031808 (83 MiB) by 1048576 bytes.
The largest jars are:
  bcprov-jdk18on-1.78.jar      8388608 bytes (8 MiB)
  groovy-4.0.21.jar            7340032 bytes (7 MiB)
  rsyntaxtextarea-3.4.0.jar    1572864 bytes (1.5 MiB)

The file lists the expected modules and the size limit so that a reviewer sees every change to the contents or size
of the release.

To find which dependency brings org.example:foo into the release, run:
  ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo

Then choose one of these:
  - If the release should not contain foo, exclude it or revert the dependency update. Without foo the total is
    87031808 bytes, which equals total-size-limit, so the size check passes.
  - If the release should ship foo and grow by 1 MiB, run
      ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars
    It rewrites the expected file from the current release, adding foo-1.2.jar and updating total-size-limit.
    Raising total-size-limit by hand is not enough, because the added module fails the check on its own.
    Do not run it just to make the build pass: it accepts every added jar and the whole size increase.

If you update the expected file, put these in the change description: the added module org.example:foo
(foo-1.2.jar, 1048576 bytes), the dependency update that brought it in, and the change of total-size-limit from
87031808 to its new value.
```
