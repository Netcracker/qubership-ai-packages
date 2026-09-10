# The request genre

Open this when the artifact is a feature or change request rather than a defect report. Most of the
skill still applies. What changes is the opening, the slots a defect report does not have, and
what becomes of three rules a defect report owes. There is no reproducer of the behavior you are
asking for, because it does not exist; every claim about today's behavior still carries its
transcript (question 5 of the skill's expected-behavior test), and a demonstration of what the
current release does is usually the strongest section of a request. The reproduction on a supported
version is replaced by confirming that the current release does not already do this, and that
nobody has asked for it before. Ownership does not lapse: where the behavior sits between two
projects, say which one owns the contract and why it is the right addressee. Only the method
changes, because there is no failing run to bisect, so the argument comes from the contract rather
than from a command sequence.

## The opening is inverted

A defect report opens with what broke. A request opens with what you could not do. A project's
feature form can make expected behavior its first required field while leaving current behavior
optional; the form wins on order, and the first sentence still names the task. State the task you
could not complete before naming any construct the project lacks.

*Test (the API deletion test):* remove every sentence that names your proposed API. If the remaining
text no longer states a problem, you have written a patch request with a preamble.

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
  explicit statement of what you searched. Some processes make this a required field.
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

The grounding order in the skill applies here too, and bites harder. A request grounded in "another
product does it this way" or in personal preference is the shape maintainers close. Ground it in a
task the project's own documentation says it supports, in an error the project itself raises, or in
users who hit the same wall.

## A request in a team's own backlog

The forms and guides the skill reads in step 1 rarely exist there; what stands in for them is in
`project-conventions.md`. The slots above still apply, and the acceptance criterion and the
non-goals are the two a backlog item most often lacks.

## What the request does not owe, and the one ask that looks like it

Priority, severity, a milestone, an estimate, or a design. Those are the project's, and offering them
reads as scope you have already claimed. A backport is different: where you need the change on a
maintenance line, say which line and why, with evidence that the line still takes changes. That is
an ask with a grounding, not a milestone you have set.
