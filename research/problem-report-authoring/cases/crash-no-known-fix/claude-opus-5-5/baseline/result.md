**Title:** `[bug] Quill.parse fails with "Internal error" on {"":null} since 3.0.0`

**Label:** `bug`

### What happened?

I parsed `{"":null}` with `Quill.parse(String)` on quillson 3.1.4. It threw `io.quillson.JsonParseException: Internal error while reading object member at line 1, column 4 (offset 3)`, caused by `java.lang.NullPointerException: Cannot invoke "io.quillson.core.FieldName.hash()" because "name" is null`. The full trace is under Logs.

I expected `Quill.parse("{\"\":null}")` to return a value that prints `{"":null}`. 2.9.6 does that with the same program. 3.1.4 also parses `{"":1}`, so it accepts an empty member name, and the exception calls the failure an internal error rather than a syntax error.

The failure needs an empty member name and a `null` value together. Either one alone parses (table under Reproducer). The member fails inside an array and inside a nested object too. `Quill.reader().parse(Reader)` on a `StringReader` of `{"":null}` fails with the same cause.

Last good: 2.9.6. First bad: 3.0.0, the release after 2.9.6. 3.0.0 throws the same trace with different quillson line numbers.

In our service this rejects about 40 of the 180000 documents a day we receive from a partner. Their export writes `"":null` into the documents, and they will not change it before Q1 2027.

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

On 2.9.6 it prints `{"":null}` and exits 0. On 3.0.0 and 3.1.4 it exits 1 with the trace under Logs.

Other values of `input`, same program:

| Input | 2.9.6 | 3.1.4 |
| --- | --- | --- |
| `{"":null}` | `{"":null}` | `JsonParseException`, cause NPE |
| `{"":1}` | `{"":1}` | `{"":1}` |
| `{"a":null}` | `{"a":null}` | `{"a":null}` |
| `[{"":null}]` | `[{"":null}]` | `JsonParseException`, cause NPE |
| `{"x":{"":null}}` | `{"x":{"":null}}` | `JsonParseException`, cause NPE |

### quillson version

3.1.4. Also fails on 3.0.0; 2.9.6 works. Not tested on 3.2.0: the Maven mirror I can reach had not synced it.

### JDK version

Temurin 21.0.4+7. Temurin 17.0.12+7 and 23.0.1+11 fail the same way; only the reflection frames differ.

### Logs

3.1.4 on Temurin 21.0.4+7, as printed:

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

Nearest existing issue: #1043, "NPE when a custom `FieldNamingStrategy` returns null", fixed in 3.0.2. This one needs no custom strategy, and 3.1.4 already contains that fix.

**Possible cause (a guess from reading the 3.1.4 sources; everything above stands without it).** In `ObjectReader`, a member whose value is `null` seems to take a shortcut that reads the name again through `FieldNameCache.intern`, and to pass `null` there when the name is empty. I did not step through it in a debugger. The 3.2.0 changelog lists "Field-name interning rewritten for fewer allocations (#1187)", which touches the same code, so 3.2.0 may behave differently.

AI assistance: an AI agent (Claude) ran the reproducer on the versions above and drafted this report.

- [x] I searched existing issues, open and closed
- [ ] I reproduced this on the latest release
- [x] AI assistance was used to write this report
