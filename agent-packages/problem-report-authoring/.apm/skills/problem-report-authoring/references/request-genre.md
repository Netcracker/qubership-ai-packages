# The request genre

Open this when the artifact is a feature or change request rather than a defect report. Most of the
skill still applies. What changes is the opening, the slots a defect report does not have, and what
becomes of the rules a defect report owes. There is no reproducer of the behavior you are asking
for, because it does not exist; every claim about today's behavior still carries its transcript or
the document it rests on (question 5 of the skill's expected-behavior test), and a demonstration of
what the current release does is usually the strongest section of a request. The reproduction on a
supported version is replaced by confirming that the current release does not already do this, and
the duplicate search by finding whether someone asked before, which the prior-proposals slot below
carries. Ownership does not lapse: where the behavior sits between two projects, say which one owns
the contract and why it is the right addressee. Only the method changes, because there is no failing
run to bisect, so the argument comes from the contract rather than from a command sequence.

## The opening is inverted

A defect report opens with what broke. A request opens with what you could not do. A project's
feature form can make expected behavior or a proposed solution its first required field while
leaving current behavior optional. The form wins on order and on meaning: that field carries the
solution, marked as one possible shape, and the task you could not complete opens the first field
whose label admits it, such as context, motivation, or a description. Where no field does, the task
is the first sentence of the solution field, before the solution. Where the solution field comes
first and a later field takes the problem, the solution field opens with the task in one sentence
and the later field states it in full; the one-line opening is not a duplicate. The document's order
is the form's, and what the rule asks is that a reader meets the task before any construct the
project lacks.

*Test (the API deletion test):* remove every sentence that names your proposed API. If the remaining
text no longer states a problem, you have written a patch request with a preamble.

The title names the task or the capability, not the API: "no way to limit a retry by elapsed time"
rather than "add `maxElapsed` to `RetryPolicy`". Where you have a patch ready, say so in one line at
the end; a maintainer decides whether to ask for it, and the request has to stand without it.

## The slots

- **The problem.** A task you could not complete, in your own vocabulary. Not "the API lacks X".
- **Who else is blocked, and what it costs.** Both directions: the cost of doing it and the cost of
  leaving it undone. Name a party other than yourself, or say explicitly that you are the only known
  case. A maintainer's first question is how far the problem extends.
- **The acceptance criterion: how anyone will know it worked.** One sentence that could become a
  test or a measurement. Phrasing it as a question the project can answer later beats any ritual
  template.
- **What is out of scope.** A non-goals sentence keeps the discussion from expanding into the change
  you did not ask for. Maintainers use it to bound the review.
- **Whether it has been proposed before, and how yours differs.** A link to the prior discussion, or an
  explicit statement of what you searched. This is the slot §4 of the skill sends the query to; some
  processes make it a required field.
- **Alternatives, including your workaround.** In a slot of their own below the problem statement,
  subordinate, and stated with why each was ruled out. Ruling something out is information about your
  requirements; leading with it is a frame that undercuts the request. One kind moves: a setting you
  tried that does **not** solve the problem is a negative result rather than an alternative, and it
  belongs with the problem statement, under a heading or in a sentence that says it does not fix it,
  as §3 of the skill says.
- **A sketch, optional and labeled.** A mock-up, a snippet, or before-and-after code helps a
  maintainer see the shape you mean. It sits below the problem statement and is marked as one possible
  shape, not as the requirement. Separate the requirement from the rendering explicitly: say which
  part you need and which part is the project's to choose.

## Grounding, for a request

The grounding order in the skill applies here too, and it costs more here. A request grounded only
in "another product does it this way" or in personal preference is the shape maintainers close.
Ground it in a task the project's own documentation says it supports, in an error the project itself
raises, or in users who hit the same wall. A genuinely new need has no documented promise behind it,
and that does not disqualify it: the grounding is then the task, who has it, and what it costs them
today, stated as such. Evidence of a defect and justification for an improvement are different
things; a request does not borrow the language of a defect report to look stronger.

## A request in a team's own backlog

The forms and guides the skill reads in step 2 rarely exist there; what stands in for them is in
`project-conventions.md`. The slots above still apply, and the acceptance criterion and the
non-goals are the two a backlog item most often lacks.

## What the request does not owe, and the backport ask

Priority, severity, a milestone, an estimate, or a design, on a project's own tracker. Those are the
project's, and offering them is read as scope you have already claimed. Two channels differ: on a
vendor's support form severity is a field the requester sets (`question-and-support-ticket.md`), and
in a team's own backlog priority is the reporter's where the team's process says so
(`project-conventions.md`). A backport is different: where you need the change on a maintenance
line, say which line and why, with evidence that the line still takes changes. That is an ask with a
grounding, not a milestone you have set.
