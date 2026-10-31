### What happened?

I parse an object whose member has an empty name and a `null` value, and `Quill.parse` throws `JsonParseException` with a `NullPointerException` as the cause. This happens on 3.0.0 and 3.1.4. 2.9.6 parses the same input. Excerpt of the 3.1.4 trace (the full trace is under Logs):

```java
Quill.parse("{\"\":null}");
```

```text
Exception in thread "main" io.quillson.JsonParseException: Internal error while reading object member at line 1, column 4 (offset 3)
...
Caused by: java.lang.NullPointerException: Cannot invoke "io.quillson.core.FieldName.hash()" because "name" is null
```

**Expected:** `Quill.parse("{\"\":null}")` returns an object with one member, whose name is the empty string and whose value is `null`. Printing it gives `{"":null}`, as it does on 2.9.6. The exception reports an internal error, not malformed input, and 3.1.4 accepts each condition on its own:

| Input | 2.9.6 | 3.1.4 |
| --- | --- | --- |
| `{"":null}` | `{"":null}` | `JsonParseException`, cause NPE |
| `{"":1}` | `{"":1}` | `{"":1}` |
| `{"a":null}` | `{"a":null}` | `{"a":null}` |
| `[{"":null}]` | `[{"":null}]` | `JsonParseException`, cause NPE |
| `{"x":{"":null}}` | `{"x":{"":null}}` | `JsonParseException`, cause NPE |

`Quill.reader().parse(Reader)` over a `StringReader` of `{"":null}` fails with the same cause.

We hit this in production. A partner feed's export writes `"":null` into some objects, and about 40 of the 180000 documents it sends us each day fail to parse.

### Reproducer

`EmptyKeyNull.java`, run with the JDK single-file source launcher against each jar from Maven Central:

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

On 2.9.6 it prints `{"":null}` and exits with status 0. On 3.0.0 and 3.1.4 it exits with status 1 and prints the trace under Logs. The 3.0.0 trace differs only in the quillson line numbers.

### quillson version

3.1.4. Last good: 2.9.6. First bad: 3.0.0, the release that followed 2.9.6. Not tested on 3.2.0, because I could not download it in my environment.

### JDK version

Temurin 21.0.4+7. Temurin 17.0.12+7 and 23.0.1+11 fail the same way, apart from the reflection frames.

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

The nearest existing issue is #1043, "NPE when a custom `FieldNamingStrategy` returns null", fixed in 3.0.2. This report uses no custom strategy and reproduces on 3.1.4, which contains that fix.

My reading of the 3.1.4 sources, which I have not checked in a debugger and which the sections above do not rely on: in `ObjectReader`, a member whose value is `null` seems to take a shortcut that reads the name again through `FieldNameCache.intern`, and that call receives `null` when the name is empty. I don't know whether the fix belongs there or whether the shortcut should exist at all.

AI assistance: an AI agent ran the reproducer and the input variations above and drafted this report.

- [x] I searched existing issues, open and closed
- [ ] I reproduced this on the latest release
- [x] AI assistance was used to write this report
