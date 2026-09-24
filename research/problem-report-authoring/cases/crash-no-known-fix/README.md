# Case: a crash with no known fix

A regression case for `problem-report-authoring`. It is synthetic: the library (quillson), the company, the partner
feed, and the people are fictional. It was built to test whether the rules added after
[`nested-workflow-tag`](../nested-workflow-tag/README.md) generalize to a plain defect report, where the reporter has a
crash, a reproducer, and a regression window, and no idea where the fix goes.

## What it exercises

The rules under suspicion of overfitting, as a first draft of version 1.1.0 stated them; the published 1.1.0
restates each one, and the letters are defined in [the research README](../../README.md#cases). The present tense
below describes that draft:

- **(a)** Question 7 of §5 asks every expected block for a shape of the fix that works, backed by a document or a run.
  Here nobody has one, and the report is complete without it: the expected block states the outcome, a triager reads
  the trace, and the fix is the project's.
- **(c)** A trimmed paste. The form's Logs field asks for the full stack trace and says not to trim it; the rule to
  paste only the lines that carry the claim must yield to the form.
- **(e)** A gap no claim seems to rest on. 3.2.0 came out the day before and was not tested; the form asks for the
  latest release first, so a triager needs to read that it was not tried, in the report and not only in the note.
- **(f)** Isolation evidence and negative results. The table of inputs that do and do not fail is what narrows the
  trigger; it belongs in the report, not in the hand-over note.
- **(b)** The disclosure the project's `CONTRIBUTING.md` requires helps nobody reproduce, accept, or fix the crash,
  and it still has to be there.

The padding: the business context and its cost, the partner's name and schedule, the production trace with private
names, three JDKs that behave the same, the list of search queries, the unrelated closed issue, the mirror's error
message, and a reading of the source that was never checked.

## Files

| File | What it is |
| --- | --- |
| `prompt.md` | The investigation notes, frozen as of 2026-09-23, with the drafting task at the end. |
| `<model>/result.md` | The issue body the model wrote. |
| `<model>/result-note.md` | The hand-over note to the person filing, kept apart from the body. |

## How to run

Use the prompt in [`../nested-workflow-tag/README.md`](../nested-workflow-tag/README.md#how-to-run) as it stands, with
`<case>` set to this directory. It needs no network.

## Checks

Each check names the rule or the suspected regression it guards. Read `result.md` against all of them.

1. **The expected block states the outcome, not a mechanism** (a). `Quill.parse("{\"\":null}")` returns an object with
   one member whose name is the empty string and whose value is JSON `null`, as 2.9.6 does, and throws nothing. The
   block names no place in quillson's code as the fix. The report does not fail for proposing no fix, and an invented
   fix shape fails the check.
1. **The trace is whole and verbatim** (c). Both the `JsonParseException` and the `Caused by` block with `... 8 more`,
   tabs and punctuation as printed, in the Logs field. A trace cut to the `Caused by` lines fails.
1. **The regression window is stated.** Last good 2.9.6, first bad 3.0.0, reproduced on 3.1.4, which is inside the
   support window.
1. **The untested release is stated in the report** (e). The report says 3.2.0 was not tested, and the "reproduced on
   the latest release" box is not ticked. The note carries the command that would close the gap. Saying that 3.2.0 may
   fix it because of #1187 is a guess and fails unless marked as one.
1. **The trigger is narrowed with inputs that pass** (f). The report shows that `{"":1}` and `{"a":null}` parse on
   3.1.4, so the crash needs both an empty name and a `null` value.
1. **The disclosure is answered** (b). The AI box is ticked and one line under "Anything else?" says what the tool
   did; whether the person filing can answer for the report is raised in the note.
1. **Nothing is there only because it is true.** The body carries none of: the invoice volumes, the billing team's
   cost, Veltro or its schedule, the incident ID, the production trace or any `harbordesk` name, the mirror's error,
   the search queries, a table of JDK versions. #1043 appears in at most one sentence that says why it differs. The
   reading of the source is absent or marked as a guess the report stands without.
1. **The prose is short.** Words outside code blocks: read the result sentence by sentence past 300.

Checks 2 and 4 to 7 can be counted, from this directory, with the model's directory as the argument. Every "present"
marker for evidence should print `True`, every padding marker `False`; the fix shape and the guess still need a
reading.

```bash
python3 - claude-opus-5-5 <<'EOF'
import re, sys
text = open(f'{sys.argv[1]}/result.md').read()
prose = re.sub(r'```.*?```', '', text, flags=re.S)
print('prose words:', len(prose.split()), '(read sentence by sentence past 300)')
for marker in ['Caused by: java.lang.NullPointerException', '... 8 more', '2.9.6', '3.0.0', '3.2.0', '{"":1}']:
    print(f'{marker!r} present (expect True):', marker in text)
print('AI disclosure present (expect True):', bool(re.search(r'\bAI\b', text)))
print('search queries listed (expect False):', bool(re.search(r'[`"](empty key|empty field name)[`"]', text)))
for marker in ['Veltro', 'invoice', 'HD-5521', 'harbordesk', 'Kafka', 'nexus', 'Q1 2027']:
    print(f'{marker!r} present (expect False):', marker.lower() in text.lower())
EOF
```
