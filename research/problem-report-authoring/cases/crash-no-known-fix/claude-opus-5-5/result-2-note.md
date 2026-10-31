# Hand-over note: quillson issue for the `{"":null}` parse failure

The draft is in `draft.md`. It follows the field order of `.github/ISSUE_TEMPLATE/bug.yml`: What happened?, Reproducer, quillson version, JDK version, Logs, Anything else?, and the checkboxes. Nothing has been filed.

## Decide before filing

1. **Can you defend it yourself?** quillson's `CONTRIBUTING.md` says: "You must understand, and be able to answer questions about, everything you submit." You have not said yet whether you will review the draft line by line. Only you can confirm this. The disclosure line under "Anything else?" says what the assistant did. It does not say that you reviewed the draft, so add that only once you have.
2. **Test 3.2.0 first.** The form says "Please test the latest release first", and the draft leaves "I reproduced this on the latest release" unticked. The company mirror had not synced 3.2.0 on 2026-09-23:

   ```text
   Could not find artifact io.quillson:quillson:jar:3.2.0 in harbordesk-central (https://nexus.harbordesk.internal/repository/maven-central/)
   ```

   This matters more than usual. The 3.2.0 changelog lists "Field-name interning rewritten for fewer allocations (#1187)", and the 3.1.4 trace fails inside `FieldNameCache.intern`, so 3.2.0 may already fix this. Also check the releases page for anything newer than 3.2.0, since the notes are from 2026-09-23. To close the gap:

   ```bash
   mvn -q dependency:get -Dartifact=io.quillson:quillson:3.2.0   # once the mirror has it, or against Maven Central directly
   java -cp ~/.m2/repository/io/quillson/quillson/3.2.0/quillson-3.2.0.jar EmptyKeyNull.java
   ```

   - If 3.2.0 prints `{"":null}`, do not file. Upgrade, or ask on the tracker whether a 3.1.5 backport is planned.
   - If it fails, tick the latest-release box and change the version field to "3.2.0 and 3.1.4". Then paste the 3.2.0 trace under Logs, because its line numbers will differ.

## Lookups I could not make (no network)

- **Re-run the duplicate search** with closed issues and PRs included, because new issues may have appeared since 2026-09-23. Queries already run: `NullPointerException FieldNameCache`, `empty key`, `"":null`, `empty field name`. Add `Internal error while reading object member` and `FieldName.hash`. The only hit was #1043, which the draft cites with the difference. If an open issue for this exists now, add the reproducer and your versions to it as a comment instead of filing.
- **Routing:** I did not read `.github/ISSUE_TEMPLATE/config.yml` or `SECURITY.md`. I treated this as an ordinary bug, because the library reports the failure as `JsonParseException`, which callers already handle for malformed input. If you see it differently, use the private route instead.

## What I left out, and why

- **Private names.** The issue is public, so it leaves out Harbordesk, Veltro, the incident ticket HD-5521, the production trace (`com.harbordesk.billing.veltro.VeltroInvoiceConsumer`, the Kafka topic `hd.billing.veltro.invoices.v3`), and the internal Nexus URL. The production trace adds nothing beyond the reproducer's trace. The draft says "a partner's feed". Name the partner only if you have cleared that.
- **The hour of manual re-keying a day.** This is internal cost and does not help the maintainers. The count of 40 in 180000 documents a day stays, because it shows real input that hits the bug.

## Filing mechanics

- **Web form:** copy each section into its field. Paste the Logs field without the fence, because that field already renders as `shell`. The title prefix is `[bug] `.
- **CLI:** issue forms are not enforced there, so the `###` headings in the draft stand in for the field labels. Delete the "Title:" and "Label:" lines at the top of `draft.md` first.

  ```bash
  gh issue create --repo quillson/quillson --label bug \
    --title '[bug] Quill.parse throws "Internal error while reading object member" on {"":null} since 3.0.0' \
    --body-file draft.md
  ```

- The reproducer command expects the 2.9.6, 3.0.0, and 3.1.4 jars in `~/.m2`. This is the exact command that was run.
