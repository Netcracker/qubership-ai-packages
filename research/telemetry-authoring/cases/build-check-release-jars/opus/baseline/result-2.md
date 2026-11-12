```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. This check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.

1 module was added to the release, and none was removed:
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings it in, run:
  ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo

The total size of the jars is 88080384 bytes (84 MiB). This exceeds total-size-limit=87031808 (83 MiB) in src/dist/src/dist/expected_release_artifacts.txt by 1048576 bytes (1 MiB), which is the size of foo-1.2.jar. Without foo-1.2.jar, the total would be 87031808 bytes, which does not exceed the limit. The largest jars are:
  8388608 (8 MiB)    bcprov-jdk18on-1.78.jar
  7340032 (7 MiB)    groovy-4.0.21.jar
  1572864 (1.5 MiB)  rsyntaxtextarea-3.4.0.jar

If org.example:foo is not intended, exclude it from the dependency that brings it in, or revert that dependency update. Either change also brings the total back to the limit.
If org.example:foo is intended, run:
  ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars
This rewrites src/dist/src/dist/expected_release_artifacts.txt from the current release, including total-size-limit. Review the diff and commit the file. In the pull request description, name org.example:foo (foo-1.2.jar, 1048576 bytes), the dependency update that brought it in, and the new total of 88080384 bytes compared with the previous total-size-limit=87031808.
```
