---
name: french-developer-style
description: French technical-prose conventions for software documentation, README files, UI strings, error messages, logs, code comments, PR descriptions, changelog entries, and French localization. Use when writing, editing, translating, or reviewing French software-facing prose. Defaults to fr-FR, supports fr-CA mode, and focuses on clear natural French, technical precision, terminology consistency, and avoiding over-translated or LLM-like phrasing.
---

# Style français pour le texte développeur

Cette compétence s’applique à la prose française destinée à des développeurs ou à des utilisateurs de produits
logiciels : documentation et README, commentaires de code et docstrings, messages de commit, descriptions de PR,
changelog, chaînes d’interface, messages d’erreur et journaux, fichiers de localisation (`.po`, `.properties`, JSON
i18n, `.ftl`, `.arb`). La longueur ne compte pas : un `msgstr` d’une ligne, un commentaire `// FIXME : …` et un
README complet passent par la même grille de lecture.

L’objectif n’est ni le marketing, ni le SEO, ni l’évasion d’un détecteur d’IA. Il s’agit d’écrire un français clair,
naturel et techniquement précis, sans calques de l’anglais, sans tournures administratives et sans tics de modèle
de langage.

## 1. Quand appliquer cette compétence

Activez la compétence dès que la tâche concerne du texte français orienté logiciel, quel que soit son volume.

Actions déclenchantes :

- **Création** : nouvelles pages, README, commentaires, messages de commit, descriptions de PR, changelog, chaînes
  d’interface, messages d’erreur ou de journal.
- **Traduction et localisation** : depuis ou vers le français ; édition des fichiers `.po`, `.pot`, `.properties`,
  `.resx`, JSON i18n, Fluent, ARB.
- **Réécriture** : reprise d’un brouillon LLM avant commit (usage principal), retouche d’une prose humaine.
- **Relecture et vérification** : « vérifie la formulation », « est-ce naturel ? », « rends ça moins traduit »,
  « relis les messages d’erreur », « audite le changelog », « contrôle les docstrings par rapport au code ».

Pour les surfaces couvertes et les non-déclencheurs, voir le fichier d’instructions du paquet.

**Quand charger les modules et références** :

- chaînes UI, formulaires, plurals ICU, Fluent → [`modules/ui-strings.md`](modules/ui-strings.md) et
  [`references/icu-fluent-placeholders.md`](references/icu-fluent-placeholders.md) ;
- texte ciblant un public canadien ou québécois → [`modules/fr-ca-overrides.md`](modules/fr-ca-overrides.md) ;
- politique d’écriture inclusive demandée par le projet →
  [`modules/inclusive-writing.md`](modules/inclusive-writing.md) ;
- terminologie : vérifier [`references/glossary-fr.tsv`](references/glossary-fr.tsv) avant d’inventer une traduction ;
- doute sur la typographie → [`references/typography-cheatsheet.md`](references/typography-cheatsheet.md) ;
- doute sur le ton ou un calque LLM → [`references/ai-tics-checklist.md`](references/ai-tics-checklist.md).

## 2. Variante linguistique et registre

Par défaut : **fr-FR**, vouvoiement, présent de l’indicatif, registre technique sobre.

Passez en **fr-CA** quand l’une de ces conditions est vraie : l’utilisateur le demande explicitement ; un chemin
contient `fr_CA` ou `fr-CA` ; la configuration de locale liste `fr-CA` ; le texte voisin utilise déjà `courriel`,
`clavardage`, `pourriel`, `magasiner`, `balado` ; le dépôt cible un public canadien ou québécois. Détails dans
[`modules/fr-ca-overrides.md`](modules/fr-ca-overrides.md).

Pour fr-BE et fr-CH, suivez fr-FR sauf glossaire interne contraire. N’introduisez pas `septante`, `huitante` ou
`nonante` si rien ne les utilise déjà.

Tutoyez (`tu`) uniquement à la demande explicite de l’utilisateur ou si la voix du produit l’impose. Ne mélangez
jamais `tu` et `vous` dans un même texte.

## 3. Voix par défaut

- **Sobre, technique, sans emphase marketing.** Pas d’adjectifs vendeurs (« puissant », « robuste », « innovant »,
  « intuitif »), pas de points d’exclamation hors des journaux applicatifs.
- **Direct et précis.** Une idée par phrase, viser 20–25 mots. Sujet–verbe–complément ; on garde la voix passive
  quand l’acteur est inconnu ou sans intérêt.
- **Genré le moins possible.** Préférez une reformulation neutre à `connecté(e)` ou au point médian. Exemples :
  - Préférer : « La connexion est établie. »
  - Éviter quand possible : « Vous êtes connecté. » ou « Vous êtes connecté(e). »
- **Titres au substantif** quand le contenu est descriptif : `Configuration du cache` plutôt que
  `Configurer le cache`, sauf tutoriel franchement procédural.
- **Présent par défaut.** « Le gestionnaire réessaie trois fois », pas « réessaiera ».

## 4. Règles de réécriture des brouillons LLM

Les patrons ci-dessous ne sont pas interdits : ils sont des signaux. Trois ou quatre dans un même paragraphe et
celui-ci doit être réécrit.

- Connecteurs vides : `ainsi`, `de plus`, `par ailleurs`, `en outre`, `cependant`, `néanmoins`, `en effet`,
  `par conséquent`. Gardez-les seulement quand ils marquent une vraie relation logique.
- Préambules de signalement : `il est important de noter que`, `il convient de noter que`, `force est de constater`,
  `il est à noter que`. À supprimer presque toujours.
- Cadres élégants creux : `dans cette optique`, `à l’aune de`, `s’inscrit dans`, `joue un rôle clé`, `constitue`,
  `représente`. À remplacer par un verbe précis.
- `permet de` vide : `cette fonction permet de retourner X` → `cette fonction retourne X`. Gardez `permet de`
  uniquement s’il introduit une vraie capacité.
- Doublets synonymiques : `simple et intuitif`, `robuste et fiable`, `rapide et performant` → gardez un seul
  qualificatif, ou aucun.
- Triplets forcés : `rapide, efficace et fiable` → coupez.
- Parallélisme négatif : `Ce n’est pas X, c’est Y` → ne gardez que ce que vous affirmez vraiment.
- Verbes pseudo-formels : `effectuer une mise à jour` → `mettre à jour` ; `procéder à` → verbe direct ;
  `disposer de` → `avoir` ; `s’avérer` → `être`.
- Conclusion générique : `En conclusion, …` ; paragraphe final qui résume sans ajouter. Supprimez.
- Posture didactique : `Dans cet article, nous allons voir…`, `Comme nous l’avons mentionné…` → entrez dans le sujet.
- Liste de puces ouvertes en gras + deux-points pour chaque item, sans nécessité : la mise en forme `Terme : prose`
  n’a sa place que pour de vraies paires terme/définition.
- Catalogue détaillé : voir [`references/ai-tics-checklist.md`](references/ai-tics-checklist.md).

## 5. Anglicismes, faux amis et calques

Trois niveaux à distinguer.

**À corriger systématiquement** (anglicismes sémantiques) :

- `faire du sens` → `avoir du sens` ;
- `adresser un problème` → `traiter`, `résoudre`, `prendre en charge` ;
- `supporter X` au sens *to support* → `prendre en charge X`, `gérer X` ;
- `assumer` au sens *to assume* → `supposer` ;
- `définitivement` au sens *definitely* → `certainement`, `vraiment` ;
- `opportunité` au sens *occasion* → `occasion` ;
- `digital` au sens logiciel → `numérique` ;
- `basé sur` (calque structurel) → `fondé sur`, `reposant sur`, `à partir de` ;
- `en termes de` (souvent vide) → reformuler avec `pour`, `côté`, ou supprimer.

**À vérifier selon le contexte** :

- `librairie` → `bibliothèque` pour les bibliothèques de code, sauf si le projet utilise déjà `librairie`.
- `éventuellement` ne veut pas dire *eventually* : utiliser `peut-être`, `le cas échéant`, ou `finir par` selon le sens.
- `permet de` peut être correct s’il introduit une vraie capacité ; vide, à remplacer par un verbe.

**À laisser en anglais** sauf glossaire de projet contraire :

- `pull request`, `merge request`, `commit`, `branch`, `rebase`, `cherry-pick` ;
- `endpoint`, `framework`, `middleware`, `cache`, `debug`, `front-end`, `back-end`, `pipeline`, `runtime`, `linter`,
  `parser`, `tooling`.

Découpage régional (détails dans le module fr-CA) :

- fr-FR : `e-mail` ou `courriel` ; éviter `mél`. fr-CA : `courriel`.
- fr-FR : `spam`. fr-CA : `pourriel` si le style du projet le permet.
- fr-FR : `cookie`. fr-CA : `cookie` aussi ; `témoin` seulement si déjà utilisé.
- `login` (verbe) → `se connecter` ; fr-CA tolère `ouvrir une session`.
- `issue` → `ticket`, `problème`, ou `issue` selon le contexte GitHub/Jira.

Glossaire de démarrage : [`references/glossary-fr.tsv`](references/glossary-fr.tsv). Un glossaire de projet
existant prime toujours sur la compétence.

## 6. Typographie française à préserver

L’intention reste dans la compétence ; l’application mécanique revient aux outils (voir section 11).

- Espace insécable avant `;`, `:`, `!`, `?`, `%`, et entre le chiffre et son unité (`3 Go`, `10 ms`).
- Guillemets français en prose : `« … »`, avec espaces insécables à l’intérieur.
- Capitales accentuées : `À propos`, `État`, `Échec`, `Évolution`, `Île`. Jamais `A propos`.
- Tiret cadratin pour les incises, demi-cadratin pour les plages numériques (`pages 10–20`), trait d’union pour les
  mots composés (`base de données`, `clé en main`).
- Apostrophe typographique `’` en prose ; apostrophe droite `'` dans le code ou la syntaxe.

**Ne jamais appliquer la typographie française à l’intérieur de** :

- blocs de code, code inline, URL, chemins de fichier ;
- commandes CLI, variables d’environnement, drapeaux ;
- JSON, YAML, TOML (clés et valeurs), expressions régulières ;
- chaînes ICU MessageFormat, chaînes Fluent ;
- liens Markdown (cible), identifiants d’API.

Préservez les guillemets droits là où la syntaxe l’exige. Détails et exemples :
[`references/typography-cheatsheet.md`](references/typography-cheatsheet.md).

## 7. Chaînes UI et localisation

Boutons et actions de menu : **infinitif**, sans ponctuation finale.

- `Save` → `Enregistrer` ; `Delete` → `Supprimer` ; `Export` → `Exporter`.

Phrases complètes (confirmations, descriptions) : impératif ou indicatif, ponctuation finale normale.

- `This will overwrite your changes.` → `Cette action écrasera vos modifications.`
- `Are you sure you want to delete this file?` → `Voulez-vous vraiment supprimer ce fichier ?`

Titres de boîte de dialogue et de section : substantif, sans point.

- `Settings` → `Paramètres` ; `Cache configuration` → `Configuration du cache`.

Évitez :

- `Cliquez ici` ou `Cliquez pour …` sur les boutons ;
- `Oups !`, `Désolé`, points d’exclamation hors logs ;
- les possessifs calqués : `Contact your administrator` → `Contactez l’administrateur` plutôt que
  `Contactez votre administrateur` ; gardez le possessif s’il lève une vraie ambiguïté ;
- les titres en `-ing` rendus mot pour mot : `Configuring the cache` → `Configuration du cache`, pas
  `Configurant le cache`.

Pour le pluriel et les variables, voir [`modules/ui-strings.md`](modules/ui-strings.md) et
[`references/icu-fluent-placeholders.md`](references/icu-fluent-placeholders.md).

## 8. Erreurs et journaux

**Messages utilisateur** — patron :

1. ce qui a échoué ;
1. pourquoi, si la cause est connue et utile ;
1. ce que la personne peut faire.

Forme canonique : `Impossible de <action>. <Cause ou recours.>`

- Faible : `Une erreur est survenue.`
- Meilleur : `Impossible d’enregistrer le fichier. Vérifiez que vous disposez des droits d’écriture.`
- Faible : `Vous avez saisi une valeur incorrecte.`
- Meilleur : `La valeur n’est pas valide. Indiquez un port entre 1 et 65535.`

À proscrire : `Oups`, `Désolé`, excuses, blâme de l’utilisateur, traces de pile dans le message visible, formulations
floues du type `Erreur lors de l’opération`.

**Journaux développeur** : pas de vouvoiement, pas de politesse. Phrases techniques courtes, identifiants
structurés (`request_id`, `user_id`, `trace_id`) hors du texte. Le niveau (`INFO`, `WARN`, `ERROR`) doit coller au
ton.

## 9. Commentaires de code et documentation API

**Commentaires** : expliquez *pourquoi*, pas *quoi*. Un commentaire qui paraphrase la ligne suivante est à
supprimer. Mentionnez les invariants, les effets de bord, les pièges, les contournements de bug, les unités et la
sécurité des accès concurrents. N’écrivez pas un long commentaire pour décorer un nom déjà clair.

**Identifiants** : ne traduisez jamais les noms de fonctions, classes, variables, fichiers, drapeaux CLI, en-têtes
HTTP, variables d’environnement. En prose française, mettez-les en `code inline` et ne les déclinez pas
(`la fonction getUser`, pas `le getUser`).

**Docstrings (Javadoc / KDoc / TSDoc / docstrings Python / doc-comments Rust)** :

- première phrase courte au présent, à la troisième personne implicite : `Retourne l’identifiant de session.`
- ensuite : paramètres, valeur de retour, exceptions, conditions de version ;
- préservez les noms de paramètres et types exactement.

**Documentation API** : présent neutre, vocabulaire précis. Ne reformulez pas un terme technique pour faire
« plus naturel » si vous perdez la précision.

## 10. Messages de commit et descriptions de PR

**Message de commit** : suivez Conventional Commits, au format `type(scope): résumé`. Le résumé reste court
(≤ 72 caractères), sans point final, et garde un mode verbal cohérent dans tout le dépôt (souvent l’infinitif en
français : `ajouter`, `corriger`, `supprimer`). Après une ligne vide, le corps explique *pourquoi* le changement était
nécessaire et signale ce qui n’est pas évident : risque de migration, compromis de performance, incident lié.
Référencez les tickets par identifiant ; ne paraphrasez pas le diff.

**Description de PR** : trois sections courtes, dans cet ordre : **Pourquoi** (le problème ou la contrainte qui a imposé
le changement), **Quoi** (le changement, en un paragraphe ou une liste), **Comment vérifier** (commandes, captures, noms
de tests). Commencez par la motivation : le reste se lit à la lumière de la cause. Signalez explicitement les
ruptures de compatibilité, les migrations et le travail restant. Le relecteur ne devrait pas avoir à lire le diff pour
décider s’il doit s’y plonger.

## 11. Ce qui relève des linters ou du glossaire

La compétence porte le jugement. Les outils portent la mécanique.

À déléguer aux outils :

- orthographe, accords, doublons (LanguageTool fr, Grammalecte, Hunspell/Dicollecte) ;
- typographie : guillemets, espaces insécables, capitales accentuées (Vale, scripts spécifiques) ;
- terminologie produit et glossaire (Vale + [`references/glossary-fr.tsv`](references/glossary-fr.tsv)) ;
- intégrité des placeholders et des messages ICU/Fluent (scripts dédiés, jamais Vale) ;
- longueur de phrase et listes de mots interdits.

Pack Vale de démarrage : [`linter/`](linter/). Détails :
[`linter/vale-fr-tech/README.md`](linter/vale-fr-tech/README.md).

## 12. Checklist finale

À passer en quelques secondes avant le commit.

- Locale : fr-FR ou fr-CA cohérent dans tout le fichier ?
- Voix unique : `vous` partout, ou tournures impersonnelles, jamais les deux ?
- Phrases > 25 mots justifiées ?
- Connecteurs vides (`ainsi`, `de plus`, `par ailleurs`) supprimés ou justifiés ?
- Anglicismes (`faire du sens`, `adresser`, `supporter`, `basé sur`) traités ?
- Boutons à l’infinitif, sans point ?
- Possessifs calqués (`votre administrateur`) retirés quand sans ambiguïté ?
- Erreurs : `Impossible de … . <Cause ou recours.>` ?
- Identifiants et chemins en `code inline`, non traduits, non déclinés ?
- Placeholders intacts (`{name}`, `%s`, `{0}`, `{$count}`) ?
- Pluriel ICU/Fluent en `one` / `other` (pas de `zero/two/few/many` inventés) ?
- Typographie absente du code, des URL, du JSON, du YAML, des regex ?

## 13. Quand enfreindre une règle

Une règle qui dégrade le texte ne s’applique pas. En particulier :

- la voix passive est correcte quand l’acteur est inconnu ou sans intérêt ;
- une phrase longue est légitime quand la pensée l’est ;
- un connecteur (`cependant`, `en effet`) reste utile quand il marque une vraie articulation logique ;
- `permet de` est juste quand il introduit une capacité réelle ;
- le tutoiement et un ton plus chaleureux peuvent être imposés par la voix du produit ;
- un terme officiel (FranceTerme, OQLF) peut s’écarter de l’usage développeur réel : suivez l’usage du dépôt.

Choisissez l’exception consciemment, pour le lecteur. Glisser dans une habitude personnelle n’en est pas une.
