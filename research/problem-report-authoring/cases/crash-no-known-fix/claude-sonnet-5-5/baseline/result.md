### What happened?

Calling `Quill.parse("{\"\":null}")`, an object with one member whose name is empty and whose value is `null`, throws on 3.1.4: `io.quillson.JsonParseException: Internal error while reading object member at line 1, column 4 (offset 3)`, caused by `java.lang.NullPointerException: Cannot invoke "io.quillson.core.FieldName.hash()" because "name" is null`. The full trace is under Logs.

I expected `parse` to return the document, so that the reproducer prints `{"":null}` and exits with status 0. That is what 2.9.6 does, and what 3.1.4 does for `{"":1}` and `{"a":null}`. The expectation rests on that earlier behavior and on the exception itself, which calls the failure an "Internal error". Not established: whether 3.0.0 changed the handling of empty member names on purpose, because I have not read its release notes.

Results for the same program with `input` changed, run on the same JDK (Temurin 21.0.4+7):

| Input | 2.9.6 | 3.1.4 |
| --- | --- | --- |
| `{"":null}` | `{"":null}` | `JsonParseException`, cause NPE |
| `{"":1}` | `{"":1}` | `{"":1}` |
| `{"a":null}` | `{"a":null}` | `{"a":null}` |
| `[{"":null}]` | `[{"":null}]` | `JsonParseException`, cause NPE |
| `{"x":{"":null}}` | `{"x":{"":null}}` | `JsonParseException`, cause NPE |

An empty name and a `null` value are both needed; either alone parses. `Quill.reader().parse(Reader)` on a `StringReader` of `{"":null}` fails with the same cause.

This is a regression. 2.9.6 is the last good release and 3.0.0, the next one, is the first bad: it fails with the same trace apart from the quillson line numbers. 2.9.x reached end of life on 2026-06-30, so I use it only as the reference behavior. 3.1.4 is inside the supported range.

We hit this in a service that imports supplier invoices as JSON from a partner feed. About 40 of the roughly 180,000 documents received per day carry `"":null` in an `attributes` object and fail this way (counts from our incident records). Each one is dead-lettered and re-keyed by hand, which costs about an hour a day. The empty key comes from the partner's CSV-to-JSON export, which we do not control.

Not tested: 3.2.0, released 2026-09-22. My Maven mirror had not synced it. Its changelog lists "Field-name interning rewritten for fewer allocations (#1187)", and the trace below passes through `FieldNameCache.intern`, so 3.2.0 may behave differently.

### Reproducer

`EmptyKeyNull.java`, run with the JDK single-file source launcher. The jar path assumes a local Maven repository.

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

2.9.6 prints `{"":null}` and exits 0. 3.0.0 and 3.1.4 exit 1.

### quillson version

3.1.4 (also fails on 3.0.0; 2.9.6 parses the input; 3.2.0 not tested, see above)

### JDK version

Temurin 21.0.4+7. Also fails the same way on Temurin 17.0.12+7 and 23.0.1+11; only the reflection frames differ.

### Logs

Output of the 3.1.4 run on Temurin 21.0.4+7:

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

### Anything else?

The nearest existing issue is #1043 (closed, fixed in 3.0.2), "NPE when a custom `FieldNamingStrategy` returns null". It needs a custom strategy, the reproducer here uses none, and 3.1.4 already contains that fix.

A guess, not a finding: from reading `ObjectReader` in the 3.1.4 sources jar, a member whose value is `null` seems to take a path that looks the name up again through `FieldNameCache.intern` and passes `null` when the name is empty. I did not step through it in a debugger, and the report does not depend on it.

AI assistance: an AI assistant ran the reproducer on the versions above and wrote this report from those runs and our incident records.

- [x] I searched existing issues, open and closed
- [ ] I reproduced this on the latest release (3.2.0 not tested, see above)
- [x] AI assistance was used to write this report
