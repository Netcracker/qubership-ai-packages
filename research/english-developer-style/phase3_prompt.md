Create a compact Claude/agent `SKILL.md` for English developer-facing prose.

Use the @phase2_result.md research report as the main source.

Goal:
- British-English-first developer documentation prose.
- Primary use: editing/rewrite of LLM-generated drafts.
- Secondary use: authoring new docs, comments, PR descriptions, commits, changelog entries, error messages, and logs.
- Optimize for clarity, precision, maintainability, and natural technical English.
- Do not optimize for AI-detector evasion.

Requirements:
- Produce a complete `SKILL.md` with YAML frontmatter.
- Keep it around 1400–1800 words.
- Structure it as:
  1. When to apply
  2. Dialect policy
  3. Voice and tone
  4. Sentence and paragraph craft
  5. Punctuation and AI-tell avoidance
  6. Hedging and certainty
  7. Domain modules:
     - docs / README
     - Javadoc / docstrings / comments
     - commit messages
     - PR descriptions
     - changelog / release notes
     - error and log messages
  8. Final pass checklist
  9. When to break the rules

Source priorities:
- Google Developer Documentation Style Guide as the base voice.
- Microsoft Writing Style Guide for global English, modifier stacks, inclusive language.
- Wikipedia Signs of AI writing for LLM prose tells, but do not turn it into a ban list.
- GitLab Documentation Style Guide / Vale rules for self-referential prose, future tense, currently, sentence length, and dialect handling.
- Atlassian content guidance for error/warning messages.
- Conventional Commits for commit structure.
- GOV.UK only for British-English spelling/plain-English defaults, not for its no-contractions rule.

Important:
- Use short rules.
- Include a few compact before/after examples.
- Prefer judgement-based guidance over huge word lists.
- Mention that mechanical checks such as dialect spelling, terminology, inclusive-language substitutions, and commit-message regex should live in Vale/textlint/commitlint, not in the skill body.
