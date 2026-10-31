## What happened?

`Quill.parse("{\"\":null}")` throws `JsonParseException: Internal error while reading object member at line 1, column 4 (offset 3)`, caused by a `NullPointerException`. The same call on 2.9.6 returns a `JsonValue` that prints `{"":null}`. 3.0.0 is the first release that fails, and 3.1.4 fails too.

Our invoice-import service parses supplier documents from a partner feed. About 40 of the 180,000 documents it receives each day contain `"":null` in an `attributes` object, fail with this exception, and are re-keyed by hand, which costs about an hour a day (from our incident ticket). The partner says the empty key comes from their CSV-to-JSON export and will not change before Q1 2027.

**Expected:** `Quill.parse` returns without an exception for these inputs, and the result prints as the input does, as on 2.9.6:

- `{"":null}` prints `{"":null}`
- `[{"":null}]` prints `[{"":null}]`
- `{"x":{"":null}}` prints `{"x":{"":null}}`

`Quill.reader().parse(Reader)` on a `StringReader` of `{"":null}` fails with the same cause, and should return the same value.

This rests on the 2.9.6 behavior and on 3.1.4 itself. 3.1.4 parses both `{"":1}` and `{"a":null}`, and it reports the failure as an internal error, not as a rejection of the input. 2.9.x is end of life, so I cannot cite a supported release. I have not checked whether 3.0.0 changed this on purpose.

Both parts are needed to fail. Results of the same program with only `input` changed:

| Input | 2.9.6 | 3.1.4 |
| --- | --- | --- |
| `{"":null}` | `{"":null}` | `JsonParseException`, cause NPE |
| `{"":1}` | `{"":1}` | `{"":1}` |
| `{"a":null}` | `{"a":null}` | `{"a":null}` |
| `[{"":null}]` | `[{"":null}]` | `JsonParseException`, cause NPE |
| `{"x":{"":null}}` | `{"x":{"":null}}` | `JsonParseException`, cause NPE |

## Reproducer

`EmptyKeyNull.java`, which needs only the JDK and the quillson jar. Run on 2026-09-23.

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

On 2.9.6 the program prints `{"":null}` and exits 0. On 3.0.0 and 3.1.4 it exits 1 with the trace under "Logs". The 3.0.0 trace differs only in the quillson line numbers. The same program fails the same way on Temurin 17.0.12+7 and 23.0.1+11; only the reflection frames differ (`NativeMethodAccessorImpl` on 17).

## quillson version

3.1.4 (`io.quillson:quillson:3.1.4`, released 2026-08-11), the latest 3.1 patch. Last good: 2.9.6. First bad: 3.0.0.

Not established: 3.2.0 (released 2026-09-22). I could not test it, because our Maven mirror had not synced it. Its changelog lists "Field-name interning rewritten for fewer allocations (#1187)", and I do not know whether that affects this.

## JDK version

Temurin 21.0.4+7 (trace below). Also fails on Temurin 17.0.12+7 and 23.0.1+11.

## Logs

Output of the reproducer on 3.1.4, Temurin 21.0.4+7:

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

## Anything else?

Nearest existing issue: #1043 (closed, fixed in 3.0.2), "NPE when a custom `FieldNamingStrategy` returns null". It needs a custom strategy, the reproducer here uses none, and 3.1.4 contains that fix.

Unconfirmed reading of the 3.1.4 sources, not checked in a debugger: `ObjectReader` seems to handle a member whose value is `null` by looking the name up again through `FieldNameCache.intern`, which receives `null` when the name is empty. The report stands without this.

AI assistance: an AI coding assistant ran the reproducer, searched the tracker, and drafted this report.

- [x] I searched existing issues, open and closed
- [ ] I reproduced this on the latest release
- [x] AI assistance was used to write this report
