# Hand-over note: quillson empty-name/null crash (HD-5521)

Not part of the issue body. The body is `result.md`, written with the form's labels as headings so it can go in through `gh`.

## Before filing

1. **Can you defend it?** quillson's `CONTRIBUTING.md` ("AI-assisted contributions") says the submitter must understand and be able to answer questions about everything submitted. You have not said yet whether you will review the draft line by line. Please read it, in particular the regression claim, the input table, and the marked source reading, before filing. If you would not stand behind the source-reading paragraph, delete it; the report stands without it.
2. **Test 3.2.0 (released 2026-09-22).** The bug form asks to test the latest release first, and its changelog has "Field-name interning rewritten for fewer allocations (#1187)", which touches the code in the trace. The company Nexus mirror had not synced 3.2.0, so it was not tested. Once it is available (mirror, or directly from Maven Central):

   ```bash
   mvn -q dependency:get -Dartifact=io.quillson:quillson:3.2.0
   java -cp ~/.m2/repository/io/quillson/quillson/3.2.0/quillson-3.2.0.jar EmptyKeyNull.java
   ```

   - If it prints `{"":null}`: do not file. Upgrading to 3.2.0 is the fix; consider a comment on #1187 only if you want to confirm it.
   - If it still fails: tick "I reproduced this on the latest release", change the **quillson version** field to "3.2.0 (also 3.1.4 and 3.0.0; works on 2.9.6)", replace the 3.1.4 trace under Logs with the 3.2.0 one if its line numbers differ, and delete the 3.2.0 changelog sentence under "Anything else?".
3. **Re-run the duplicate search right before filing.** It was done during the session, not now (no network here). On https://github.com/quillson/quillson/issues?q= with `is:issue is:pr` and both open and closed: `NullPointerException FieldNameCache`, `empty key`, `"":null`, `empty field name`; add `FieldName.hash` and `empty member name`. Only #1043 turned up before.
4. **Optional check:** the `CHANGELOG.md` entries for 3.0.0 were not read for an intended change to empty member names. A quick look there would rule out "this was deliberate".

## What was left out of the public issue, on purpose

- The production trace (34 lines, 2026-09-22T07:14:09.331Z): it carries `com.harbordesk.billing.veltro.VeltroInvoiceConsumer`, the Kafka topic `hd.billing.veltro.invoices.v3`, and Spring Kafka frames. The quillson frames are identical to the reproducer's, so the issue says so in one sentence and pastes the reproducer trace instead.
- The partner name (Veltro), the ticket HD-5521, and the internal Nexus hostname. The impact figures (about 40 of 180,000 documents a day, re-keyed by hand) stay, without names.
- No workaround is claimed. If the team later finds one (for example pre-processing the documents to drop `"":null` members), it belongs in HD-5521, and in a comment on the issue if it helps others.

## Filing

The form's required fields are only enforced in the web UI. Either paste each section into the web form (fields and checkboxes line up with the headings), or:

```bash
gh issue create --repo quillson/quillson \
  --title '[bug] Quill.parse throws JsonParseException "Internal error" (NullPointerException) on an empty member name with a null value, e.g. {"":null}' \
  --label bug \
  --body-file result.md
```

`--label bug` may be refused if you lack triage rights on the repository; drop it in that case, the form would have applied it.
