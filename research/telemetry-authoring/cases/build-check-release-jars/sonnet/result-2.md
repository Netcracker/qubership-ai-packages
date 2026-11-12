```text
Release dependencies do not match src/dist/src/dist/expected_release_artifacts.txt.

Added modules (1):
  org.example:foo  foo-1.2.jar  1 MiB (1048576 bytes)
Removed modules (0).

Total jar size is 84 MiB (88080384 bytes), which exceeds total-size-limit=87031808 (83 MiB) by 1048576 bytes. The
size of foo-1.2.jar accounts for all of it.

The check keeps a dependency update from adding modules or growing the binary release without a reviewer seeing it.

Find what brings org.example:foo into the release:
  ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo

Then choose one:
  1. Keep the module out of the release. Exclude org.example:foo from the dependency that brings it in, or revert
     that update, and rerun :src:dist:verifyReleaseDependencies. Choose this if the update was not meant to add
     org.example:foo, or if the release does not need it.
  2. Accept the module and the new size. Run
       ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars
     This rewrites src/dist/src/dist/expected_release_artifacts.txt: it adds foo-1.2.jar and sets
     total-size-limit=88080384. Commit the file.
  3. Make room instead. The largest jars are bcprov-jdk18on-1.78.jar (8 MiB, 8388608 bytes), groovy-4.0.21.jar
     (7 MiB, 7340032 bytes), and rsyntaxtextarea-3.4.0.jar (1.5 MiB, 1572864 bytes).

If you accept the change, put this in the change description: the added module org.example:foo (foo-1.2.jar,
1048576 bytes), the dependency that brings it in (from the dependencyInsight output), and the new total-size-limit
(87031808 to 88080384).
```
