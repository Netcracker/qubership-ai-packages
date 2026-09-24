# Case: a vendor ticket after the incident is over

A regression case for `problem-report-authoring`. It is synthetic: the vendor (Tessary Object Storage), the customer,
and the people are fictional. It was built to test whether the rules added after
[`nested-workflow-tag`](../nested-workflow-tag/README.md) generalize to a support ticket, where there is no source to
read, no fix the customer can shape, and the ask is information and money rather than a change.

## What it exercises

The rules under suspicion of overfitting, as a first draft of version 1.1.0 stated them; the published 1.1.0
restates each one, and the letters are defined in [the research README](../../README.md#cases). The present tense
below describes that draft:

- **(b)** The decision deletion test keeps a sentence only if it helps the maintainer reproduce, accept, or choose a
  fix. A vendor ticket asks for none of the three: its ask is a timeline, an answer about throttling, and a credit, and
  the verified mitigation is what tells the vendor the incident is over and what severity fits. The test, applied as
  written, deletes the reason the ticket exists.
- **(a)** Question 7 of §5 asks for a shape of the fix that works. The customer cannot see the vendor's internals and
  has no shape to offer; the expected behavior is the documented request rate and the SLA.
- **(f)** Isolation evidence. The other region, the GETs, and the measured prefix rate against the documented limit
  are what show the vendor that the customer did not exceed a limit. Moved to the hand-over note, they leave the
  vendor free to answer "reduce your request rate".
- **(g)** Unverified shapes. The ticket may ask whether a partition was being scaled, as a question; it may not tell the
  vendor how to fix partition scaling.

The padding: the on-call chatter, the dashboard and its panels, the previous week's unrelated incident, and four
things tried during the incident that changed nothing and that the other-region control already rules out.

## Files

| File | What it is |
| --- | --- |
| `prompt.md` | The investigation notes, frozen as of 2026-09-23, with the drafting task at the end. |
| `<model>/result.md` | The field values and the description the model wrote. |
| `<model>/result-note.md` | The hand-over note to the person filing, kept apart from the case. |

## How to run

Use the prompt in [`../nested-workflow-tag/README.md`](../nested-workflow-tag/README.md#how-to-run) with `<case>` set
to this directory, "a GitHub issue" read as "a vendor support case", and "the issue body" as "the case's field values
and description". It needs no network.

## Checks

Each check names the rule or the suspected regression it guards. Read `result.md` against all of them.

1. **The ask is explicit** (b). "What do you need from us?" asks for three things: whether eu-north-2 had an incident
   or a partition scaling event from 14:05 to 14:45 UTC on 2026-09-21, with a timeline or root cause; whether the
   account or its prefixes were throttled; and the SLA credit under §5, with §6's data supplied.
1. **The window and the IDs are there** (support-ticket table: the reproducer). The window in UTC, the five request
   IDs with their host IDs, the counts, and the CSV of the other 1,212 named as an attachment with its size.
1. **The isolation evidence is in the case, not the note** (f). The eu-west-3 PUTs with no errors, the GETs at 0.02%,
   and the busiest prefix at 5.9 PUT/s against the documented 3,500, which is also what answers the SLA's exclusion
   for requests over the documented rate.
1. **The verified mitigation is kept** (b). Backoff with jitter, deployed at 14:25 UTC, with upload failures down
   from 7.90% to 0.32% while the per-attempt 503 rate stayed near 8%, placed after the problem.
1. **No fix is prescribed** (a, g). The case asks questions about the vendor's side and proposes no change to it.
1. **The right names stay and the wrong ones go** (§6, redaction). The account ID, the three bucket names, the region,
   and the egress addresses stay. The internal hostname, `mediapipe-uploader`, the access key ID, and the signature
   are gone; the debug log, if pasted, is redacted in place and says so.
1. **The fields are filled by the portal's definitions** (§8). Severity S3, by the portal's own wording for an issue
   that is mitigated and needs a root cause and a credit; Service and Region set; the subject under 120 characters; the
   description in plain text, with no Markdown table or code fence, because the portal renders none.
1. **Every time carries a zone** (support-ticket table: the version). No CEST time appears without its UTC equivalent,
   or the case uses UTC throughout.
1. **Nothing is there only because it is true.** The case carries none of: the Slack thread, the dashboard, the
   previous week's incident, the pod restarts, the thumbnail rollback, the memory limit, the DNS cache.
1. **The prose is short.** Words outside code blocks: read the result sentence by sentence past 300.

Checks 2, 3, 6, and 9 can be counted, from this directory, with the model's directory as the argument. Every
"present" marker should print `True`, every "absent" marker `False`, and the request-ID count should be at least 5.

```bash
python3 - claude-opus-5-5 <<'EOF'
import re, sys
text = open(f'{sys.argv[1]}/result.md').read()
prose = re.sub(r'```.*?```', '', text, flags=re.S)
print('prose words:', len(prose.split()), '(read sentence by sentence past 300)')
print('request IDs (expect >= 5):', len(set(re.findall(r'\b[0-9a-f]{16}\b', text))))
print('CSV of the rest named (expect True):', bool(re.search(r'1,?21[27]|\.csv', text)))
for marker in ['acc-7f3e9120', 'lm-prod-ingest-eun2', 'lm-prod-thumbs-eun2', 'eu-west-3', '0.32%', 'credit',
               'throttl', 'S3']:
    print(f'{marker!r} present (expect True):', marker in text)
for marker in ['lm-prod.internal', 'mediapipe', 'TKAQ7M2XJ4PL9RWE', 'Signature=4be1', 'Grafana', 'Slack',
               'DNS cache', 'memory limit', 'thumbnail-service']:
    print(f'{marker!r} absent (expect False):', marker in text)
EOF
```
