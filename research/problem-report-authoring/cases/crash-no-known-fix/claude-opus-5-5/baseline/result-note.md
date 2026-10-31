# Hand-over note: quillson `{"":null}` issue

The issue body is in `draft.md`, laid out in the order of the fields in `.github/ISSUE_TEMPLATE/bug.yml`. Nothing has been filed. Every observation in it is from the 2026-09-23 session.

## Before filing: test 3.2.0 first

This decides whether you file at all. The form asks you to "test the latest release first". 3.2.0 came out on 2026-09-22, and its changelog lists "Field-name interning rewritten for fewer allocations (#1187)". The trace fails inside `FieldNameCache.intern`, so that rewrite may already have fixed this. The session could not get 3.2.0 because `nexus.harbordesk.internal` had not synced it.

From a machine that reaches Maven Central directly, or once the mirror has synced:

```bash
mvn -q dependency:get -Dartifact=io.quillson:quillson:3.2.0
java -cp ~/.m2/repository/io/quillson/quillson/3.2.0/quillson-3.2.0.jar EmptyKeyNull.java
```

- **If it prints `{"":null}`:** don't file. Upgrading the service to 3.2.0 fixes it. You could optionally comment on #1187 or its pull request to say it fixed this input.
- **If it fails:** paste the 3.2.0 trace into Logs in place of the 3.1.4 one, or next to it. Change the version field to "3.2.0 and 3.1.4". Tick "I reproduced this on the latest release". Change the title's "since 3.0.0" only if the range changes. Delete the #1187 sentence in "Anything else?".

## Lookups this session did not make

- **Duplicate search.** It ran on 2026-09-23, and 3.2.0 has shipped since. Search again in issues and pull requests, open and closed, with these queries: `NullPointerException FieldNameCache`, `empty key`, `"":null`, `empty field name`. Add `FieldNameCache.intern` and `#1187` too. The only hit last time was #1043, which is cited in the draft. If an open issue now covers this, add a comment there with the version, the input table, and the trace instead of filing a new issue.
- **Routing.** No one read `.github/ISSUE_TEMPLATE/config.yml` (contact links) or `SECURITY.md`. I don't think this is a security issue: the failure reaches the caller as a `JsonParseException`, and nothing beyond that was observed. Still, check that `config.yml` doesn't send this kind of report somewhere else.

## Decisions that are yours

- **The AI policy.** `CONTRIBUTING.md` says: "You must understand, and be able to answer questions about, everything you submit." Only file if you can explain the report, the analysis paragraph included, and answer follow-up questions yourself. Check that the disclosure line in "Anything else?" describes what actually happened. If you rewrite parts of it yourself, add that to the line.
- **Disclosing the impact.** The draft says the service gets about 40 bad documents out of 180000 a day from a partner, and that the partner won't change its export before Q1 2027. It doesn't name Harbordesk, Veltro, the service, or the Kafka topic. Delete that paragraph if those numbers shouldn't appear in public.

## What was deliberately left out

- **The production trace** (2026-09-22T07:14:09.331Z). It contains internal names (`com.harbordesk.billing.veltro.VeltroInvoiceConsumer`, `hd.billing.veltro.invoices.v3`, the Spring Kafka frames) and adds nothing the standalone reproducer doesn't already show. The reproducer depends only on quillson and the JDK.
- **A workaround.** None was tried, so the draft doesn't suggest one.

## Filing

**In the web form:** paste each `###` section into the field with that name. In **Logs**, paste only the trace, without the "```shell" fence lines, because the form already displays that field as `shell`. Tick the checkboxes as marked at the end of the draft.

**From the command line** (this skips the form's checks, which is why the body includes the field headings and checkboxes itself): first delete the `**Title:**` and `**Label:**` lines at the top of `draft.md`, then run

```bash
gh issue create --repo quillson/quillson \
  --title '[bug] Quill.parse fails with "Internal error" on {"":null} since 3.0.0' \
  --label bug \
  --body-file draft.md
```
