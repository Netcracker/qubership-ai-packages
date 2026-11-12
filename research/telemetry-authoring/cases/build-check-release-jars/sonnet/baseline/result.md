The jars of the binary release do not match src/dist/src/dist/expected_release_artifacts.txt. The check catches dependencies that enter the release unnoticed, often transitively, and unexpected growth of the release.
  + org.example:foo (foo-1.2.jar, 1048576 bytes)
To see which dependency brings it in, run ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo
The total size of the jars is 88080384 bytes (84 MiB), which exceeds total-size-limit=87031808 (83 MiB) in src/dist/src/dist/expected_release_artifacts.txt. The largest jars now:
  8388608 bcprov-jdk18on-1.78.jar
  7340032 groovy-4.0.21.jar
  1572864 rsyntaxtextarea-3.4.0.jar
If the module is not intended, exclude it or revert the dependency update that brought it in. If the growth is not intended, revert the update that grew the jars. If both are intended, run ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars, which also raises total-size-limit, commit the file, and name the module (org.example:foo), the size growth (1048576 bytes, 1 MiB), and the dependency update in the pull request description.
