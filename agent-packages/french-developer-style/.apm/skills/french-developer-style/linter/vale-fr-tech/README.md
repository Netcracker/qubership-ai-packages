# vale-fr-tech — starter Vale package

Minimal Vale rules for French developer-facing text. The pack is deliberately small: Vale is best at
substitution, existence, and consistency checks against literal tokens or simple regex. It is not the right
tool for grammar, accord, or full typographic enforcement — pair this pack with **LanguageTool** (`fr`) or
**Grammalecte** for grammar, and a typography post-processor for non-breaking spaces.

## What this pack does

| Rule file | Type | What it catches |
| --- | --- | --- |
| [`Anglicisms.yml`](Anglicisms.yml) | substitution | High-confidence anglicisms with a single preferred French equivalent. |
| [`AITics.yml`](AITics.yml) | existence | Hedge-prone phrases and rhetorical fillers common in LLM drafts. Fired at `suggestion` level — review in batch, not every match. |
| [`Typography.yml`](Typography.yml) | existence | Unaccented capitals (`Etat`, `A propos`), ASCII triple-dot ellipsis, English-style straight-quoted French phrases. |
| [`Terms.yml`](Terms.yml) | substitution | Short list of terminology nudges. Override per project with a richer glossary. |

## What this pack does **not** do

A handful of rules are tempting but unreliable in Vale. They live here as documentation rather than as
shipped rules — wire them with a dedicated tool instead.

- **Non-breaking spaces before `; : ! ? %`.** Vale cannot reliably distinguish an NBSP (U+00A0) from a
  regular ASCII space in front of a punctuation mark across every file. Use a typography post-processor
  (`typograf`, `LanguageTool` rule sets, an editor formatter) or enforce it in the rendering pipeline.
- **Guillemets français around quoted phrases.** Detecting `"..."` reliably across code, prose, and JSON
  exceeds Vale’s scope. Run a markdown-aware formatter or a custom script.
- **Apostrophe typographique (`’` vs `'`)**. Same problem — too many legitimate ASCII apostrophes in code
  examples. Handle it in the editor or the publishing pipeline.
- **Full ICU / Fluent placeholder integrity.** Use `messageformat-validator`, `fluent-syntax`,
  `compare-locales`, or `msgfmt -c`. Vale cannot parse these formats.
- **Grammar and accord.** Hand it to LanguageTool (`fr`) or Grammalecte.
- **Sentence length.** Easy to add (`extends: occurrence` + max words), but very noisy on technical writing.
  Enable only if the project has a clear maximum.

## How to install

Copy the pack into your repository:

```sh
cp -R agent-packages/french-developer-style/.apm/skills/french-developer-style/linter/. .vale/
```

Then point your project’s `.vale.ini` at it:

```ini
StylesPath = .vale
MinAlertLevel = suggestion

[*.{md,adoc,markdown,mdx}]
BasedOnStyles = vale-fr-tech
```

Run Vale locally or in CI:

```sh
vale .
```

## How to tune for your project

- **Allowlist proper nouns.** `Typography.yml` flags any `\bEtat\b` — your project may have a product named
  `Etat` or contain proper nouns like `Eolian`. Add them to a `Vale.Vocab` file under
  `.vale/Vocab/Project/accept.txt`.
- **Disable rules that fight your glossary.** A fr-CA project may prefer `librairie` in some contexts —
  disable the matching `Terms.yml` swap there. The file-scoped `BasedOnStyles` directive in `.vale.ini`
  accepts per-rule toggles: `vale-fr-tech.Anglicisms = NO`.
- **Override per directory.** Use `[docs/legacy/*.md]` sections in your `.vale.ini` to soften rules on
  imported content you cannot rewrite right now.

## Locale switching

The pack does not auto-detect fr-FR vs fr-CA. Wire one of:

- a project-level `.vale.ini` per locale (`docs/fr-CA/.vale.ini` overrides the default);
- a CI matrix that runs `vale --config .vale.fr-CA.ini docs/fr-CA/`;
- a small additional rule file `Anglicisms.fr-CA.yml` that swaps `e-mail → courriel`, etc., enabled only on
  fr-CA paths.

## Licence

The rule files ship under the same licence as the rest of the package. Substitution targets are short
generic French equivalents — no proprietary style-guide text is reproduced. If you derive richer rules from
the Microsoft, Mozilla, or OQLF style guides, paraphrase and credit upstream.
