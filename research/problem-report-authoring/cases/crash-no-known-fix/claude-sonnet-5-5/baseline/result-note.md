# Hand-over note for the quillson issue (not part of the issue body)

Nothing has been filed. The body is in `draft.md`.

## Title and filing command

Title: `[bug] Quill.parse throws JsonParseException (NullPointerException) for an object member with an empty name and a null value`

```bash
gh issue create --repo quillson/quillson \
  --title '[bug] Quill.parse throws JsonParseException (NullPointerException) for an object member with an empty name and a null value' \
  --body-file draft.md
```

The `bug` label is left off because `gh` fails for someone without triage rights, and the form applies it in the web UI. The body uses the form's field names as headings, so you can also paste each section into the web form. The form's required-field check runs only there.

## Decide before filing

1. **Run 3.2.0 first.** The form asks to test the latest release, and I could not (the company mirror had not synced it). Resolve it from Maven Central directly, then rerun the reproducer with that jar:
   ```bash
   mvn -q dependency:get -Dartifact=io.quillson:quillson:3.2.0
   java -cp ~/.m2/repository/io/quillson/quillson/3.2.0/quillson-3.2.0.jar EmptyKeyNull.java
   ```
   If it still fails, tick "I reproduced this on the latest release", put the trace's line numbers in if they differ, and drop the "Not tested" paragraph and the version-field remark. If it parses, there is nothing to file against 3.2.0; whether to report the 3.1.x line, which still receives fixes, is your call.
2. **AI policy.** `CONTRIBUTING.md` says you must understand, and be able to answer questions about, everything you submit. I can't certify that. Please read the report line by line first. If you won't, don't file it. I ticked the AI box and added the one-line description under "Anything else?", as the policy asks.
3. **Publishing internal figures.** The report gives the incident numbers (about 40 of 180,000 documents a day, about an hour a day of manual re-keying). Remove that paragraph if you don't want them public. It's an impact I could cite from the ticket, not one I observed.

## Left out on purpose

- The production trace (34 lines). It carries the consumer class, the Kafka topic, and Spring frames, and the reproducer trace shows the same failure.
- The company name, the partner's name, the ticket ID HD-5521, and the partner's statement that the export won't change before Q1 2027. The report says only that the partner's export produces the empty key.
- The Maven mirror error text (internal hostname). The report says the mirror had not synced 3.2.0.
- Any workaround. Nothing was tried, so none is claimed.

## Lookups I could not make

- **3.0.0 release notes and changelog.** Check whether empty member names or null handling were changed on purpose between 2.9.6 and 3.0.0. The report says this is not established. If it was intentional, the report becomes a request and needs rewording. Check `CHANGELOG.md` under 3.0.0 and the 3.0.0 release page.
- **Documentation on empty member names.** I found no statement either way in the notes. If the README or docs describe empty names, cite it in the expected-behavior paragraph, since that grounding is stronger than the 2.9.6 behavior (2.9.x is end of life).
- **`.github/ISSUE_TEMPLATE/config.yml`.** I didn't see the contact links. Check that none redirects bug reports elsewhere.
- **`SECURITY.md`.** I treated this as an ordinary defect, with no security impact claimed or observed.
- **Wider duplicate search.** Run so far (issues and pull requests, open and closed): `NullPointerException FieldNameCache`, `empty key`, `"":null`, `empty field name`. One hit, #1043, which has a different trigger. Also try `Internal error while reading object member`, `empty member name`, `FieldName.hash`, and the pull request behind #1187. An open report of the same defect would make this a comment instead of a new issue.
- **Rendering.** I didn't open an existing quillson issue to confirm fenced blocks render as expected.

## Not done

- The source reading in "Anything else?" was not checked in a debugger. It's marked as a guess and the report stands without it. Delete it if you'd rather not carry it.
- The 3.0.0 and the JDK 17 and 23 results come from the session's runs; I didn't repeat them after the last edit of the draft, which doesn't change any code.
