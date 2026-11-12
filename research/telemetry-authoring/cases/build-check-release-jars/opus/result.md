```text
Release dependencies do not match src/dist/src/dist/expected_release_artifacts.txt.

Added module, missing from the expected list:
  org.example:foo  foo-1.2.jar  1048576 bytes (1 MiB)
Removed modules: none

The jars of the release total 88080384 bytes (84 MiB), which exceeds total-size-limit=87031808 (83 MiB)
in expected_release_artifacts.txt by 1048576 bytes. That overage equals the size of foo-1.2.jar.

The expected list and total-size-limit exist so that a reviewer sees every jar that enters or leaves the binary
release, and how much the release grows.

To see which dependency brings org.example:foo into the release, run:
  ./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency org.example:foo

Then choose one fix:
- If JMeter does not need org.example:foo at runtime, exclude it from the dependency that brings it, or revert the
  update that added it. Without foo-1.2.jar the total is 87031808 bytes, which is within total-size-limit, so both
  checks pass.
- If the release needs org.example:foo, accept the new list:
    ./gradlew :src:dist:verifyReleaseDependencies -PupdateExpectedJars
  This rewrites expected_release_artifacts.txt from the current release, including total-size-limit. Commit the
  file. Don't accept it only to make the build pass: if you haven't checked why the dependency update added
  org.example:foo, run the command above first.

If you accept the change, put these facts in the pull request description for the reviewer: org.example:foo 1.2
(foo-1.2.jar, 1048576 bytes) was added, the dependency that brings it, and the release total grew from 87031808
to 88080384 bytes (83 MiB to 84 MiB).
```
