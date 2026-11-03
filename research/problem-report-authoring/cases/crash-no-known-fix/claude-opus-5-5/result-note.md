# Hand-over note: quillson issue for `{"":null}`

The issue body is in `draft.md`. Nothing has been filed.

## Title

```text
[bug] Parsing {"":null} throws JsonParseException caused by NullPointerException since 3.0.0
```

## Before you file

1. **Test 3.2.0 first.** The form asks you to test the latest release, and the 3.2.0 changelog lists "Field-name interning rewritten for fewer allocations (#1187)", which touches the code in the trace. The company mirror had not synced 3.2.0 on 2026-09-23. Fetch it from Maven Central, or retry the mirror, then rerun the reproducer:

   ```bash
   mvn -q dependency:get -Dartifact=io.quillson:quillson:3.2.0 \
     -DremoteRepositories=central::default::https://repo1.maven.org/maven2
   java -cp ~/.m2/repository/io/quillson/quillson/3.2.0/quillson-3.2.0.jar EmptyKeyNull.java
   ```

   - If 3.2.0 prints `{"":null}`, don't file this. The fix is to upgrade, or to ask for a 3.1.x backport, which would be a different issue.
   - If 3.2.0 fails, tick "I reproduced this on the latest release", set the version field to `3.2.0` (keep 3.1.4 in "What happened?"), paste the 3.2.0 trace under Logs, and delete the sentence "I could not test 3.2.0…" and the #1187 sentence in "Anything else?".
   - If the releases page lists something newer than 3.2.0 (the notes are from 2026-09-23), test that instead.

2. **Rerun the duplicate search.** It was run on 2026-09-23, more than a month ago. Search https://github.com/quillson/quillson/issues?q= (issues and pull requests, open and closed) for:
   `NullPointerException FieldNameCache`, `empty key`, `"":null`, `empty field name`.
   The only hit then was #1043 (closed, fixed in 3.0.2, different trigger). If an open issue for this exists now, add your 3.1.4 transcript and the version table to it as a comment instead of opening a new one.

3. **Check the routing files, which I did not read:** `.github/ISSUE_TEMPLATE/config.yml` (contact links that may redirect reports) and `SECURITY.md`. I don't think this is a security issue: the parser throws a `JsonParseException` that the caller can catch, and there is no hang or crash beyond that. Decide that yourself if you see it differently.

4. **The AI policy needs a decision from you.** `CONTRIBUTING.md` says: "You must understand, and be able to answer questions about, everything you submit." The draft ticks the AI checkbox and has the one-line statement under "Anything else?" that the policy asks for. File it only if you have read it line by line and can answer follow-up questions about the reproducer, the version table, and the source reading without the tool.

5. **Decide whether the production paragraph should go in.** The last paragraph of "What happened?" says how many documents fail each day and that the supplier won't fix its export before Q1 2027. That comes from incident HD-5521. I left out Harbordesk, Veltro, the service and class names, the Kafka topic, and the production trace. Delete the paragraph if even those numbers shouldn't be public. The report still holds up without it.

## Filing

The web form is the safer route: paste each `###` section into the field with the same label, and tick the checkboxes there. To file from the command line instead, run:

```bash
gh issue create --repo quillson/quillson \
  --title '[bug] Parsing {"":null} throws JsonParseException caused by NullPointerException since 3.0.0' \
  --label bug \
  --body-file draft.md
```

`gh` skips the form's required-field checks, and `--label` fails for an account without triage rights on the repository. If it fails, drop the flag and the maintainers will label the issue.

## Not established, and not in the report

- No workaround was tested. Two possible ones are rewriting `"":null` to another value before parsing, or staying on 2.9.6 (end of life since 2026-06-30). Neither was run, so neither is in the report.
- The source reading wasn't checked in a debugger, and the report says so. No fix is proposed because nobody knows where it belongs.
- The operating system isn't recorded in the notes. The form doesn't ask for it, and nothing suggests the result depends on it.
