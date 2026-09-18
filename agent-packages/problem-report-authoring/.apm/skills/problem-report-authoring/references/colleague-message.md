# The short form: telling a colleague

Open this when the artifact is a chat message to someone who shares the codebase, not a filed
report. The goal-not-the-step rule and the expected-behavior test apply unchanged, and so does the
rule against writing a step you did not execute. The symptom-first rule holds for the first line:
the ask and the symptom open the message. The analysis rules relax after that line: a colleague who
shares the code often wants your theory right after the symptom, ahead of the steps, and what still
holds is that it is marked as a guess and that the message says what you saw independently of it.
The reproducer applies as the command and its output, without packaging it as a project or reducing
it. What lapses is everything that presupposes a tracker or a form: the duplicate search, the routing
lookup, the form lookup, and the project's reproducer oracle. Shared context may be assumed, and the
message is a few lines long.

## The four rules

- **Put the ask in the first message.** A greeting alone buys a round trip and a wait. Send the
  question, the symptom, and what you need in one message.
- **Say what you already ruled out, and how.** This is the half that makes a short message useful. It
  tells the reader where not to look and shows what your evidence actually covers. It is also the
  antidote to the trap where you describe your attempted fix instead of the outcome you cannot reach:
  the ruled-out list is where an attempt belongs.
- **Name shared artifacts by identifiers that resolve.** A branch, a commit, a file, a symbol, a test
  name, and the ref they exist at. A colleague reads your message inside the repository; anything they
  cannot grep costs them a question.
- **Say what you want back.** A decision, a pointer, or a review. A message that describes a situation
  and stops has asked for nothing, and the reader has to guess whether it is theirs.

## What may be dropped, and what may not

| Drop | Keep |
| --- | --- |
| The project's vocabulary explained | The exact error text |
| The full environment | The version or branch, when it is not the obvious one |
| The template's field names | The literal you expect and the literal you got |
| Background you both lived through | What you already ruled out |

## The escalation

Where the answer turns out to matter beyond the conversation, the message becomes the first draft of a
filed report, and everything in the skill applies to it: the ownership check, the currency check, the
expected-behavior test, and a reproducer someone can run.
