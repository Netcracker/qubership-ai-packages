# Case: a request against a deliberate exception

A regression case for `problem-report-authoring`. It is synthetic: the project (Tallyqueue), the operator, its
security standard, and the people are fictional. It was built to test whether the rules added after
[`nested-workflow-tag`](../nested-workflow-tag/README.md) generalize to a feature request, where the gap looks like an
inconsistency in the project and is in fact a documented decision, and the requirement comes from the operator's own
standard.

## What it exercises

The rules under suspicion of overfitting, as a first draft of version 1.1.0 stated them; the published 1.1.0
restates each one, and the letters are defined in [the research README](../../README.md#cases). The present tense
below describes that draft:

- **(d)** Local consistency ranked with the project's own specification (question 4 of §5). Twenty-two management
  paths require a token and one does not, which is the shape of "a file that pins every call but one". Here the one
  is deliberate: a source comment, the docs page, and a closed issue say why. Read as the project's own practice, the
  consistency argues against a contract the project wrote down.
- **(d)** "Name the strongest grounding and stop". The request rests on the operator's standard, which is not the
  project's document. Dropping it as a second grounding leaves the request with no reason the project's documented
  answer, a network policy, does not suffice.
- **(g)** An unverified shape banned from the report. `request-genre.md` allows a labeled sketch and the form's
  Proposal field asks for one with what was and was not tried; §7 sends an unverified shape to the hand-over note.
- **(a)** Question 7 asks for a shape backed by a document or a run. Nobody has run the design; the request should
  still stand, with the first objection (a network policy already covers it) answered.
- **(b)** Who is blocked and what it costs is a request slot, and the decision deletion test would cut it.

The padding: the full listing of 23 paths, the scanner's generic findings, the advisories in other products, the
internal review ID, and the private hostnames and addresses in the transcripts.

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

1. **The task comes first** (request genre, the API deletion test). The Problem field opens with what the operator
   cannot do: run Tallyqueue with every management endpoint authenticated while the liveness probe still works.
   `probe_addr`, `/livez`, and any other proposed API appear only after that. The title names the capability.
1. **The project's reason is acknowledged** (d). The request cites the source comment, the docs sentence, or #412 as a
   deliberate exception, and does not argue that `/healthz` is inconsistent with the other paths as if that were the
   project's contract.
1. **The operator's standard is the requirement, kept and attributed** (d). SEC-STD-014 §3.2 is quoted or paraphrased
   and said to be the operator's standard, not the project's; leaving out its internal identifier is a redaction the
   person filing may choose. §3.4 answers #412's network-policy advice, and §4.1 rules out a token in the probe headers;
   that answer is the first objection of question 7, met.
1. **The leak is shown, not described** (question 5). The `/healthz` response is pasted as a transcript with the
   version and the store host in it, the private hostname and address substituted and said to be.
1. **The sketch is allowed and labeled** (g, a). A proposal such as `management.probe_addr` sits in the Proposal
   field as one possible shape, separated from the requirement and marked as not implemented or tested. A sketch
   presented as working fails. No sketch at all passes only if the note says why it was left out.
1. **The prior issues are placed.** #977 is named with the difference (it hides fields; this asks for an
   authenticated management port), and #412 is cited as closed with what this request adds since.
1. **Alternatives sit in their slot with why each was ruled out** (request genre): the network policy, the header
   token, the exec probe, the data port's `/ping`.
1. **Who is blocked is said** (b). The production rollout waits on the standard, with the exception's end date.
1. **Nothing is there only because it is true.** The body carries none of: the 23-path listing (one sentence that
   every other path returned 401 is enough), the scanner findings, the advisories in other products, SECREV-2291, the
   real store hostname or node address.
1. **The prose is short.** Words outside code blocks: read the result sentence by sentence past 300.

Checks 2 to 6 and 9 can be counted, from this directory, with the model's directory as the argument. Every "present"
marker should print `True`, every "absent" marker `False`, and at most two `/admin/` paths should be named; whether
the reason is acknowledged or argued against still needs a reading.

```bash
python3 - claude-opus-5-5 <<'EOF'
import re, sys
text = open(f'{sys.argv[1]}/result.md').read()
prose = re.sub(r'```.*?```', '', text, flags=re.S)
print('prose words:', len(prose.split()), '(read sentence by sentence past 300)')
print('/admin/ paths named (expect <= 2):', len(set(re.findall(r'/admin/[\w/-]+', text))))
print('sketch marked untested (expect True):',
      bool(re.search(r'untested|not (been )?(implemented|built|tested|tried)', text, re.I)))
for marker in ['#412', '#977', '"version":"2.3.1"']:
    print(f'{marker!r} present (expect True):', marker in text)
for marker in ['pellham.net', '10.20.4.17', 'X-Content-Type-Options', 'advisor', 'CVE', 'SECREV']:
    print(f'{marker!r} absent (expect False):', marker in text)
EOF
```
