# Axis: formats

Can the people who write a configuration or data format the change adds or reshapes fill it in correctly, and does a
mistake in it fail loudly? The readers are the users who write the format by hand or through a chart, the operators who
run it in production and need its effect to be predictable, and the agents asked to edit it. Breaks of a format that a
release already shipped, and how readers of two releases meet one file, belong to compatibility; the wording of an error
belongs to telemetry. This axis judges the shape of the format itself.

## Check

Write each finding as the entry a reader writes, what they expect from it, and what happens.

- **Understood from the format alone.** For each member, the schema or the page that documents the format states the
  meaning, the allowed values, the effect, and what absence means, without a rule number or a document the reader does
  not have. Fill the documented example in from scratch with only that schema or page in view, and list what you had to
  guess.
- **One concept per member.** A member that does two jobs, such as a `name` that also selects which database driver
  loads, splits in two. A member whose value another member already determines is a second way to say one thing that has
  to agree with the first. A property set on one entity that belongs to another, such as a timeout repeated on every URL
  of a host when the client applies one timeout per host, moves to that entity.
- **Alike things look alike.** One concept is expressed the same way everywhere: the discriminator of a kind, the
  casing of enum values, the type of a URL or a duration, a list or a map for the same kind of collection. Different
  concepts do not share a name. Compare with the format's siblings in the repository too, such as the chart values that
  write it.
- **Names predict the effect.** Read each name and enum value as a reader who has not seen the code would: a name whose
  plain reading promises more or less than the code does (a `dryRun` that still sends notifications, a `retries: 0`
  that means no limit) is a finding. Where an established tool names the same concept, the format uses that name, or
  the departure has a reason. *Vocabulary* covers words in comments and code members.
- **Collections keyed by identity.** A list whose items carry a unique name is a map in disguise: a map makes uniqueness
  structural, addresses an item by name in an error or a patch, and merges key by key in Helm values and JSON Merge
  Patch, where a list is replaced whole. A list stays where the order matters or an item has no identity.
- **Mistakes fail loudly.** List the mistakes a reader is likely to make (a misspelled member or file name, a wrong
  case, a trailing slash, an option set on the wrong entity, a file in the previous format) and what each does. A
  mistake that validation accepts and that leaves the system running but trusting, refusing, or skipping something
  silently is a finding; so is one that stops the system with no error naming the member at fault.
- **Room to grow.** Say what the format needs to add a second instance of a kind or a new kind, and whether that change
  can stay compatible. A file that a reader of another release can meet needs a way to tell a newer format from a typo,
  such as a `version` member.

## JSON Schema

Where the format has a JSON Schema, run a validator for the draft it declares on the documented examples and on the
mistakes above, and quote what it reports.

- An `if` that does not list the discriminator in its own `required` passes when the discriminator is missing, and
  every `then` applies: the reader gets errors from every branch, even where the discriminator is required at the top.
  `oneOf` over branches can report an error from the wrong branch, as Python `jsonschema` does; `if`/`then` on a
  discriminator that each `if` requires reports the right one.
- `false` schemas and `not` give messages that name no fix (`False schema does not allow …`). Leaving a member out of a
  branch under `additionalProperties: false` reports it by name.
- `additionalProperties: false` does not see members a sibling subschema declares; `unevaluatedProperties` does, from
  draft 2019-09, and a draft-07 validator, such as Helm's before 3.19, ignores it.
- A `description` that promises a constraint the keywords do not enforce is a claim the format does not keep. Each
  member has a description; a member whose type does not show its allowed values also has an example; a `default`
  equals what the code applies. A JSON or YAML file that users edit directly allows a `$schema` member, so that editors
  find the schema.
- A schema that exists only in a document's prose drifts from the code that validates the files; a schema file that the
  code or a test loads stays true.

## Not a finding

A shape that a standard or the tool consuming the file fixes, such as a Kubernetes resource or an OpenID Connect
discovery document. A format that only a program writes and reads. A code change that leaves the serialized form
unchanged, such as a renamed field whose tag keeps its name.

## Severity

A likely mistake that validation accepts and that leaves the system silently trusting or refusing what the reader meant
otherwise is `major`, unless the description states and accepts it. A structure that has to change incompatibly for an
extension the description or the repository plans is `major`. A claim the format does not keep is `major`, as
`finding-rules.md` grades it. Other findings are `minor`; a casing or naming mismatch with no effect on behavior is a
`nit`.
