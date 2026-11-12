Title: `[bug] Quill.parse throws "Internal error while reading object member" on {"":null} since 3.0.0`

Label: `bug`

### What happened?

`Quill.parse("{\"\":null}")` throws `JsonParseException` on quillson 3.0.0 and 3.1.4. The message is `Internal error while reading object member at line 1, column 4 (offset 3)`, and the cause is a `NullPointerException` (full trace under Logs). On 2.9.6 the same call returns the object and prints `{"":null}`.

I expected `Quill.parse("{\"\":null}")` to return an object with one member whose name is the empty string and whose value is JSON `null`, printed as `{"":null}`, as on 2.9.6.

The failure needs both the empty name and the `null` value. Each input below was parsed with the reproducer, changing only `input`:

| Input | 2.9.6 | 3.1.4 |
| --- | --- | --- |
| `{"":null}` | `{"":null}` | `JsonParseException`, cause NPE |
| `{"":1}` | `{"":1}` | `{"":1}` |
| `{"a":null}` | `{"a":null}` | `{"a":null}` |
| `[{"":null}]` | `[{"":null}]` | `JsonParseException`, cause NPE |
| `{"x":{"":null}}` | `{"x":{"":null}}` | `JsonParseException`, cause NPE |

`Quill.reader().parse(Reader)` on a `StringReader` of `{"":null}` fails with the same cause.

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

Run with the JDK single-file source launcher against each version:

```bash
for v in 2.9.6 3.0.0 3.1.4; do
  echo "== $v"
  java -cp ~/.m2/repository/io/quillson/quillson/$v/quillson-$v.jar EmptyKeyNull.java
done
```

2.9.6 prints `{"":null}` and exits 0. 3.0.0 and 3.1.4 exit 1 with the trace under Logs; on 3.0.0 only the quillson line numbers differ.

### quillson version

3.1.4. Also fails on 3.0.0; last good is 2.9.6, the release before 3.0.0. Not tested on 3.2.0, which was not available to me.

### JDK version

Temurin 21.0.4+7. Temurin 17.0.12+7 and 23.0.1+11 fail the same way; only the reflection frames differ.

### Logs

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

(Output of the reproducer on 3.1.4 and Temurin 21.0.4+7.)

### Anything else?

In production, about 40 of the 180000 documents we receive each day from a partner's feed fail with this cause. Each one has `"":null` inside an object, which the partner's CSV-to-JSON export produces and which they will not change before Q1 2027.

The nearest existing issue is #1043, "NPE when a custom `FieldNamingStrategy` returns null", fixed in 3.0.2. This one uses no custom naming strategy and reproduces on 3.1.4, which contains that fix.

**Reading of the source (a guess, not checked in a debugger; the report above stands without it).** In the 3.1.4 sources, `ObjectReader` appears to take a shortcut for a member whose value is `null`, reading the name again through `FieldNameCache.intern` and passing `null` when the name is empty.

AI assistance: an AI assistant ran the reproducer and the input variations above and drafted this report.

- [x] I searched existing issues, open and closed
- [ ] I reproduced this on the latest release
- [x] AI assistance was used to write this report
