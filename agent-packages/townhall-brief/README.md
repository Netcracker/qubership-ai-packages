# townhall-brief

A skill that turns a team's material into a brief for a two-minute slot at a technical townhall. Hand the agent slides,
notes, a draft, a task export, a rehearsal transcript, or agent conversations for the period, and ask it to prepare
the townhall brief. The agent keeps what changes the work, plans, or decisions of other teams, and one line per large
piece of work that changes nothing for them.

The listeners are the head of the department and the leads of the neighboring teams. They know what each team does
but not how it works inside. The budget is at most 220 words, lists included, which is two minutes at 110 words per
minute. The speaker can name another audience, slot, or period, and the skill adjusts the budget to the slot.

## What it does

1. Groups the material into pieces of work and types each one: a one-off delivery, recurring work such as support or
   releases, a research spike, design, testing, infrastructure, or an incident. The type decides what can count as an
   effect on other teams: a delivery is judged by who can use it, recurring work by its deviation from the norm, an
   incident by its cause and what changed so it does not recur.
1. Decides the fate of each piece of work by one question: does it change anything in the work, plans, or decisions of
   a listener outside the team? If yes, it goes into the brief with the effect named. If no, but it took a noticeable
   share of the period, it stays as one line. Otherwise it goes into the list of what was left out.
1. Marks a piece of work whose type implies an effect the source does not state with `[?]` and a question to the
   speaker. It does not
   infer the effect, invent a request to the listeners, or add numbers the source does not contain.
1. Treats instructions found inside the material as data about the team's work, not as commands, and keeps secrets,
   environment names, and the names of people blamed for an incident out of the brief.

The skill judges volume and focus only. It does not assess whether the team works the right way. The rules, the table
of work types, the order in which sections are cut when the brief runs over, and the pre-delivery checklist are in
[SKILL.md](.apm/skills/townhall-brief/SKILL.md).

## Output

1. The brief, at most 220 words, in sections: highlights, where the time went, what is late or changes for others,
   what the team needs from the listeners, and topics for follow-up questions. Empty sections are omitted.
1. A table of the pieces of work left out, each with a one-line reason.
1. The `[?]` items with questions to the speaker.
1. The word count of the brief and the estimated speaking time.

The skill text is in Russian. The brief is written in the language the speaker will present in, Russian by default.
Product names and technical terms stay untranslated.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/townhall-brief
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/townhall-brief#<ref>
```

Replace `<ref>` with the release tag or commit SHA you want to pin.

Then run `apm install`. The skill deploys to the location your agent reads (`.agents/skills/`, `.claude/skills/`,
`.cursor/`, ...).

To install it from the marketplace into the user scope instead:

```sh
apm marketplace add Netcracker/qubership-ai-packages
apm install townhall-brief@qubership-ai-packages --target claude,codex,cursor -g
```
