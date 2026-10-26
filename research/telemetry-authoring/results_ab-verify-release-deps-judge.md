# Judge: verifyReleaseDependencies failure message, 24 variants

| code | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 | F10 | F11 | F12 | R1 | R2 | R3 | R4 | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | P | Y | P | Y | Y | N | Y | Y | N | N | Y | Y | Y | P | Y | Y | F1: no reason for the check; F3: "exceeds total-size-limit=87031808" without naming the file it lives in (only the header names the file); F6/F9/F10 absent; R2: no cause command, only "Check `src/dist/build/dist/release_jars.csv`" |
| B | P | Y | P | Y | Y | N | N | Y | N | N | Y | Y | Y | P | Y | Y | F1: no reason; F3: key printed, file only in the header; F6/F7/F9/F10 absent; R2: "Next: Nothing yet", accept command only |
| C | Y | Y | Y | Y | Y | P | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | F6: printed as "--dependency <group:module>", then "for example org.example:foo"; not runnable as printed |
| D | P | Y | P | Y | Y | N | N | N | N | N | Y | N | Y | N | Y | Y | F1: only "Otherwise the binary release changes without review"; F8/F12: "./gradlew :src:dist -PupdateExpectedJars" names no task; F9: no remedy; R2: reader copied "./gradlew :src:dist -PupdateExpectedJars" |
| E | P | Y | P | Y | Y | N | Y | Y | Y | N | Y | Y | Y | P | Y | Y | F1: no reason; F3: key without its file; F6/F10 absent; R2: "None run", accept command only |
| F | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| G | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| H | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| I | P | Y | P | Y | Y | N | Y | Y | N | N | Y | Y | Y | P | Y | Y | F1: no reason; F3: key without its file; F7 via absolute path "/home/user/jmeter/src/dist/build/dist/release_jars.csv"; F6/F9/F10 absent; R2: accept command only |
| J | P | Y | P | Y | Y | N | N | N | N | N | Y | N | Y | N | Y | N | F8/F12: "./gradlew :src:dist -PupdateExpectedJars" names no task; F5: overflow not printed but computable; R2: wrong accept command copied; R4: "the file is probably `src/dist/expected_release_artifacts.txt`" (wrong path) |
| K | P | Y | P | Y | Y | N | N | N | N | N | Y | N | Y | N | Y | N | F8/F12: "./gradlew :src:dist -PupdateExpectedJars"; R2: wrong accept command copied; R4: "missing from `src/dist/expected_release_artifacts.txt`" (wrong path) |
| L | P | Y | P | Y | Y | N | Y | Y | N | N | Y | Y | Y | P | Y | Y | F1: no reason; F3: key without its file; F7 via absolute csv path; F6/F9/F10 absent; R2: next step is reading the csv, not a command |
| M | P | Y | P | Y | Y | N | Y | Y | N | N | Y | Y | Y | P | Y | Y | F1: no reason; F3: key without its file; F6/F9/F10 absent; R2: accept then "./gradlew build", no cause command |
| N | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| O | P | Y | P | Y | Y | N | N | Y | N | N | Y | Y | Y | P | Y | Y | F1: no reason; F3: key without its file; F6/F7/F9/F10 absent; R2: accept command only |
| P | P | Y | P | Y | Y | N | N | N | N | N | Y | N | Y | N | Y | Y | F8/F12: "./gradlew :src:dist -PupdateExpectedJars"; R2: wrong accept command copied |
| Q | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| R | P | Y | P | Y | Y | N | N | Y | N | N | Y | Y | P | P | Y | Y | F1: no reason; F6/F7/F9/F10 absent; R1: "It compares release jars with a reviewed list", no purpose stated; R2: accept command only |
| S | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| T | Y | Y | Y | Y | Y | P | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | F6: "--dependency <module>" left unfilled although the module is known |
| U | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | P | Y | Y | Y | Y | F12: "total-size-limit=83.0 MiB (87031808 bytes)" misstates the key's value format; the file holds total-size-limit=87031808 |
| V | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| W | P | Y | P | Y | Y | N | N | Y | N | N | Y | Y | P | P | Y | N | F1: no reason; F6/F7/F9/F10 absent; R1: says what it checks, not why; R2: accept command only; R4: "Regenerating the list won't fix the size overage" is false: -PupdateExpectedJars resets total-size-limit |
| X | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |

## Best

1. G: every slot filled. It prints a runnable `dependencyInsight` per added module, lists the largest jars plus the csv, and says how `-PupdateExpectedJars` resets `total-size-limit`, so the reader worked out the new 89 MiB limit correctly.
2. V: every slot filled, with a filled-in `dependencyInsight` per module and the regeneration rule for `total-size-limit`. The reader repeated that rule correctly and invented nothing.
3. N: every slot filled in a compact layout, with sizes in bytes and MiB, a filled-in cause command, and a PR instruction. The reader produced a clean, complete reply.

## Worst

1. J: the accept command `./gradlew :src:dist -PupdateExpectedJars` names no task, and the overflow is not printed. There is no reason, cause command, or remedy, and the reader guessed a wrong expected-file path.
2. K: it has the same broken accept command and no reason, cause command, remedy, or PR guidance. The reader rewrote the expected-file path to a wrong one.
3. D: it has the same broken accept command, and its only other sentence is "Otherwise the binary release changes without review", which gives no remedy. The reader passed the broken command on to the user.

## Key

| code | run |
| --- | --- |
| A | r2/sonnet-old-1 |
| B | r2/haiku-old-1 |
| C | r2/sonnet-new-1 |
| D | r1/haiku-old-1 |
| E | r1/sonnet-old-2 |
| F | r1/haiku-new-3 |
| G | r1/sonnet-new-1 |
| H | r2/haiku-new-2 |
| I | r2/sonnet-old-3 |
| J | r1/haiku-old-3 |
| K | r2/haiku-new-3 |
| L | r1/sonnet-old-3 |
| M | r1/sonnet-old-1 |
| N | r2/sonnet-new-2 |
| O | r1/haiku-old-2 |
| P | r2/haiku-old-3 |
| Q | r2/sonnet-new-3 |
| R | r2/sonnet-old-2 |
| S | r1/sonnet-new-3 |
| T | r1/haiku-new-1 |
| U | r1/sonnet-new-2 |
| V | r2/haiku-new-1 |
| W | r2/haiku-old-2 |
| X | r1/haiku-new-2 |

## Aggregates

| round | run | code | ledger F1-F12 (of 12) | broken accept cmd | reader R1-R4 (of 4) |
| --- | --- | --- | ---: | --- | ---: |
| r1 | haiku-new-1 | T | 11.5 |  | 4 |
| r1 | haiku-new-2 | X | 12 |  | 4 |
| r1 | haiku-new-3 | F | 12 |  | 4 |
| r1 | haiku-old-1 | D | 5 | yes | 3 |
| r1 | haiku-old-2 | O | 7 |  | 3.5 |
| r1 | haiku-old-3 | J | 5 | yes | 2 |
| r1 | sonnet-new-1 | G | 12 |  | 4 |
| r1 | sonnet-new-2 | U | 11.5 |  | 4 |
| r1 | sonnet-new-3 | S | 12 |  | 4 |
| r1 | sonnet-old-1 | M | 8 |  | 3.5 |
| r1 | sonnet-old-2 | E | 9 |  | 3.5 |
| r1 | sonnet-old-3 | L | 8 |  | 3.5 |
| r2 | haiku-new-1 | V | 12 |  | 4 |
| r2 | haiku-new-2 | H | 12 |  | 4 |
| r2 | haiku-new-3 | K | 5 | yes | 2 |
| r2 | haiku-old-1 | B | 7 |  | 3.5 |
| r2 | haiku-old-2 | W | 7 |  | 2 |
| r2 | haiku-old-3 | P | 5 | yes | 3 |
| r2 | sonnet-new-1 | C | 11.5 |  | 4 |
| r2 | sonnet-new-2 | N | 12 |  | 4 |
| r2 | sonnet-new-3 | Q | 12 |  | 4 |
| r2 | sonnet-old-1 | A | 8 |  | 3.5 |
| r2 | sonnet-old-2 | R | 7 |  | 3 |
| r2 | sonnet-old-3 | I | 8 |  | 3.5 |

| round | model | arm | mean ledger /12 | runs with all 12 | broken accept cmd | mean reader /4 |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| r1 | haiku | new | 11.8 | 2/3 | 0/3 | 4.0 |
| r1 | haiku | old | 5.7 | 0/3 | 2/3 | 2.8 |
| r1 | sonnet | new | 11.8 | 2/3 | 0/3 | 4.0 |
| r1 | sonnet | old | 8.3 | 0/3 | 0/3 | 3.5 |
| r2 | haiku | new | 9.7 | 2/3 | 1/3 | 3.3 |
| r2 | haiku | old | 6.3 | 0/3 | 1/3 | 2.8 |
| r2 | sonnet | new | 11.8 | 2/3 | 0/3 | 4.0 |
| r2 | sonnet | old | 7.7 | 0/3 | 0/3 | 3.3 |
