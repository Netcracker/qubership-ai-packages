# Hand-over note: quillson issue for the empty-name `null` member crash (HD-5521)

The issue body is in `draft.md`. Nothing has been filed. Everything in it comes from the session on 2026-09-23. Today is 2026-10-31, so do steps 1 and 2 before you file.

## Title

```text
[bug] Parsing {"":null} throws JsonParseException "Internal error while reading object member" since 3.0.0
```

## Before filing

1. **Test 3.2.0, the latest release, and check whether anything newer exists.** The form asks you to test the latest release first, and the draft says 3.2.0 was not tested. The session could not fetch 3.2.0 because the `harbordesk-central` mirror had not synced it. The 3.2.0 changelog lists "Field-name interning rewritten for fewer allocations (#1187)", and the NPE is thrown in `FieldNameCache.intern`. 3.2.0 may already fix this. Run:

   ```bash
   mvn -q dependency:get -Dartifact=io.quillson:quillson:3.2.0
   # if the mirror still lacks it:
   curl -fLo quillson-3.2.0.jar https://repo1.maven.org/maven2/io/quillson/quillson/3.2.0/quillson-3.2.0.jar
   java -cp quillson-3.2.0.jar EmptyKeyNull.java
   ```

   - If 3.2.0 prints `{"":null}`, don't file. Upgrading the service to 3.2.0 is the fix for HD-5521.
   - If 3.2.0 fails, add it to the "quillson version" field (for example "3.1.4 and 3.2.0"), remove the "Not tested on 3.2.0" sentence, tick "I reproduced this on the latest release", and paste the 3.2.0 trace under Logs if it differs from the 3.1.4 trace.
   - Do the same for any release newer than 3.2.0 on https://github.com/quillson/quillson/releases.

2. **Search the tracker again.** The search was run on 2026-09-23, covered issues and pull requests, open and closed, and found only #1043. Rerun it for anything filed since then, and open #1187 to see whether it mentions empty names:

   - `NullPointerException FieldNameCache`
   - `empty key`
   - `"":null`
   - `empty field name`
   - `FieldName.hash`

   If you find an open issue for the same defect, post the draft's version, reproducer, and trace there as a comment instead of filing a new issue.

3. **AI policy: your call.** quillson's `CONTRIBUTING.md` says: "You must understand, and be able to answer questions about, everything you submit." You haven't said whether you will review the draft line by line. Only file it if you can answer follow-up questions without the tool. The disclosure line under "Anything else?" and the ticked checkbox are what the policy asks for. Edit the line if your part in this was different (for example, if you reviewed or reran it).

## Choices made in the draft

- **The production trace and internal names are left out.** The log from 2026-09-22T07:14:09.331Z contains the `com.harbordesk.billing.veltro` package, the Kafka topic `hd.billing.veltro.invoices.v3`, and Spring Kafka frames. The standalone reproducer shows the same `Caused by` block, so the public issue needs neither. The partner (Veltro) and the incident ticket number are not named either. Check that you're fine with sharing the "about 40 of 180000 documents a day" figure. If not, delete that paragraph; the report stands without it.
- **The source reading under "Anything else?"** is marked as unverified. Delete it if you'd rather not defend it in the thread.
- **No workaround is offered.** None was tried. Preprocessing the documents to drop `"":null` members before parsing might work but wasn't tested.

## Filing

- **Web form:** paste each `###` section into the field with the same label. The Logs field is rendered as `shell`, so paste the trace into it without the surrounding fence. Tick the checkboxes as shown at the end of the draft. The draft omits the label of the checkbox field because the session didn't record it.
- **CLI:** issues created with `gh` skip the form, so the `###` headings stand in for the fields. `--label bug` needs triage rights on the repository. If `gh` rejects the label, leave out `--label` and let the maintainers add it.

  ```bash
  gh issue create --repo quillson/quillson \
    --title '[bug] Parsing {"":null} throws JsonParseException "Internal error while reading object member" since 3.0.0' \
    --label bug \
    --body-file draft.md
  ```
