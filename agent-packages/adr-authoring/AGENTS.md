# Editing the adr-authoring package

These are instructions for changing the skill under `.apm/skills/adr-authoring/`, not for using it to write a record.

## Check an edit against every reader

A record the skill writes has four readers:

- the approver, who decides whether the decision is right;
- the maintainer, who asks later why the code is this way;
- an agent that writes code under the record, and needs to know what the code must do and how to tell that it does;
- the checker, an agent or a person who checks a change against the record, and needs one verdict for each
  requirement.

An edit that helps one reader and costs another is a regression, unless the pull request names the cost and says why it
is worth paying.

## Check an edit against every kind of decision

Before an edit that changes what a record says or how a rule is shaped, check the new text against each of these kinds,
by reading where no case covers one:

- the behavior of a service: a protocol, an error response, a limit, a retry;
- the choice of a pattern or a structure, such as microservices or event sourcing;
- the choice of a technology, a library, or a tool;
- a structural invariant, such as which module may depend on which;
- a persisted format, a schema, or a published interface;
- a cross-cutting requirement: logging, security, performance, a supported platform version;
- a process decision, such as how dependencies are updated or how a release is cut;
- a decision that constrains no code.

For each kind, a rule written in the shape the skill prescribes has to be checkable by the means that kind is checked
with: a request and its response, a build, a linter, an architecture test, or a reviewer.

- **A rule drawn from one case states the condition under which it holds**: the kind of decision, the reader, or the
  repository it applies to.
- **A worked example is one instance, not the rule.** Where the skill shows a rule on a token or a host, the rule's text
  still tells the writer what to do for a library choice or a module boundary.
- **A new case goes to a kind of decision that the cases do not cover yet**, where the edit rests on that kind.

## Keep the instructions consistent

- **An edit contradicts no other instruction of the skill.** List the instructions that govern what the edited one
  governs: a status, a section, a rule, or a change. Read each pair as an agent that follows both literally, and resolve
  a contradiction in the text.
- **An instruction to an agent other than the writer names how it reaches that agent.** The skill loads when a task is
  about a record. An agent that writes code under a record has no such task, so a rule meant for it has no effect unless
  a trigger, a file that agent reads, or another skill carries it there.
- **A rule moves in all of its places in the same change.** A rule can sit in a section body, in the template, in the
  reading guide that a repository copies, in the frontmatter description, in the trigger under `.apm/instructions/`, in
  the package `README.md`, and in the bold name other sections cite it by. Search for the rule's own words across all of
  them before editing. The `Implements` and `Defers` trailers also sit in `change-description-authoring`, and an edit to
  them here moves there in the same change.
