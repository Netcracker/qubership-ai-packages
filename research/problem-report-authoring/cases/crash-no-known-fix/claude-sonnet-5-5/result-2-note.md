# Hand-over note for the person filing

Nothing has been filed or sent. `draft.md` is the issue body, with the headings named after the fields of `.github/ISSUE_TEMPLATE/bug.yml` in the form's order.

## Filing

Fields and checkboxes are enforced only in the web UI. With the CLI, the headings and checklist in the body stand in for them:

```bash
gh issue create --repo quillson/quillson \
  --title '[bug] Parsing {"":null} throws JsonParseException on 3.0.0 and later; 2.9.6 parses it' \
  --label bug \
  --body-file draft.md
```

If you use the web form, paste each section into the field of the same name.

## Decisions for you

1. **Can you explain and defend this report without the tool?** `CONTRIBUTING.md` ("AI-assisted contributions") says you must understand, and be able to answer questions about, everything you submit. You haven't said yet whether you will review the draft line by line. I ticked the AI box and added the one-line disclosure under "Anything else?" because the form asks for both. Edit the disclosure line if it doesn't describe what happened.
2. **Is naming the production impact acceptable?** The draft says "a supplier feed" and "our invoice-import service" and leaves out the partner's name, the company name, the internal class, the Kafka topic, and the Nexus host. Change that if you want more or less said.

## Not established, and the command that closes it

- **3.2.0 (latest release, 2026-09-22) was not tested.** The company mirror hadn't synced it. The report says so under "quillson version", and I left the "reproduced on the latest release" box unticked. The form asks for the latest release first, so do this before filing if you can, from a machine that reaches Maven Central directly:

  ```bash
  mvn -q dependency:get -Dartifact=io.quillson:quillson:3.2.0
  java -cp ~/.m2/repository/io/quillson/quillson/3.2.0/quillson-3.2.0.jar EmptyKeyNull.java
  ```

  Then update "quillson version", tick the box, and change the title if 3.2.0 no longer fails. The 3.2.0 changelog entry "Field-name interning rewritten for fewer allocations (#1187)" touches the area, so either result is plausible.
- **Whether the 3.0.0 change was intentional.** I did not read the 3.0.0 release notes or the README for a compatibility statement or a mention of empty member names. Check `CHANGELOG.md` for 3.0.0 and any semantic versioning promise. If either covers this, the "Expected" paragraph can cite it as a stronger grounding than the 2.9.6 behavior.
- **The `Quill.reader().parse(Reader)` case** is recorded as failing with the same cause, but my notes don't say which version it was run on. The draft says 3.1.4. Re-run it before filing, or delete the sentence.
- **Operating system.** The notes don't record it, and the form has no field for it, so the draft omits it.
- **The 3.0.0 trace** is described as identical to 3.1.4 apart from quillson line numbers. I did not paste it.

## Left out on purpose

- The 34-line production trace. The `Caused by` block matches the pasted one, and the rest holds internal names (service class, topic) and Spring Kafka frames. Offer a redacted copy if a maintainer asks.
- Tracker queries: `NullPointerException FieldNameCache`, `empty key`, `"":null`, `empty field name`, issues and pull requests, open and closed. Only hit: #1043. The form has no slot for queries, so the report carries the hit and the difference only. Re-run them if some time has passed.
- No workaround is known, so the report has no workaround section. A fix location is unknown, so the report suggests none; the source reading is marked as a guess.
- The 2.9.x end of life (2026-06-30) is not in the report. It matters only because the last good version is outside the support window, and 3.1.4, which is supported, fails.
