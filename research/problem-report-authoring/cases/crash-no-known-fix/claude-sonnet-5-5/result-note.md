# Hand-over note for the person filing (not part of the issue)

Nothing has been filed or sent. The body is in `draft.md`. It uses the headings of `quillson/quillson`'s `bug.yml` in the form's order.

## To file

```bash
gh issue create --repo quillson/quillson \
  --title '[bug] Quill.parse throws JsonParseException on {"":null} since 3.0.0' \
  --body-file draft.md --label bug
```

`gh` does not enforce the form's required fields, so the headings and checkboxes are written into the body. A reporter without triage rights may not be able to set `--label bug`; if `gh` refuses, drop the flag.

## Decisions for you

1. **AI policy.** `CONTRIBUTING.md` allows AI-assisted issues if you tick the box, add one line under "Anything else?", and "understand, and be able to answer questions about, everything you submit." The draft ticks the box and carries the line, but you have not said whether you will read it line by line. Do that before filing, and correct the disclosure line if what the assistant did differs from what it says.
2. **What goes public.** The issue says that about 40 of 180,000 documents a day fail and that billing loses about an hour a day. It also says the supplier will not change its export before Q1 2027. These figures come from the incident ticket HD-5521, not from my runs. Confirm you are willing to publish them, or cut the second paragraph of "What happened?" down to the goal.
3. I did not name Harbordesk, the supplier, the ticket ID, the consumer class, or the Kafka topic. Nothing was substituted, so the report carries no "names were changed" sentence.

## Not established (run these before filing)

- **Latest release.** My runs are from 2026-09-23. I could not test 3.2.0 (released 2026-09-22) because the company mirror had not synced it, and the form asks you to test the latest release first. Today is 2026-10-31, so there may be newer releases too. Check the releases page, then fetch from Maven Central directly:
  `mvn -q dependency:get -Dartifact=io.quillson:quillson:3.2.0 -Dtransitive=false -DremoteRepositories=https://repo1.maven.org/maven2`
  then add `3.2.0` (and any newer version) to the `for` loop in the reproducer. If the newest release no longer fails, say so in the issue; the report may then be unnecessary. If it still fails, add it to the "quillson version" field, tick "I reproduced this on the latest release", and re-paste the trace if it differs.
- 3.2.0's `CHANGELOG.md` lists "Field-name interning rewritten for fewer allocations (#1187)". That touches the area the stack trace names, but I did not test it, so the issue does not mention it.
- **Support window.** The README quote ("3.2.x and 3.1.x receive fixes. 2.9.x reached end of life on 2026-06-30.") was read on 2026-09-23. Re-read it. 3.1.4 was the latest 3.1 patch then.
- **Whether 3.0.0 changed this on purpose.** I did not read the 3.0.0 section of `CHANGELOG.md` or any compatibility statement. If the project documents that empty member names are rejected, or excludes undocumented behavior from its compatibility promise, the "Expected" paragraph rests on less than it claims. Read the 3.0.0 changelog and the README before filing.
- **Duplicate search.** I ran these on issues and pull requests, open and closed: `NullPointerException FieldNameCache`, `empty key`, `"":null`, `empty field name`. Only #1043 came back. Repeat them for anything opened since 2026-09-23. If an open issue now covers this, add a comment with the version, the input table, and the trace instead of filing a second report. Also look for an open pull request that changes the same code.
- **Reproducer.** The pasted output is from the 2026-09-23 run; I did not re-run it for this draft. Run it once from an empty directory before filing.

## Left out of the issue

- The 34-line production trace (2026-09-22T07:14:09.331Z). It adds only company class names, the topic name, and Spring Kafka frames on top of the same `Caused by` block. The issue says the log shows that block.
- The Maven mirror error for 3.2.0, which contains an internal hostname.
- Any workaround on your side. The notes record none, so the issue names none.
