### What happened?

`Quill.parse("{\"\":null}")` throws a `JsonParseException` when an object member has an empty name and a `null` value. On 3.1.4 the exception and its cause are these (the full trace is under Logs):

```text
io.quillson.JsonParseException: Internal error while reading object member at line 1, column 4 (offset 3)
Caused by: java.lang.NullPointerException: Cannot invoke "io.quillson.core.FieldName.hash()" because "name" is null
```

I expected it to return an object with one member, named `""`, with the value `null`, whose `toString()` prints `{"":null}`. 2.9.6 returns exactly that. On 3.1.4, `{"":1}` and `{"a":null}` both parse; only the combination of an empty name and `null` fails.

This is a regression in 3.0.0: 2.9.6 parses the input, and 3.0.0 and 3.1.4 throw the same exception. I could not test 3.2.0 because I couldn't download it.

We hit this in production on a supplier feed that writes `"":null` inside objects. About 40 of the roughly 180 thousand documents we receive each day fail this way, and the supplier won't change its export before Q1 2027.

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

On 2.9.6 it prints `{"":null}` and exits 0. On 3.0.0 and 3.1.4 it exits 1 with the trace under Logs; only the quillson line numbers differ on 3.0.0.

The same program with other values of `input`:

| `input` | 2.9.6 | 3.1.4 |
| --- | --- | --- |
| `{"":null}` | `{"":null}` | `JsonParseException`, cause NPE |
| `{"":1}` | `{"":1}` | `{"":1}` |
| `{"a":null}` | `{"a":null}` | `{"a":null}` |
| `[{"":null}]` | `[{"":null}]` | `JsonParseException`, cause NPE |
| `{"x":{"":null}}` | `{"x":{"":null}}` | `JsonParseException`, cause NPE |

`Quill.reader().parse(new StringReader("{\"\":null}"))` fails on 3.1.4 with the same cause.

### quillson version

3.1.4

### JDK version

Temurin 21.0.4+7. Temurin 17.0.12+7 and 23.0.1+11 fail the same way.

### Logs

```shell
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

An AI assistant drafted this report from my notes and test runs.

The closest existing issue is #1043, an NPE when a custom `FieldNamingStrategy` returns null. This reproducer uses no custom strategy, and 3.1.4 already contains the 3.0.2 fix for #1043.

**Possible cause.** This is my reading of the 3.1.4 sources, not checked in a debugger, and everything above stands without it. `ObjectReader` seems to take a shortcut for a member whose value is `null`, which reads the name again through `FieldNameCache.intern` and passes `null` there when the name is empty. The 3.2.0 changelog lists a rewrite of field-name interning (#1187), and I have not tested whether it changes this.

### Checklist

- [x] I searched existing issues, open and closed
- [ ] I reproduced this on the latest release
- [x] AI assistance was used to write this report
