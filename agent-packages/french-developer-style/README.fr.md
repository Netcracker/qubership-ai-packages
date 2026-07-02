# french-developer-style

> English version: [README.md](README.md).

Recommandations de style pour le texte français orienté développeur, quelle que soit sa longueur : documentation
Markdown et README, commentaires de code et docstrings dans les fichiers source (`.go`, `.js`, `.ts`, `.py`,
`.java`, `.rs`, `.kt`, `.cs`, …), messages de commit, descriptions de PR, entrées de changelog, chaînes
d’interface, messages d’erreur et de journal, fichiers de localisation côté français (`.po`, `.properties`, JSON
i18n, `.ftl`, `.arb`). Un `msgstr` d’une ligne, un libellé de bouton de trois mots et un README de plusieurs
pages passent par la même grille de lecture.

La compétence se déclenche sur toute tâche qui touche un texte français orienté logiciel : écriture, réécriture,
traduction, localisation, relecture, vérification, audit, contrôle. Les verbes français (`écrire`, `réécrire`,
`traduire`, `relire`, `vérifier`, `rends ça plus naturel`) chargent aussi la compétence.

Le paquet encode les règles fondées sur le jugement éditorial — voix, structure, catalogue de tics LLM,
diagnostic d’anglicismes, intention typographique, patron des messages d’erreur, politique de locale — que les
linters ne peuvent pas appliquer de façon fiable. Les contrôles mécaniques (orthographe, accord, application
typographique, intégrité des placeholders ICU/Fluent, grammaire complète) reviennent à LanguageTool, Grammalecte,
des validateurs dédiés et le pack Vale de démarrage fourni sous
[`linter/`](.apm/skills/french-developer-style/linter/).

## Hors périmètre

- Marketing, SEO, argumentaires commerciaux, accroches produit.
- Fiction, journalisme, traduction littéraire.
- Évasion de détecteur d’IA ou outillage d’« humanisation » — la checklist des tics LLM est un filtre éditorial
  pour la clarté, pas un outil furtif.
- Français hors du périmètre logiciel (écrit académique, contrats juridiques, correspondance officielle avec
  l’administration).

## Locale par défaut et mode fr-CA

Locale par défaut : **fr-FR**, avec vouvoiement (`vous`), présent de l’indicatif, registre technique sobre et
titres au substantif (`Configuration du cache`, pas `Configurer le cache`).

Le mode **fr-CA** s’active dès qu’**une** des conditions suivantes est vraie :

- l’utilisateur demande explicitement du français canadien, du français québécois ou `fr-CA` ;
- un chemin de fichier contient `fr_CA`, `fr-CA`, `fr_CA.UTF-8` ou un marqueur de locale équivalent ;
- la configuration de locale (`languages`, `i18n.locales`, gettext, ICU) liste `fr-CA` ;
- le texte voisin utilise déjà `courriel`, `clavardage`, `pourriel`, `magasiner`, `balado` ;
- le dépôt cible le gouvernement fédéral canadien, le gouvernement du Québec ou un public canadien.

Pour fr-BE et fr-CH, la compétence suit fr-FR sauf glossaire interne contraire. `septante`, `huitante` et
`nonante` ne sont jamais introduits si rien ne les utilise déjà.

Quand le dépôt impose déjà une convention de locale et de terminologie, suivez le dépôt — ne le surchargez pas.

## Activation des modules

| Module | Chargement |
| --- | --- |
| [`modules/ui-strings.md`](.apm/skills/french-developer-style/modules/ui-strings.md) | Édition de boutons, libellés, placeholders, infobulles, messages de validation, confirmations, états vides, ICU MessageFormat, Mozilla Fluent. |
| [`modules/fr-ca-overrides.md`](.apm/skills/french-developer-style/modules/fr-ca-overrides.md) | Une des règles de détection fr-CA ci-dessus est satisfaite. |
| [`modules/inclusive-writing.md`](.apm/skills/french-developer-style/modules/inclusive-writing.md) | Demande explicite de l’utilisateur ou politique documentée du projet. **Désactivé par défaut.** |

Les modules s’ajoutent au `SKILL.md` principal, ils ne le remplacent pas.

## Fichiers de référence

| Fichier | Contenu |
| --- | --- |
| [`references/glossary-fr.tsv`](.apm/skills/french-developer-style/references/glossary-fr.tsv) | TSV de démarrage avec `term_en / fr-FR / fr-CA / leave_as_english / note`. Environ 150 entrées. |
| [`references/ai-tics-checklist.md`](.apm/skills/french-developer-style/references/ai-tics-checklist.md) | 30 patrons fréquents dans les brouillons LLM en français, avec consigne de réécriture. |
| [`references/typography-cheatsheet.md`](.apm/skills/french-developer-style/references/typography-cheatsheet.md) | Intention typographique française : espaces insécables, guillemets, capitales accentuées, tirets. Zones d’exclusion (code, syntaxe). |
| [`references/icu-fluent-placeholders.md`](.apm/skills/french-developer-style/references/icu-fluent-placeholders.md) | Catégories de pluriel CLDR pour le français, `select`, échappement de l’apostrophe en ICU, structure Fluent, éléments à ne pas traduire. |

Le glossaire est un point de départ. Un glossaire de projet prime toujours sur cette base. N’importez pas un
glossaire propriétaire verbatim : reformulez et créditez la source en amont quand vous reprenez du Microsoft,
du Mozilla ou de l’OQLF.

## Pack de linter

[`linter/`](.apm/skills/french-developer-style/linter/) fournit un pack Vale de démarrage
([`vale-fr-tech/`](.apm/skills/french-developer-style/linter/vale-fr-tech/)) qui couvre quelques substitutions,
des marqueurs de tics LLM et des indices typographiques. Le README du pack précise ce que Vale peut et ne peut
pas faire ici : n’attendez pas qu’il applique les espaces insécables, l’intégrité ICU/Fluent ou la grammaire.
Pairez avec LanguageTool (`fr`), Grammalecte et un post-processeur typographique.

## Installation

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/french-developer-style
```

Ou à la main dans `apm.yml` :

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/french-developer-style@<ref>
```

Remplacez `<ref>` par le tag de release, la branche ou le commit SHA à
épingler, par exemple `v1.0.0`.

Puis lancez `apm install` pour déployer la compétence et les sorties d’instructions générées.

## Exemples d’invocation

Demandes qui chargent la compétence :

- « Traduis ce README en français. »
- « Réécris les messages d’erreur de `errors_fr.po` pour qu’ils sonnent moins traduits. »
- « Localise ce flux d’interface en fr-CA. »
- « Relis les docstrings français de `lib/auth.py` : la formulation est-elle naturelle ? »
- « Vérifie les chaînes de `fr.json` et rends-les moins traduites. »
- « Audite les messages d’erreur du module de paiement. »

Les messages courts comptent : un `msgstr "…"` d’une ligne déclenche la même grille qu’un README complet.

## Limites connues

- Le paquet encode du jugement éditorial, pas une grammaire complète. Confiez la grammaire, l’accord,
  l’orthographe et l’application typographique à LanguageTool, Grammalecte et Hunspell/Dicollecte.
- Le pack Vale reste volontairement minimal. Un contrôle terminologique plus riche demande un glossaire de
  projet compilé à partir de `references/glossary-fr.tsv` et du vocabulaire du produit.
- fr-CA est un mode, pas un paquet séparé. Les différences se trouvent dans
  [`modules/fr-ca-overrides.md`](.apm/skills/french-developer-style/modules/fr-ca-overrides.md). fr-BE et
  fr-CH n’ont pas de module dédié : repli sur fr-FR.
- L’intégrité ICU/Fluent est décrite dans le fichier de référence mais n’est pas appliquée par le paquet.
  Branchez `messageformat-validator`, `fluent-syntax`, `msgfmt -c` ou `compare-locales` séparément.
- Le glossaire marque plusieurs termes comme `contextuel` (selon le projet). Considérez ces entrées comme un
  point de départ, pas comme une réponse finale.

## Avertissement de licence

La compétence emprunte sa structure au guide de style **Mozilla** (licence publique), au **Microsoft French
Localization Style Guide** (propriétaire — paraphrasé, jamais cité verbatim), aux ressources du **Bureau de la
traduction** et à la **Vitrine linguistique de l’OQLF** (consultables publiquement, utilisées comme référence
pour fr-CA), et à un catalogue de tics LLM de style Boileau (inspiration structurelle uniquement). Tous les
exemples du paquet sont originaux. N’insérez pas de texte de règle ou d’exemple traduit issu d’un guide
propriétaire dans cette compétence ou dans un pack de règles dérivé.

## Origine

Le paquet est issu d’un pipeline de recherche éditoriale comparable à celui des paquets
[`english-developer-style`](../english-developer-style/) et
[`russian-developer-style`](../russian-developer-style/). Les notes de recherche, prompts et résultats sont
sous [`research/french-developer-style/`](../../research/french-developer-style/) — utiles pour adapter la
compétence à une autre locale.

## Mise à jour

`apm outdated` signale les nouvelles versions, `apm deps update` met à niveau. Incrémentez la version dans
`apm.yml` quand le contrat change (nouveau module, renommage, nouvelle condition d’activation), pas à chaque
retouche de prose.
