# Hand-over note for the quillson issue

Nothing has been filed or sent. The issue body is in `draft.md`, written against `.github/ISSUE_TEMPLATE/bug.yml` with the form's field names as headings.

## Decide before filing

1. **The AI policy.** `CONTRIBUTING.md` says you "must understand, and be able to answer questions about, everything you submit." You haven't said whether you will review the draft line by line. Please do, and be ready to answer follow-ups yourself. The draft ticks the AI box and has the one-line disclosure under "Anything else?". Edit that line if it doesn't describe what happened. The policy asks only for disclosure, but I could not check whether the project welcomes tool-written reports beyond that.
2. **Public figures.** The draft says 40 of 180,000 documents a day and about an hour a day of manual re-keying. These come from your incident ticket, not from anything I observed. Confirm the numbers and that your company is fine with them being public.

## Not established (close before filing)

- **3.2.0 was not tested.** The form says to test the latest release first. The company mirror had not synced 3.2.0 (`Could not find artifact io.quillson:quillson:jar:3.2.0 in harbordesk-central`). From a machine that reaches Maven Central directly:

  ```bash
  mvn -q dependency:get -Dartifact=io.quillson:quillson:3.2.0 -DremoteRepositories=https://repo.maven.apache.org/maven2
  java -cp ~/.m2/repository/io/quillson/quillson/3.2.0/quillson-3.2.0.jar EmptyKeyNull.java
  ```

  The 3.2.0 changelog lists a field-name interning rewrite (#1187), so the result could go either way. If it parses, don't file; the bug is fixed upstream, and you may want to ask which release has it. If it fails, add the trace difference if any, tick "I reproduced this on the latest release", and drop the "Not established" paragraph under "quillson version".
- **Reproducer re-run.** Every run in the draft was done by the session on 2026-09-23. You have not re-run it. Run the loop from a clean directory once before filing.
- **Not checked:** the 3.0.0 release notes for an intentional change, and the README or docs for a compatibility promise on 3.x. The draft says only that I have not checked the first.
- **Tracker search.** Queries run: `NullPointerException FieldNameCache`, `empty key`, `"":null`, `empty field name`, in issues and pull requests, open and closed. Only #1043 came up. Re-run them once, and also check PR #1187 and anything filed since 2026-09-23, and tick the "searched" box only if you are satisfied. Nothing can establish absence from these queries alone.

## Deliberately left out of the draft

- The production trace (internal class `VeltroInvoiceConsumer`, the Kafka topic name). The reproducer already shows the same `Caused by` block.
- The partner's name, the incident ticket number HD-5521, and your company's name. The public repository doesn't need them.
- Any workaround. None was established in the session. If your team filters the empty key before parsing, say how and what it changed, and it can go in under "Anything else?" after the problem.
- A suggested fix. The session has no basis for one.
- A standards argument: an empty string is a valid JSON member name under RFC 8259. That is general knowledge, not checked against what quillson claims to implement. Add it as a weaker second ground if you want it.

## How to file

Easiest is the web form, pasting each section into its field and ticking the boxes (the title prefix `[bug] ` and the `bug` label come from the form). From the CLI, the form's required fields are not enforced and the label may be refused if you lack triage rights on the repository:

```bash
gh issue create --repo quillson/quillson \
  --title '[bug] Quill.parse throws JsonParseException for {"":null}, which parsed in 2.9.6' \
  --body-file draft.md
```
