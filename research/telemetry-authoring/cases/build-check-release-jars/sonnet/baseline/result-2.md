```text
The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings it in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The total size of the jars is 88080384 bytes (84 MiB), which exceeds total-size-limit=87031808 (83 MiB) in src/dist/src/dist/expected_release_artifacts.txt. The new module accounts for the whole excess of 1048576 bytes (1 MiB). The largest jars now:
  8388608 bcprov-jdk18on-1.78.jar
  7340032 groovy-4.0.21.jar
  1572864 rsyntaxtextarea-3.4.0.jar
If the module is not intended, exclude it or revert the dependency update that brought it in. Without foo-1.2.jar the total is 87031808 bytes, which is within total-size-limit. If the module is intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, which adds org.example:foo to the file and also raises total-size-limit. Then commit the file and name the module, the size growth of 1048576 bytes, and the dependency update in the pull request description.
```
