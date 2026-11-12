### What happened?

I call `Quill.parse("{\"\":null}")`, a JSON object with an empty member name and a `null` value. On 2.9.6 it returns a `JsonValue` that prints as `{"":null}`. On 3.0.0 and 3.1.4 it throws `io.quillson.JsonParseException: Internal error while reading object member at line 1, column 4 (offset 3)`, caused by a `NullPointerException`. It fails the same way on JDK 17, 21, and 23.

I hit this while importing supplier invoices from a partner feed whose JSON export writes `"":null` inside an `attributes` object. The supplier has said it will not change the export before Q1 2027, so we cannot fix the input on our side. Our incident ticket reports that about 40 of the 180,000 documents we receive each day fail this way, and the billing team re-keys them by hand, which costs about an hour a day. Our service log from 2026-09-22 shows the same `Caused by` block as the one under Logs.

Both parts of the input are needed. Run with the launcher from the Reproducer section, changing only `input`:

| Input | 2.9.6 | 3.1.4 |
| --- | --- | --- |
| `{"":null}` | `{"":null}` | `JsonParseException`, cause `NullPointerException` |
| `{"":1}` | `{"":1}` | `{"":1}` |
| `{"a":null}` | `{"a":null}` | `{"a":null}` |
| `[{"":null}]` | `[{"":null}]` | `JsonParseException`, cause `NullPointerException` |
| `{"x":{"":null}}` | `{"x":{"":null}}` | `JsonParseException`, cause `NullPointerException` |

`Quill.reader().parse(Reader)` on a `StringReader` over `{"":null}` fails on 3.1.4 with the same cause.

Expected: `Quill.parse` accepts `{"":null}` as a top-level value, as an array element, and as a nested member, and returns a value that prints as `{"":null}`. `Quill.reader().parse(Reader)` does the same. This rests on three things: 2.9.6 behaves this way, with 3.0.0 the first release after it and the first that fails; 3.1.4 already parses `{"":1}` and `{"a":null}`; and RFC 8259 allows an empty string as a member name. The error itself is labeled "Internal error" and carries a `NullPointerException`, so the parser did not reject the input on purpose.

### Reproducer

`EmptyKeyNull.java`:

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

The command assumes the three jars are in the local Maven repository. On 2.9.6 it prints `{"":null}` and exits 0. On 3.0.0 and 3.1.4 it exits 1 with the trace below; the 3.0.0 trace differs only in the quillson line numbers. I ran it on 2026-09-23. Nothing but quillson and the JDK is involved.

### quillson version

3.1.4 (also fails on 3.0.0; last good is 2.9.6). Not established on 3.2.0, released 2026-09-22: my Maven mirror had not synced it when I tried on 2026-09-23, so I could not run it.

### JDK version

Temurin 21.0.4+7 (also fails on Temurin 17.0.12+7 and 23.0.1+11; on 17 the reflection frames show `NativeMethodAccessorImpl`).

### Logs

Output of the command above on 3.1.4 with Temurin 21.0.4+7:

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

The nearest existing issue is #1043 (closed, fixed in 3.0.2), "NPE when a custom `FieldNamingStrategy` returns null". It needs a custom strategy, this reproducer uses none, and 3.1.4 contains that fix.

A reading of the 3.1.4 sources, which is a guess: I did not step through it in a debugger, and this report stands without it. In `ObjectReader`, a member whose value is `null` appears to take a shortcut that re-reads the name through `FieldNameCache.intern`, which then receives `null` when the name is empty. I do not know where the right fix is, or whether the shortcut should exist.

AI assistance: an AI assistant ran the reproducer on the three releases and drafted this report.

- [x] I searched existing issues, open and closed
- [ ] I reproduced this on the latest release
- [x] AI assistance was used to write this report
