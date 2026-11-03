### What happened?

`Quill.parse("{\"\":null}")` throws `JsonParseException: Internal error while reading object member at line 1, column 4 (offset 3)`, caused by a `NullPointerException`. The same input parses on 2.9.6 and fails on 3.0.0 and 3.1.4. An empty member name alone or a `null` value alone parses on 3.1.4, so the failure needs both. I ran each input below with the reproducer's launcher on 2.9.6 and 3.1.4:

| Input | 2.9.6 | 3.1.4 |
| --- | --- | --- |
| `{"":null}` | `{"":null}` | `JsonParseException`, cause `NullPointerException` |
| `{"":1}` | `{"":1}` | `{"":1}` |
| `{"a":null}` | `{"a":null}` | `{"a":null}` |
| `[{"":null}]` | `[{"":null}]` | `JsonParseException`, cause `NullPointerException` |
| `{"x":{"":null}}` | `{"x":{"":null}}` | `JsonParseException`, cause `NullPointerException` |

`Quill.reader().parse(Reader)` on a `StringReader` of `{"":null}` fails on 3.1.4 with the same cause.

**Expected:** each failing row above parses on 3.1.4 and prints the same text as on 2.9.6, for example `{"":null}` for the first row, with no exception. This rests on the 2.9.6 behavior and on 3.1.4 itself: it parses `{"":1}` and `{"a":null}`, and it reports the failure as an internal error. I did not check whether the 3.0.0 release notes mention a change.

**Impact:** in our production invoice-import service, a supplier feed exports `"":null` inside some documents. The supplier says the empty key is an artifact of its CSV-to-JSON export and will not change before Q1 2027. About 40 of the 180000 documents we receive each day fail with this exception on 3.1.4. Our billing team re-keys them by hand, which takes about an hour a day. This comes from our incident ticket, not from the reproducer; the production stack trace has the same `Caused by` block as the one under Logs.

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

2.9.6 prints `{"":null}` and exits 0. 3.0.0 and 3.1.4 exit 1 with the trace under Logs; on 3.0.0 only the quillson line numbers differ.

### quillson version

3.1.4 (the latest 3.1 patch, which the README lists as supported). Last good: 2.9.6. First bad: 3.0.0, the release after 2.9.6.

Not established: 3.2.0, released 2026-09-22. The Maven mirror I can reach had not synced it. Its `CHANGELOG.md` lists "Field-name interning rewritten for fewer allocations (#1187)", so I can't say whether 3.2.0 is affected.

### JDK version

Temurin 21.0.4+7. Temurin 17.0.12+7 and 23.0.1+11 fail the same way; only the reflection frames differ.

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

The nearest existing issue is #1043 (closed, fixed in 3.0.2), "NPE when a custom `FieldNamingStrategy` returns null". It needs a custom strategy, the reproducer here uses none, and 3.1.4 contains that fix.

Reading of the source, which may be wrong: in the 3.1.4 sources jar, a member whose value is `null` seems to take a path that reads the name through `FieldNameCache.intern` and passes `null` when the name is empty. I did not step through it in a debugger. The report above stands without this paragraph.

AI assistance: Claude ran the reproducer and drafted this report from our incident ticket and session notes.

- [x] I searched existing issues, open and closed
- [ ] I reproduced this on the latest release
- [x] AI assistance was used to write this report
