# french-developer-style : recherche

> English version: [README.md](README.md).

Pipeline éditorial en trois phases qui a produit le paquet APM `french-developer-style`. Le paquet lui-même
se trouve sous [`agent-packages/french-developer-style/`](../../agent-packages/french-developer-style/) ;
ce dossier est le journal de bord qui l’accompagne.

## Méthode

| Phase | Artefacts | Ce qui s’est passé |
| --- | --- | --- |
| Phase 1 : prospection large | `phase1_prompt.md`, `phase1_result.md` | Un prompt de recherche profonde recense les sources de style candidates pour la prose française orientée logiciel. Économique, large, sans synthèse. Conclusion : aucune compétence LLM française toute prête ne cible le texte développeur ; la synthèse est nécessaire. |
| Phase 2 : évaluation approfondie | `phase2_prompt.md`, `phase2_result.md` | La liste courte est réévaluée selon la couverture, l’adéquation fr-FR / fr-CA, le recoupement avec un catalogue de tics LLM, le risque de faux positifs sur le texte technique et les contraintes de licence. Conclusion : combiner le guide francophone de Mozilla, le guide de localisation Microsoft fr-FR (paraphrasé uniquement), les ressources du Bureau de la traduction et de la Vitrine linguistique de l’OQLF pour fr-CA, CLDR / ICU MessageFormat / Mozilla Fluent pour la sécurité des placeholders, le Lexique des règles typographiques de l’Imprimerie nationale pour la typographie, et une checklist de tics LLM façon Boileau pour l’inspiration structurelle. |
| Phase 3 : synthèse | `phase3_prompt.md` → [`SKILL.md`](../../agent-packages/french-developer-style/.apm/skills/french-developer-style/SKILL.md) | La compétence, les modules, les références et le pack Vale de démarrage sont assemblés à partir des conclusions de la phase 2. La copie de référence reste dans le paquet et n’est pas dupliquée ici. |

Découper le travail en deux phases d’évaluation garde l’évaluation approfondie peu coûteuse en pré-filtrant
les candidats, et conserve une liste courte réutilisable si le brief change plus tard.

## Fichiers

```text
phase1_prompt.md, phase1_result.md     liste courte des sources de style
phase2_prompt.md, phase2_result.md     évaluation approfondie, décision de synthèse
phase3_prompt.md                       prompt qui a assemblé la compétence
```

La sortie de la phase 3 vit dans le paquet APM, pas ici, pour éviter la divergence. Les fichiers de ce
dossier restent figés comme journal de bord ; éditez la compétence à son
[emplacement canonique](../../agent-packages/french-developer-style/.apm/skills/french-developer-style/SKILL.md).

## Historique des noms

`phase2_result.md` mentionne une fois `fr-tech-prose/` comme nom de dossier de travail pendant la recherche.
L’identifiant canonique est `french-developer-style`.

Le suffixe `-prose` a été abandonné pour la même raison que dans les paquets jumeaux anglais et russes : les
routeurs de compétence et les lecteurs traitaient `prose` comme un indice que la compétence ne s’applique
qu’au texte long (pages README, design docs, descriptions de PR de plusieurs paragraphes) et la sautaient
pour les messages d’erreur d’une ligne, les libellés de bouton de trois mots et les `msgstr` courts dans les
fichiers `.po`. La compétence s’applique au texte français orienté développeur quelle que soit sa longueur ;
le nouveau nom le reflète.

Si vous rejouez les prompts en phases, traitez toute référence résiduelle à `fr-tech-prose` ou
`french-prose-style` comme un artefact de l’exécution initiale et substituez `french-developer-style` dans
le nouveau résultat.

## Stratégie de locale

La phase 2 a tranché sur un paquet unique avec **fr-FR par défaut** et **fr-CA en mode explicite**, plutôt
que sur deux paquets `fr-FR` et `fr-CA` distincts. La justification :

- la plupart des règles éditoriales (voix, tics LLM, diagnostic d’anglicismes, patron des messages d’erreur,
  sécurité des placeholders) sont communes aux deux variantes ;
- les différences se concentrent dans une courte table de terminologie (`courriel`, `clavardage`, `pourriel`,
  `magasiner`, `balado`) et une fine couche de choix de registre (`ouvrir une session` au lieu de
  `se connecter`) ;
- maintenir deux paquets aurait doublé la surface éditoriale pour une fraction de contenu unique.

fr-BE et fr-CH n’ont pas de module dédié : repli sur fr-FR. `septante`, `huitante` et `nonante` ne sont
introduits que si le dépôt les utilise déjà.

## Réutilisation pour une autre langue

Le pipeline est neutre vis-à-vis de la langue : la prospection, l’évaluation et la synthèse ne dépendent pas
de la langue cible. La plupart des règles éditoriales survivent à un changement de langue ; le travail se
concentre sur les sources de style, la typographie, l’orthographe, la terminologie et la stratégie de mode
de locale.

1. Utilisez `phase1_prompt.md` et `phase2_prompt.md` comme gabarit. Échangez la langue cible, les guides de
   localisation, la langue du catalogue de tics LLM et les candidats sources ; la structure du prompt reste.
1. Relisez la table des candidats de la phase 2. Ne rejouez la phase 2 en entier que si la nouvelle langue
   dispose d’une source absente de la liste courte française (par exemple un organisme terminologique
   national équivalent à l’OQLF ou à l’Académie française).
1. Rejouez la phase 3 avec la nouvelle locale par défaut et substituez les sections sur la typographie
   (guillemets, tirets, espaces insécables, capitales accentuées), les règles de placeholder (catégories de
   pluriel CLDR pour la locale cible) et le diagnostic d’anglicismes. Conservez l’avertissement de licence
   sur les guides de style propriétaires : il s’applique à la plupart des guides nationaux de localisation.
