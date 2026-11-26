---
name: agent-instruction-authoring
description: >-
  Load before writing, editing, fixing, or reviewing text an AI agent will follow: a SKILL.md, an AGENTS.md or
  CLAUDE.md, a rules or instructions file, an agent persona, a review checklist, or a brief for a subagent or another
  model that a skill, script, or workflow keeps for reuse. Load it above all when a case, an eval run, or a user
  reports a bad output and you are about to change the skill or instruction that produced it, before the first line
  of the fix: that is where narrow patches enter. Also load it to review such a change in a diff. Governs what the
  instructions say, in any harness: rules that hold for a class of situations, the condition under which each rule
  does not apply, where a rule lives, and how to tell a general rule from a patch for one case. Package layout,
  frontmatter, and installation belong to apm-authoring; wording belongs to the developer-style skill of the language
  the text is written in.
---

# Authoring agent instructions

An instruction is read by an agent in a situation its writer never saw. The agent treats every sentence as an order and
applies it wherever the words match. The rules below keep an instruction general enough to help in that situation and
bounded enough to stay quiet where it does not apply. They govern writing a new instruction, editing one, and reviewing
a diff of one. Text that a person reads and no agent follows, such as a documentation page or a commit message, is out
of scope.

## 1. Write only what changes what the agent does

Every sentence of an instruction enters the agent's context whenever the instruction does: a root `AGENTS.md` or
`CLAUDE.md` on every task, a scoped instruction file on every task it applies to, a skill on every task that loads it, a
brief on every call, whether or not that task needs the sentence. A sentence earns that place only where an agent
without it would act differently: a convention of the project, an order of steps the agent cannot infer, a failure that
looks fine in the output. The agent already knows what its field has published: the vocabulary, such as "an idempotent
request gives the same result when sent twice", and the standard procedures of the field's tools, such as adding a
dependency with the build tool. A sentence that states them changes nothing the agent does and stays out, unless the
project uses the term or the procedure in another way, because there the agent's prior is wrong. Any other sentence goes
through the check of rule 8: a clause that gives the same output with and without it, on the inputs where its condition
holds, is noise. Leave it out, and delete one already there.

## 2. Write for a class of situations

Each sentence has to hold for a class of situations, not only for the input in front of the writer, because the agent
applies it to inputs nobody tested. An example shows one member of the class, and one example per rule is usually
enough. Across the skill, draw the examples from unrelated domains, such as a database migration in one rule and a
translation file in the next, so that the agent can tell each rule from the details of its example. Examples from one
repository or one domain teach the agent that the rules are about that domain. A skill that covers one domain by design,
such as the usage guide of a library, takes its examples from that domain, and spreads them across the different inputs
the skill serves: two calls that fail in different ways, not one call twice.

## 3. Name the class before fixing a failed case

When a case, an eval run, or a user shows a bad output, write down the class of the failure before editing: what the
agent did wrong, in words that also describe other inputs. "The commit body guessed at a cause it had not verified" is a
class; "the body in case 14 said *probably a race*" is an instance. Then search the skill for the rule that already
governs that class. Where one exists, sharpen it, move it to the place the agent reads at that moment, or delete the
text that contradicts it: a new rule beside the old one leaves the agent two rules to reconcile. Changing or deleting
text is the default fix, and each added line needs a reason why no existing rule could carry it.

A failure is not always the skill's. A check that grades the wrong thing, a broken harness, or a single run that
ignored a clear rule is fixed in the check, the harness, or with more runs, and the skill text stays as it is.

## 4. Give every rule its boundary

An agent applies "do X" to every input its words fit, including inputs where X is noise. Each "do X" therefore states
when X is not needed: the input on which the item is absent, or the test that tells. "Name the rollback step of the
migration" becomes "Name the rollback step; a migration that only adds a nullable column needs none." A rule that holds
on every input, such as a format a parser requires, needs no boundary.

## 5. Redraw a rule that needs a third exception

Each "except" marks an input the rule's wording got wrong. A third one shows that the rule is drawn along the wrong
line: find the condition that separates all the cases at once and state that condition instead. "Translate every
string, except placeholders, except product names, except glossary terms" becomes "Translate the text a user reads, and
leave what a program matches or a glossary fixes." An enumeration that is the content itself, such as the supported
versions or the reserved words, is a list, not a chain of exceptions.

## 6. Keep the case out of the text

Case names, check numbers, ticket numbers, and identifiers from one repository belong in the record of the case, which
lives outside the installed skill, not in the skill text. In the skill they match the rule to one input and mean
nothing to an agent in another repository. An identifier the agent meets in every repository the skill serves, such as a
command-line flag, a file name a tool requires, or a section of a standard, belongs in the text. An example in the skill
does not reproduce the input of a case either: a case whose input the skill quotes tests whether the agent recognizes
the example, not whether it follows the rule.

## 7. State each rule once

A rule lives in one section of the skill; any other place that needs it cites it by name or number and does not restate
its condition. A restated rule drifts: the next fix edits one copy, and the agent then reads two rules that disagree.
Before adding a sentence, search the skill for its key words. Before writing a prohibition, "never X" or "no other Y",
also search for the rules that produce X or Y: a rule "never log a request body" contradicts a debugging rule that dumps
whole requests, and the two are reconciled in the same edit. The frontmatter description and a final checklist name a
rule to make the agent load or run it, and that naming is a citation.

## 8. Check a change where it should not fire

Before keeping a change to a rule, check it against two inputs besides the one that prompted it: one from another domain
the skill serves (in a skill about one domain, another kind of input), where the rule has to fire and still make sense,
and one where it has to stay quiet. A check on the motivating input alone passes any rule that matches that case,
including one that fires on every input. Where the skill has regression cases, run the change on them, and add the quiet
input to them so the next change is checked against it too; with only a few runs per model, allow for noise before
calling a difference real. Where it has none, such as a new `CLAUDE.md`, read each input and decide what an agent would
do with the rule and without it. A rewrite that drops an example quoting a case's input (rule 6) may pass fewer of that
case's checks, and that alone is not a regression: judge the rewrite on the cases from other domains or other kinds of
input. A change that rewords a rule without changing what it asks needs no check.

## 9. Review a change without the case

A change prompted by a bad output goes to a fresh reviewer, an agent or a person, who gets the changed instruction text
alone: not the case, and nothing that names it, such as the case's records and results, the commit message, or the
description of the change. For each added or changed sentence, the reviewer names the class of situations it addresses
and two inputs of the skill that it applies to. The two inputs differ from each other, and both lie inside the skill's
scope, because any sentence fits some domain. The reviewer does not know which input failed, so it may name that input
again; the author, who knows, discards such an input and asks for another. A sentence left without its class, or without
two such inputs, is a patch: take it back to rule 3. So is a sentence that restates a rule the skill already has (rule
7) or gives one its third exception (rule 5); a sentence that gives a rule its missing boundary (rule 4) is a fix. The
reviewer does not see the case, because with the case in view every patch looks justified. A reviewer's own suggestion
is a new sentence too: before the author takes it as written, it goes through the same test, put to a reviewer who has
seen neither the case nor the reason for the suggestion. After several rounds of review, re-read the whole section:
fixes that each look reasonable can add up to one sentence per failed case. A deleted sentence, or one that only moves,
needs no class.
