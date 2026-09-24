# The short form: telling a colleague

Open this when the artifact is a chat message to someone who shares the codebase, not a filed
report. Shared context may be assumed, and the message is a few lines long. The table says which
rules of the skill hold, which change shape, and which lapse; a rule not listed lapses.

| Rule | In a message to a colleague |
| --- | --- |
| Symptom first (§3) | Holds for the first line. In a shared repository a commit, a branch, or a symbol is shared vocabulary, so "main is red since abc123, run link" is a symptom, not internals |
| The goal, not only the step (§3) | Holds |
| Causal analysis marked with its confidence (§3) | Holds, and the analysis may come right after the symptom, ahead of the steps: a colleague who shares the code often wants the theory early. The message still says what you saw independently of it |
| Expected behavior (§5) | Reduced to one line each: the literal or relation you expect and what you got, where the symptom line does not say them already. "Checkout spins" says both. The seven questions are not run on a chat message |
| Evidence attributed, nothing invented (§6) | Holds. A CI run counts by its link; a step a colleague ran is theirs |
| Secrets removed, private names substituted (§6) | Secrets out: a token in a pasted log is a token in the chat history. Private names stay; the reader shares them |
| Failing output pasted as text (§6) | Holds for the error text; a screenshot may accompany it, never replace it |
| Reproducer (§6) | The command and its output where a command shows the failure, without packaging it as a project or reducing it; for something you saw on a screen, what you did and where |
| Summary first, no speculative consequences (§7) | Hold: the ask in the first message is the summary, and a consequence you did not observe stays out |
| Ownership and currency (§4) | Reduced to naming the branch or the build where it is not the obvious one |
| Duplicate search, routing, form lookup, the project's reproducer service | Lapse |

## The four rules

- **Put the ask in the first message.** A greeting alone costs a round trip and a wait. Send the
  question, the symptom, and what you need in one message. "Checkout spins for me on staging since
  this morning; can you check the payment service?" is complete: an observation, enough context to
  act, and an ask.
- **Say what you already ruled out, where you ruled anything out.** This is the half that makes a
  longer message useful: it tells the reader where not to look and shows what your evidence covers.
  It is also where an attempted fix belongs, rather than described in place of the outcome you
  cannot reach. A one-line notice that ruled out nothing says nothing here; do not invent a list.
- **Name shared artifacts by identifiers that resolve.** A branch, a commit, a file, a symbol, a test
  name, a run link, and the ref they exist at. A colleague reads your message inside the repository;
  anything they cannot grep costs them a question.
- **Say what you want back.** A decision, a pointer, a review, or a look at a service. A message that
  describes a situation and stops has asked for nothing, and the reader has to guess whether it is
  theirs. A post to a channel rather than to a person names who is asked, or says that it asks
  nothing and links the ticket it announces.

## What may be dropped, and what may not

| Drop | Keep |
| --- | --- |
| The project's vocabulary explained | The exact error text |
| The full environment | The version or branch, when it is not the obvious one |
| The template's field names | What you expect and what you got, one line each, where the symptom does not say them |
| Background you both lived through | What you already ruled out, where you did |

## The escalation

Where the answer turns out to matter beyond the conversation, the message becomes the first draft of a
filed report, and the rules that lapsed or were reduced here apply in full: the ownership and currency
checks, the duplicate search, the seven questions on the expected block, and a reproducer someone can
run.
