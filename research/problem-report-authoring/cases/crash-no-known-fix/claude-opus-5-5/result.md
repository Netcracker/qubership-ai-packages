### What happened?

I call `Quill.parse` on a JSON object that has a member with an empty name and a `null` value, `{"":null}`, and it throws `JsonParseException: Internal error while reading object member at line 1, column 4 (offset 3)`, caused by a `NullPointerException`. The full trace is under Logs.

What I expected: `Quill.parse("{\"\":null}")` returns a value whose `toString()` is `{"":null}`, the same way the same call already returns `{"":1}` for `{"":1}` and `{"a":null}` for `{"a":null}` on 3.1.4. The document is valid JSON (RFC 8259 §4: an object member's name is a string, and the empty string is a string), and the exception calls itself an internal error with an NPE as its cause rather than rejecting the input as malformed, so I read it as a crash and not as an intended rejection.

What happens instead: the call fails whenever both conditions hold, an empty member name and a `null` value, at any depth. Either one alone parses. Results on 3.1.4, with 2.9.6 for comparison, from the reproducer below with only `input` changed:

| Input | 2.9.6 | 3.1.4 |
| --- | --- | --- |
| `{"":null}` | `{"":null}` | `JsonParseException`, cause NPE |
| `{"":1}` | `{"":1}` | `{"":1}` |
| `{"a":null}` | `{"a":null}` | `{"a":null}` |
| `[{"":null}]` | `[{"":null}]` | `JsonParseException`, cause NPE |
| `{"x":{"":null}}` | `{"x":{"":null}}` | `JsonParseException`, cause NPE |

The streaming entry point fails the same way: `Quill.reader().parse(Reader)` on a `StringReader` over `{"":null}` throws with the same cause.

This is a regression between 2.9.6 and 3.0.0: 2.9.6 (the last 2.9 release) prints `{"":null}` and exits 0; 3.0.0 (the next release) and 3.1.4 throw. 3.0.0 prints the same trace apart from quillson line numbers.

Where we hit it: a service that parses supplier invoices from a partner's feed rejects about 40 of the 180,000 documents it receives a day, and every rejected document has `"":null` somewhere inside an object. The partner says the empty key comes from their CSV-to-JSON export and will not change before Q1 2027, so these documents are re-keyed by hand. I have no workaround inside quillson.

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

On 2.9.6 this prints `{"":null}` and exits 0. On 3.0.0 and 3.1.4 it exits 1 with the trace under Logs.

### quillson version

3.1.4. Also fails on 3.0.0; works on 2.9.6. Not established on 3.2.0: I could not download it yet, so I have not run the reproducer against it.

### JDK version

Eclipse Temurin 21.0.4+7. Same failure on Temurin 17.0.12+7 and 23.0.1+11; only the reflection frames of the launcher differ.

### Logs

The reproducer on 3.1.4 and Temurin 21.0.4+7, untrimmed:

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

Our production log shows the same `Caused by` block under our own message-consumer frames; it is not pasted here, and our service and partner names are left out of this report.

### Anything else?

Related, but a different trigger: #1043 (NPE when a custom `FieldNamingStrategy` returns null, fixed in 3.0.2). The reproducer here uses no custom strategy, and 3.1.4 already contains that fix. I searched issues and pull requests, open and closed, for `NullPointerException FieldNameCache`, `empty key`, `"":null`, and `empty field name`; #1043 was the only hit.

The 3.2.0 changelog mentions "Field-name interning rewritten for fewer allocations (#1187)". I have not checked whether that changes this.

Reading of the source (a guess, not verified in a debugger; everything above stands without it): in the 3.1.4 sources, `ObjectReader` seems to take a shortcut for a member whose value is `null` that reads the name again through `FieldNameCache.intern` and passes `null` there when the name is empty. I do not know where the right fix is, or whether that shortcut should exist.

AI assistance: an AI coding assistant (Claude Code) ran the reproducer and the input variations above and drafted this report.

### Checklist

- [x] I searched existing issues, open and closed
- [ ] I reproduced this on the latest release
- [x] AI assistance was used to write this report
