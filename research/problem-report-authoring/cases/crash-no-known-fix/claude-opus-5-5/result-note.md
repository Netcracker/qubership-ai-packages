# Hand-over note: quillson empty-name/null-member issue

Not part of the issue body. The body is in `result.md`; nothing has been filed.

## Before filing: run the reproducer on 3.2.0

The form asks reporters to test the latest release first, and 3.2.0 (2026-09-22) was not tested: the company mirror had not synced it. Its changelog entry "Field-name interning rewritten for fewer allocations (#1187)" touches the area in the trace, so it may already fix this.

```bash
mvn -q dependency:get -Dartifact=io.quillson:quillson:3.2.0 \
  -DremoteRepositories=https://repo.maven.apache.org/maven2
java -cp ~/.m2/repository/io/quillson/quillson/3.2.0/quillson-3.2.0.jar EmptyKeyNull.java
```

- If it prints `{"":null}`: do not file. Check #1187 to confirm it covers this, and plan the upgrade to 3.2.x (3.1.x is still supported, so asking for a 3.1 backport is an option).
- If it fails: change the "quillson version" field to name 3.2.0 as failing, delete the 3.2.0 sentence under "Anything else?", tick "I reproduced this on the latest release", and paste the 3.2.0 trace under Logs if its line numbers differ.

## Duplicate search to re-run just before filing

Queries run on 2026-09-23 against quillson/quillson issues and pull requests, open and closed: `NullPointerException FieldNameCache`, `empty key`, `"":null`, `empty field name`. Only hit: #1043. Also worth trying: `Internal error while reading object member`, `FieldName.hash`, and a look at PR #1187 and anything linked from it.

## Questions for you

- quillson's `CONTRIBUTING.md` says you must understand, and be able to answer questions about, everything you submit. Please read the draft line by line before filing; only you can decide that you can defend it.
- The AI disclosure line under "Anything else?" is my wording; adjust it to say what the tool actually did (for example, whether it also ran the reproducer).

## Lookups not made

- `.github/ISSUE_TEMPLATE/config.yml` (contact links, routing) and `SECURITY.md` were not in the notes. Glance at them; I don't consider this a vulnerability report (the parser throws an exception; no hang or memory growth was observed), but the routing check was not done.

## What was left out on purpose

- Private names: Harbordesk, the partner Veltro, the service and consumer class names, the Kafka topic, the ticket HD-5521. The impact sentence describes the traffic without them.
- The production log (34 lines): it shows the same `Caused by` block under our own frames and adds nothing the reproducer does not.
- The billing team's hour a day of manual re-keying: impact for us, not for the maintainers.
- An untried workaround (stripping `"":null` members before parsing) was not suggested.

## Filing

With `gh`, the form's required fields are not enforced, so the body carries the field labels as headings and the checkboxes as a task list:

```bash
gh issue create --repo quillson/quillson \
  --title '[bug] Quill.parse throws "Internal error while reading object member" on {"":null} since 3.0.0' \
  --label bug \
  --body-file result.md
```

If you use the web form instead, paste each section into its field; the Logs field wraps its content in a `shell` block itself, so paste the trace there without the surrounding fence.
