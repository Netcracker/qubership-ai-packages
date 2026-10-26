# Prompts of the verifyReleaseDependencies trial

## Writer prompt

Given to every writer run, from `src/dist/` of the fixture.

```markdown
`./gradlew :src:dist:verifyReleaseDependencies` fails with the bare message `Release dependencies do not match` whenever the jars of the binary release no longer match `src/dist/src/dist/expected_release_artifacts.txt`: a module was added or removed, or the total size of the jars exceeds `total-size-limit`. Replace that message in `src/dist/build.gradle.kts` with a proper failure message.

Do not run Gradle: this environment has no network access, so the build cannot resolve dependencies. Do not commit. When you are done, reply with a short summary of the change.
```

## Project instructions

Appended to the system prompt with `--append-system-prompt-file`; user-level `CLAUDE.md` files were disabled with `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1`.

### Arm `old`

```markdown
Contents of CLAUDE.md (project instructions, checked into the codebase):

Security model: [SECURITY.md](./SECURITY.md)

## Building and testing

JMeter builds with Gradle. Use `./gradlew --quiet ...` to reduce output verbosity.

After modifying Java code, before reporting the change as done (handing
control back to the user), run `./gradlew --quiet classes style` and fix any
reported issues.

JMeter uses Gradle toolchains; JDKs are found locally or auto-provisioned. The
code targets JDK 17. To test under a specific JDK pass build parameters:

- `-PjdkTestVersion=<n>` — JDK to run **tests** with; `0` means "use the current Java"
- `-PjdkTestVendor=<vendor>` / `-PjdkTestImplementation=<impl>` — pin the vendor / VM implementation (jdkTestVersion is enough for most cases)

List every available build parameter with `./gradlew parameters`.

## Skill trigger: `telemetry-authoring`

Load `telemetry-authoring` before writing or changing a call to a logger, a metric, or a span, and before deciding what
a new failure, retry, fallback, clamped value, or waited-on state should emit. A coding task reaches this point the
moment the branch is written, not when the pull request is due: load it then, and read its `references/` file for the
repository's ecosystem before the first call (JVM, Go, and Python have one; for any other ecosystem the skill says what
to do without one). Also load it to review instrumentation in a diff, including instrumentation that is conspicuously
absent. Wording, tense, sentence length, and dialect of the message belong to the developer-style skill of the language
it is written in (`english-developer-style` for English); load that too.
```

### Arm `new`

```markdown
Contents of CLAUDE.md (project instructions, checked into the codebase):

Security model: [SECURITY.md](./SECURITY.md)

## Building and testing

JMeter builds with Gradle. Use `./gradlew --quiet ...` to reduce output verbosity.

After modifying Java code, before reporting the change as done (handing
control back to the user), run `./gradlew --quiet classes style` and fix any
reported issues.

JMeter uses Gradle toolchains; JDKs are found locally or auto-provisioned. The
code targets JDK 17. To test under a specific JDK pass build parameters:

- `-PjdkTestVersion=<n>` — JDK to run **tests** with; `0` means "use the current Java"
- `-PjdkTestVendor=<vendor>` / `-PjdkTestImplementation=<impl>` — pin the vendor / VM implementation (jdkTestVersion is enough for most cases)

List every available build parameter with `./gradlew parameters`.

## Skill trigger: `telemetry-authoring`

Load `telemetry-authoring` before writing or changing a call to a logger, a metric, or a span, and before deciding what
a new failure, retry, fallback, clamped value, or waited-on state should emit. A coding task reaches this point the
moment the branch is written, not when the pull request is due: load it then, and read its `references/` file for the
repository's ecosystem before the first call (JVM, Go, and Python have one; for any other ecosystem the skill says what
to do without one). Also load it to review instrumentation in a diff, including instrumentation that is conspicuously
absent. That includes the failure message of a build script, a CLI command, or a CI check (a Gradle or Maven task that
verifies something, a lint, a pre-commit hook): its reader holds only the tool's output, and the skill's tool mode
covers it. Wording, tense, sentence length, and dialect of the message belong to the developer-style skill of the language
it is written in (`english-developer-style` for English); load that too.
```

## Writer command

```bash
#!/bin/zsh
# Usage: run.sh <run-name>, e.g. run.sh haiku-new-1. Runs one headless writer in runs/<run-name>.
set -u
EXP=${0:A:h}
name=$1
model=${name%%-*}
arm=${${name#*-}%%-*}
mkdir -p $EXP/logs $EXP/out
cd $EXP/runs/$name || exit 1
CLAUDE_CODE_DISABLE_CLAUDE_MDS=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 claude -p "$(cat $EXP/prompt.md)" \
  --append-system-prompt-file $EXP/arms/$arm/system.md \
  --model $model \
  --setting-sources project \
  --strict-mcp-config \
  --output-format stream-json --verbose \
  --allowedTools Read Grep Glob Edit Write Skill 'Bash(git diff:*)' 'Bash(git status:*)' 'Bash(grep:*)' 'Bash(ls:*)' 'Bash(cat:*)' 'Bash(sed:*)' \
  > $EXP/logs/$name.jsonl 2> $EXP/logs/$name.err
diff -u --label a/src/dist/build.gradle.kts --label b/src/dist/build.gradle.kts $EXP/base/src/dist/build.gradle.kts src/dist/build.gradle.kts > $EXP/out/$name.diff
echo "$name exit=$?"
```

## Fact ledger

```markdown
# Fact ledger for the verifyReleaseDependencies failure message

Built from the task statement (what an agent holding only the build output needs), not from the skill text.

Scenario rendered for every variant: the module `org.example:foo` (`foo-1.2.jar`, 1048576 bytes) entered the release,
no module left it, and the total size of the jars is 88080384 bytes against `total-size-limit=87031808`. Project path
`:src:dist`, task path `:src:dist:verifyReleaseDependencies`, expected file
`src/dist/src/dist/expected_release_artifacts.txt`, actual list `src/dist/build/dist/release_jars.csv`.

| Id | The rendered output lets the reader... |
| --- | --- |
| F1 | name the check that failed and say in one sentence why the check exists |
| F2 | find the file to edit: the path of the expected file |
| F3 | find where the size limit lives: the key `total-size-limit` together with the file it is in |
| F4 | name each added module (and would name each removed one) |
| F5 | quote the size numbers: the total, the limit, and the overflow or enough to compute it |
| F6 | run a command that shows which dependency brought the added module in, with the module filled in |
| F7 | find which jars caused the growth: a printed list of the largest jars, a file to compare, or a command |
| F8 | accept the change with a command that runs as printed (`-PupdateExpectedJars` on the right task) |
| F9 | know what to do when the change is not intended |
| F10 | know what to put in the pull request description or tell the user |
| F11 | tell the branches apart: added, removed, and over-limit each get their own text |
| F12 | trust every path, key, and command in the output: none is invented or wrong (a "no" here is a defect) |
```

## Render prompt

```markdown
# Render failure messages

Each file `blind/<CODE>.diff` under `{EXP}` is a change to `src/dist/build.gradle.kts`; the unchanged file is
`{EXP}/base/src/dist/build.gradle.kts`. Every change replaces the bare `throw GradleException("Release dependencies do
not match")` in the task `verifyReleaseDependencies` with code that builds a failure message. Render, for each code you
are given, the exact text a user sees when the task fails in the scenario below, and write it to `{EXP}/blind/<CODE>.txt`
with the Write tool. Do not judge or improve the message; a rendering mistake is worse than an ugly message.

Scenario:

- Gradle task path `$path` = `:src:dist:verifyReleaseDependencies`; `project.path` / `projectPath` = `:src:dist`.
- `expectedFile.relativeTo(rootDir)` = `src/dist/src/dist/expected_release_artifacts.txt`; the actual list
  (`actualJars`, `layout.buildDirectory.file("dist/release_jars.csv")`) relative to the root is
  `src/dist/build/dist/release_jars.csv`. Absolute paths, where the code prints one, start with `/home/user/jmeter/`.
- `added` = `[org.example:foo]`; its jar is `foo-1.2.jar`, 1048576 bytes. `removed` is empty.
- `totalSize` = 88080384; `sizeLimit` = 87031808; `releaseJarsSizeHeadroom` = 5242880.
- The ten largest artifacts, largest first, as `size name`: `12582912 bcprov-jdk18on-1.78.jar`, `9437184 groovy-4.0.21.jar`,
  `5242880 jmeter-core.jar`, `4194304 xstream-1.4.20.jar`, `3145728 rhino-1.7.14.jar`, `2097152 httpclient-4.5.14.jar`,
  `2097152 caffeine-3.1.8.jar`, `1572864 jackson-databind-2.17.0.jar`, `1048576 foo-1.2.jar`, `1048576 xalan-2.7.3.jar`.
  Where the code iterates over another collection, derive it from these facts; where it needs a value this list does
  not define, write `<undefined: what>` in its place.
- Gradle prints a thrown `GradleException` as `Execution failed for task ':src:dist:verifyReleaseDependencies'.` followed
  by `> ` and the message. Render only the message itself, and before it anything the code prints with `println` or a
  logger on the failing path, marked `[printed earlier at <level>]`.

Write each file as plain text: the message exactly as the code builds it, newlines and indentation included. If the
code does not compile or cannot reach the failure in this scenario, write that in one line instead. When done, reply
with one line per code: the code and `ok` or the problem.
```

## Reader prompt and command

```markdown
You ran `./gradlew build` in the user's Apache JMeter checkout to verify their change, a dependency update. The build failed with the output below. You cannot open the build scripts or any other file, and you cannot run anything; work from this output alone.

Reply to the user in at most 150 words:

1. What failed, and why that check exists.
2. What exactly changed.
3. The commands you would run next, if any, copied or completed from the output.
4. What the user should do if the change is intended, and what if it is not.
5. What, if anything, belongs in their pull request description.

Where the output does not tell you something, say so instead of guessing.

```text
{OUTPUT}
```
```

```bash
#!/bin/zsh
# Usage: reader.sh <code>. Hands blind/<code>.txt to a fresh haiku with no repository and no instructions.
set -u
EXP=${0:A:h}
code=$1
dir=$EXP/reader-cwd/$code
mkdir -p $dir $EXP/reader
prompt=$(python3 -c 'import sys; t=open(sys.argv[1]).read(); print(t.replace("{OUTPUT}", open(sys.argv[2]).read().rstrip()))' $EXP/reader_prompt.md $EXP/blind/$code.txt)
cd $dir
CLAUDE_CODE_DISABLE_CLAUDE_MDS=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 claude -p "$prompt" \
  --model haiku \
  --setting-sources project \
  --strict-mcp-config \
  --disable-slash-commands \
  --tools '' \
  > $EXP/reader/$code.md 2> $EXP/reader/$code.err
echo "$code exit=$?"
```

## Judge prompt

```markdown
# Judge failure messages and the replies of agents that read them

You judge {N} variants of one failure message, named by code only. For each code `X` under `{EXP}/blind/`:

- `X.diff` is the code that builds the message, a change to `{EXP}/base/src/dist/build.gradle.kts`;
- `X.txt` is the message rendered for one scenario, described at the top of `{EXP}/ledger.md`;
- `{EXP}/reader/X.md` is the reply of a fresh agent that saw only `X.txt` as the output of a failed build and was asked
  to explain it to the user (its prompt is `{EXP}/reader_prompt.md`).

Read `{EXP}/ledger.md` and the unchanged build file first. Facts you can check there: the task path, the property
`updateExpectedJars` (passed as `-PupdateExpectedJars`), the key `total-size-limit=` in the expected file, and the
expected file's location. `./gradlew :src:dist:dependencyInsight --configuration runtimeClasspath --dependency <module>`
is a valid Gradle command for this project.

Score every code on every ledger row F1 to F12 as `Y`, `P` (partial), or `N`, judging the rendered text and, for F11,
the code's other branches as well. F12 is `Y` when nothing in the message is invented or wrong.

Then score the reader's reply:

- R1: it explains correctly what failed and why the check exists (`Y`/`P`/`N`);
- R2: it gives the user at least one correct, runnable next command for the cause, and the correct accept command
  (`Y`/`P`/`N`);
- R3: it says what to do when the change is not intended, and what to put in the pull request (`Y`/`P`/`N`);
- R4: it invents nothing: no file, key, command, or cause absent from the output and false (`Y` when clean, `N` with
  the invention quoted).

Write `{EXP}/judge.md` with the Write tool: one Markdown table, a row per code, columns `code`, F1 to F12, R1 to R4, and
a short note quoting the decisive text for any `P` or `N`. Under the table, list the three best and the three worst
codes with one sentence each. Do not try to guess which model or version wrote a variant. Do not edit any other file.
Reply with the table only.
```
