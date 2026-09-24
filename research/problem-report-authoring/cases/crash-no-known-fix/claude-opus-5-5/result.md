### What happened?

`Quill.parse("{\"\":null}")` throws `io.quillson.JsonParseException: Internal error while reading object member at line 1, column 4 (offset 3)`, caused by `java.lang.NullPointerException: Cannot invoke "io.quillson.core.FieldName.hash()" because "name" is null`. The input is a JSON object with one member whose name is the empty string and whose value is `null`. The full trace is under Logs.

It takes both parts. On 3.1.4, with the reproducer below and only `input` changed:

| Input | 2.9.6 | 3.1.4 |
| --- | --- | --- |
| `{"":null}` | prints `{"":null}` | `JsonParseException`, cause NPE |
| `{"":1}` | prints `{"":1}` | prints `{"":1}` |
| `{"a":null}` | prints `{"a":null}` | prints `{"a":null}` |
| `[{"":null}]` | prints `[{"":null}]` | `JsonParseException`, cause NPE |
| `{"x":{"":null}}` | prints `{"x":{"":null}}` | `JsonParseException`, cause NPE |

`Quill.reader().parse(Reader)` on a `StringReader` of `{"":null}` fails with the same cause.

**Expected:** `Quill.parse("{\"\":null}")` returns a `JsonValue` whose `toString()` is `{"":null}`, and the nested forms above parse the same way. That is what 3.1.4 does for `{"":1}` and `{"a":null}`, and what 2.9.6 did for all five inputs. The exception is a `NullPointerException` that quillson itself wraps as an "Internal error", not a rejection of the input.

This is a regression between 2.9.6 (last good) and 3.0.0 (first bad); 3.0.0 fails with the same trace apart from quillson line numbers.

In our service, which receives supplier documents from a partner's JSON export, about 40 of 180000 documents a day contain `"":null` inside an object and are rejected with this exception.

### Reproducer

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

2.9.6 prints `{"":null}` and exits 0. 3.0.0 and 3.1.4 exit 1 with the trace under Logs.

### quillson version

3.1.4 (also fails on 3.0.0; last good 2.9.6). Not established on 3.2.0: I could not download it yet, so I have not run the reproducer on the latest release.

### JDK version

Temurin 21.0.4+7. Also fails the same way on Temurin 17.0.12+7 and 23.0.1+11; only the reflection frames differ.

### Logs

3.1.4 on Temurin 21.0.4+7:

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

The nearest existing issue is #1043 (NPE when a custom `FieldNamingStrategy` returns null, fixed in 3.0.2). This one needs no custom strategy, and 3.1.4 already contains that fix.

The 3.2.0 changelog lists "Field-name interning rewritten for fewer allocations (#1187)". The `Caused by` frames are in `FieldNameCache.intern`, so 3.2.0 may behave differently; I have not tested it.

A guess from reading the 3.1.4 sources, not confirmed in a debugger; the report stands without it: a member whose value is `null` seems to take a shortcut that re-reads the name through `FieldNameCache.intern` and passes `null` when the name is empty. I don't know where the right fix is, or whether the shortcut should exist.

AI assistance: an AI assistant drafted this report from my reproduction notes.

- [x] I searched existing issues, open and closed
- [ ] I reproduced this on the latest release
- [x] AI assistance was used to write this report
