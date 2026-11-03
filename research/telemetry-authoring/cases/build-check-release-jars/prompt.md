Apache JMeter builds with Gradle. The task `:src:dist:verifyReleaseDependencies` compares the jars of the binary release
with the committed file `src/dist/src/dist/expected_release_artifacts.txt`, which lists one module per line with its jar
name and size, and ends with a line `total-size-limit=<bytes>`. The task fails when a module was added or removed, or
when the total size of the jars exceeds `total-size-limit`. Today it fails with the bare message
`Release dependencies do not match`.

What the build establishes:

- `./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars` rewrites the expected file from the current
  release, `total-size-limit` included, and the task then passes.
- `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency <group:name>` shows which
  dependency brings a module into the release.
- The task holds the list of added and removed modules with their jar names and sizes, and the size of every jar.

Scenario: a dependency update brought the module `org.example:foo` (`foo-1.2.jar`, 1048576 bytes) into the release; no
module left it. The total size of the jars is now 88080384 bytes, against `total-size-limit=87031808`. The largest jars
are `bcprov-jdk18on-1.78.jar` (8388608 bytes), `groovy-4.0.21.jar` (7340032 bytes), and `rsyntaxtextarea-3.4.0.jar`
(1572864 bytes).

Write the failure text the task prints in this scenario, as a person or an agent reading the build output sees it. Give
the text only.
