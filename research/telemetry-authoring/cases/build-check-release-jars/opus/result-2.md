```text
Release dependencies do not match src/dist/src/dist/expected_release_artifacts.txt.
  Added modules:   org.example:foo (foo-1.2.jar, 1048576 bytes)
  Removed modules: none
  Total size of the jars is 84 MiB (88080384 bytes), which exceeds total-size-limit=87031808 (83 MiB) by 1 MiB (1048576 bytes).

The file lists every module in the binary release and limits the total size of its jars. A reviewer then sees each module a change adds and how much it grows the release.

To find the dependency that brings org.example:foo into the release, run:
  ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo

If JMeter does not need foo at runtime, exclude it from that dependency, or go back to the previous version of the dependency you updated. The check then passes and the file stays as it is.

If JMeter needs foo, run this command to rewrite the file from the current release, total-size-limit included:
  ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars
Commit the file. In the pull request description, name org.example:foo (foo-1.2.jar, 1048576 bytes) and the new total of 88080384 bytes, so the reviewer can decide whether the release should grow by 1 MiB.

Do not run -PupdateExpectedJars only to make the build pass. It accepts every added module and the larger total without anyone reviewing them.
```
