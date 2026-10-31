```text
Release dependencies do not match src/dist/src/dist/expected_release_artifacts.txt. The file lists every jar of the
binary release, so a reviewer sees each module that a dependency update adds, transitive ones included, and any growth
in the size of the release.

Modules added to the release (1):
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
Modules removed from the release: none

To see which dependency brings org.example:foo into the release, run:
  ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo

The total size of the jars is 88080384 bytes (84 MiB). It exceeds total-size-limit=87031808 (83 MiB) in
src/dist/src/dist/expected_release_artifacts.txt by 1048576 bytes (1 MiB). Without foo-1.2.jar, the total is 87031808
bytes, which is within the limit. The largest jars:
  8388608 bytes (8 MiB)      bcprov-jdk18on-1.78.jar
  7340032 bytes (7 MiB)      groovy-4.0.21.jar
  1572864 bytes (1.5 MiB)    rsyntaxtextarea-3.4.0.jar

If org.example:foo is not intended, exclude it from the dependency that brings it in, or revert that dependency update.
The release then has the expected modules and a total of 87031808 bytes, and this check passes.

If the module and the growth are intended, run:
  ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars
This rewrites src/dist/src/dist/expected_release_artifacts.txt from the current release, including total-size-limit.
Commit the file. In the pull request description, name org.example:foo (foo-1.2.jar, 1048576 bytes), the new total of
88080384 bytes (84 MiB), and the dependency update that brought the module in.
```
