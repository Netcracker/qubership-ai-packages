# What the session established

You spent a session on a crash in Harbordesk's invoice-import service. These are your notes; nothing here has been
written up for anyone else. All observations are from 2026-09-23.

## Starting point

The person filing pasted an incident ticket (HD-5521): the invoice-import service dead-letters about 40 of the
180,000 supplier documents it receives each day from the partner feed Veltro, with a `JsonParseException` from
quillson. The dead-lettered documents are re-keyed by hand by the billing team, which costs them about an hour a day.
Every failing document carries `"":null` somewhere in its `attributes` object; Veltro says the empty key is an
artifact of their CSV-to-JSON export and will not be changed before Q1 2027. The person filing asked for an upstream
issue in English. Target tracker: `quillson/quillson` on GitHub, the library's own repository.

## Versions and support window

- The service uses `io.quillson:quillson:3.1.4` (released 2026-08-11), the latest patch of the 3.1 line.
- quillson `README.md`, section "Supported versions": "3.2.x and 3.1.x receive fixes. 2.9.x reached end of life on
  2026-06-30."
- Release order from the project's GitHub releases page: ... 2.9.5, 2.9.6, 3.0.0, 3.0.1, 3.0.2, 3.1.0 ... 3.1.4,
  3.2.0. 2.9.6 is the last 2.9 release, and 3.0.0 came directly after it.
- 3.2.0 was released on 2026-09-22. Its `CHANGELOG.md` entry includes "Field-name interning rewritten for fewer
  allocations (#1187)". Not tested, see below.

## Reproducer

`EmptyKeyNull.java`, run with the JDK single-file source launcher:

```java
import io.quillson.Quill;
import io.quillson.JsonValue;

public class EmptyKeyNull {
    public static void main(String[] args) {
        String input = "{\"\":null}";
        JsonValue v = Quill.parse(input);
        System.out.println(v);
    }
}
```

```bash
for v in 2.9.6 3.0.0 3.1.4; do
  echo "== $v"
  java -cp ~/.m2/repository/io/quillson/quillson/$v/quillson-$v.jar EmptyKeyNull.java
done
```

On 2.9.6 it prints `{"":null}` and exits 0. On 3.0.0 and 3.1.4 it exits 1 with the same trace, apart from the
quillson line numbers on 3.0.0. The 3.1.4 output on Temurin 21.0.4+7, as printed:

```text
Exception in thread "main" io.quillson.JsonParseException: Internal error while reading object member at line 1, column 4 (offset 3)
	at io.quillson.core.DocumentReader.readDocument(DocumentReader.java:61)
	at io.quillson.Quill.parse(Quill.java:143)
	at io.quillson.Quill.parse(Quill.java:121)
	at EmptyKeyNull.main(EmptyKeyNull.java:7)
	at java.base/jdk.internal.reflect.DirectMethodHandleAccessor.invoke(DirectMethodHandleAccessor.java:103)
	at java.base/java.lang.reflect.Method.invoke(Method.java:580)
	at jdk.compiler/com.sun.tools.javac.launcher.Main.execute(Main.java:484)
	at jdk.compiler/com.sun.tools.javac.launcher.Main.run(Main.java:208)
	at jdk.compiler/com.sun.tools.javac.launcher.Main.main(Main.java:135)
Caused by: java.lang.NullPointerException: Cannot invoke "io.quillson.core.FieldName.hash()" because "name" is null
	at io.quillson.core.FieldNameCache.slotFor(FieldNameCache.java:88)
	at io.quillson.core.FieldNameCache.intern(FieldNameCache.java:61)
	at io.quillson.core.ObjectReader.readMemberName(ObjectReader.java:214)
	at io.quillson.core.ObjectReader.readMember(ObjectReader.java:171)
	at io.quillson.core.ObjectReader.readObject(ObjectReader.java:132)
	at io.quillson.core.ValueReader.readValue(ValueReader.java:97)
	at io.quillson.core.DocumentReader.readDocument(DocumentReader.java:54)
	... 8 more
```

The same program on Temurin 17.0.12+7 and 23.0.1+11 fails the same way; only the reflection frames differ
(`NativeMethodAccessorImpl` on 17).

## Which inputs fail

Same launcher, `input` changed, 3.1.4 and 2.9.6:

| Input | 2.9.6 | 3.1.4 |
| --- | --- | --- |
| `{"":null}` | `{"":null}` | `JsonParseException`, cause NPE |
| `{"":1}` | `{"":1}` | `{"":1}` |
| `{"a":null}` | `{"a":null}` | `{"a":null}` |
| `[{"":null}]` | `[{"":null}]` | `JsonParseException`, cause NPE |
| `{"x":{"":null}}` | `{"x":{"":null}}` | `JsonParseException`, cause NPE |

So it takes both an empty member name and a `null` value; either alone parses. `Quill.reader().parse(Reader)` on a
`StringReader` of `{"":null}` fails with the same cause.

## The production trace

From the service's log, 2026-09-22T07:14:09.331Z, 34 lines: the same `Caused by` block under
`com.harbordesk.billing.veltro.VeltroInvoiceConsumer.onMessage(VeltroInvoiceConsumer.java:77)`, Kafka listener frames
from `org.springframework.kafka`, and the topic name `hd.billing.veltro.invoices.v3`.

## 3.2.0 was not tested

The session can reach Maven Central only through the company's mirror, which had not synced 3.2.0:

```text
$ mvn -q dependency:get -Dartifact=io.quillson:quillson:3.2.0
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-dependency-plugin:3.8.1:get (default-cli) on project standalone-pom: Couldn't download artifact: The following artifacts could not be resolved: io.quillson:quillson:jar:3.2.0 (absent): Could not find artifact io.quillson:quillson:jar:3.2.0 in harbordesk-central (https://nexus.harbordesk.internal/repository/maven-central/)
```

## Reading of the source

Reading `ObjectReader` in the 3.1.4 sources jar, it looks as if a member whose value is `null` takes a shortcut that
re-reads the name through `FieldNameCache.intern` and passes `null` when the name is empty. You did not step through
it in a debugger; this is a reading, not a finding. You have no idea where the right fix inside the library is, or
whether the shortcut should exist at all.

## Tracker search (quillson/quillson, issues and pull requests, open and closed)

Queries: `NullPointerException FieldNameCache`, `empty key`, `"":null`, `empty field name`. One hit: #1043 (closed
2025-11-04, fixed in 3.0.2), "NPE when a custom `FieldNamingStrategy` returns null". Different trigger: it needs a
custom strategy, the reproducer here uses none, and 3.1.4 contains the fix.

## Channel

`.github/ISSUE_TEMPLATE/bug.yml`, title prefix `[bug] `, label `bug`. Fields in order:

- **What happened?** (textarea, required): "Describe what you did, what you expected, and what happened instead."
- **Reproducer** (textarea, required): "A self-contained `main` method or JUnit test and the exact input. No links to
  repositories."
- **quillson version** (input, required): "The exact version, e.g. 3.1.4. Please test the latest release first."
- **JDK version** (input, required).
- **Logs** (textarea, optional, rendered as `shell`): "The full stack trace, if any. Please do not trim it."
- **Anything else?** (textarea, optional).
- Checkboxes: "I searched existing issues, open and closed" (required); "I reproduced this on the latest release"
  (optional); "AI assistance was used to write this report" (optional).

`CONTRIBUTING.md`, section "AI-assisted contributions": "If an AI tool helped write an issue or a pull request, tick
the box in the form and say in one line, under 'Anything else?', what it did. You must understand, and be able to
answer questions about, everything you submit." The person filing has not said yet whether they will review the
draft line by line.

## The task

Draft the GitHub issue for quillson/quillson that reports this. Write the issue body as Markdown to the output file
named in your instructions, and the hand-over note to the person filing (anything that is not part of the issue
body) to the second output file. Do not open a browser, do not use the network, and do not file anything: everything
established is in these notes.
