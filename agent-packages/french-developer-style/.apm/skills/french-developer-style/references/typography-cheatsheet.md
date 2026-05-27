# Typographie française — aide-mémoire

Cet aide-mémoire condense les règles utiles en prose française. Les outils mécaniques (Vale, scripts de
typographie, traitement de texte) appliquent la plupart de ces règles automatiquement — utilisez-les. La
compétence retient seulement les règles que l’éditeur humain ou l’agent doivent garder en tête.

Toutes les règles ci-dessous **ne s’appliquent qu’à la prose**. Voir la section « Où ne jamais appliquer » à la
fin.

## Espaces insécables

L’espace insécable (`U+00A0`) ou l’espace fine insécable (`U+202F`) empêche le retour à la ligne et donne un
écart visuellement plus serré que l’espace normale.

| Avant | Espace ? | Exemple |
| --- | --- | --- |
| `;` | espace fine insécable | `Configurez le cache ; redémarrez le service.` |
| `:` | espace fine insécable | `Erreur : fichier introuvable.` |
| `!` | espace fine insécable | (à éviter en doc technique) |
| `?` | espace fine insécable | `Voulez-vous vraiment supprimer ?` |
| `%` | espace insécable | `99 %` |
| `°` | non | `35°C` ; mais `35 °C` est admis |
| `«` (ouvrante) | espace insécable après | `« ainsi »` |
| `»` (fermante) | espace insécable avant | `« ainsi »` |
| Chiffre + unité | espace insécable | `3 Go`, `10 ms`, `200 €` |
| Chiffre + ordinal | non | `1er`, `2e`, `20e` |
| Abréviation + nom propre | espace insécable | `M. Dupont`, `n° 5` |

Note pratique : la plupart des éditeurs Markdown rendent `U+00A0` correctement. Si le pipeline final passe par un
moteur qui mange les espaces insécables, fixez-le côté outil — ne réécrivez pas la prose.

## Guillemets

- Guillemets français : `« … »` (avec espaces insécables à l’intérieur). Pour le premier niveau de citation.
- Guillemets de second niveau : `“ … ”` (anglais) ou `‹ … ›` (chevrons simples), selon la convention du projet.
- N’utilisez pas `"` (guillemet droit ASCII) en prose. Conservez-le dans les exemples de code.
- Pas de guillemets autour d’un identifiant de code : utilisez les backticks `` ` `` à la place.

## Apostrophe

- Apostrophe typographique en prose : `’` (`U+2019`).
- Apostrophe droite `'` (`U+0027`) dans le code, les chemins, les expressions régulières, les chaînes
  ICU/Fluent.
- L’élision suit le français standard : `l’API`, `aujourd’hui`, `s’il`.

## Capitales

- Les capitales prennent les accents : `À propos`, `État`, `Échec`, `Évolution`, `Île`, `Ça suffit`.
- Acronymes : tout en capitales, sans points (`API`, `HTTP`, `JSON`, `URL`).
- Le premier mot d’un titre prend la capitale ; les autres restent en minuscules sauf nom propre.
  - `Configuration du cache`, pas `Configuration Du Cache`.
- Noms de produits : casse officielle (`GitHub`, `GitLab`, `Kubernetes`, `PostgreSQL`, `iOS`, `npm`).

## Tirets

Trois caractères distincts :

| Caractère | Nom | Usage |
| --- | --- | --- |
| `-` | trait d’union | Mots composés : `clé-en-main`, `front-end` ; option CLI : `--quiet`. |
| `–` | tiret demi-cadratin | Plages numériques : `pages 10–20`, `Lun.–Ven.`. |
| `—` | tiret cadratin | Incise : `Le cache — invalidé toutes les heures — reste cohérent.` |

Conventions :

- En français, l’incise peut aussi se faire avec des virgules ou des parenthèses. N’abusez pas du tiret cadratin.
- Pour les plages, le tiret demi-cadratin sans espace : `2010–2020`.
- Pas d’espace autour du trait d’union.

## Nombres

- Séparateur des milliers : espace fine insécable. `1 000`, `10 000 000`.
- Séparateur décimal : virgule. `3,14` (en prose).
  - Conservez le point décimal dans le code, les API, les fichiers de configuration. Ne traduisez pas `3.14` en
    `3,14` dans un exemple de code JSON.
- Pour les versions, gardez la forme d’origine : `Python 3.12`, pas `Python 3,12`.

## Ponctuation finale

- Phrases complètes : point final.
- Titres : pas de point.
- Items de liste : pas de point si l’item n’est pas une phrase complète ; point si c’en est une.
- Pas de point d’exclamation dans la documentation technique (sauf dans la sortie d’un log).

## Élision et liaison

- Devant voyelle ou `h` muet : `l’API`, `l’hôte`, `l’index`.
- Devant `h` aspiré : pas d’élision. `le héros`, `le hub`.
- Pour les sigles : suivez la prononciation. `un API` (à l’oral « une A-P-I »), mais `l’API` est plus courant en
  écrit développeur.

## Abréviations courantes

| Abréviation | Forme correcte | Note |
| --- | --- | --- |
| Madame | `Mme` | sans point |
| Monsieur | `M.` | avec point |
| numéro | `n°` | `U+00B0` (degré), pas la lettre `o` |
| par exemple | `par ex.` | éviter `e.g.` en français |
| c’est-à-dire | `c.-à-d.` | éviter `i.e.` en français |
| etc. | `etc.` | jamais `...etc.` |

## Où ne jamais appliquer la typographie française

Toutes les règles ci-dessus s’arrêtent à la frontière du code et de la syntaxe. À l’intérieur de ces zones,
**conservez l’ASCII strict** :

- blocs de code Markdown (`` ``` `` … `` ``` ``) ;
- code inline (`` `…` ``) ;
- chemins de fichiers, URL, identifiants de code ;
- commandes CLI, drapeaux, variables d’environnement ;
- contenu JSON, YAML, TOML, INI (clés et valeurs) ;
- expressions régulières ;
- chaînes ICU MessageFormat et Fluent ;
- références à des en-têtes HTTP, paramètres d’API, sélecteurs CSS ;
- liens Markdown (la cible, pas le libellé visible).

Exemples :

- En prose : `Lancez la commande « apm install ».` — guillemets français autour du nom.
- Dans le code : ``Lancez `apm install`.`` — backticks, pas de guillemets, pas d’espace insécable.

## Cas limites

- **Pourcentages en code** : `99%` reste tel quel dans une expression de calcul, JSON, ou nom de variable.
- **Adresses e-mail** : pas de typographie française à l’intérieur.
- **URL avec deux-points** : `https://example.com/api` — pas d’espace insécable.
- **Heures** : `12:30` reste avec deux-points droit ; en prose pure, `12 h 30` est admis.
- **Dollars, euros** : `42 €`, `$42` (selon la convention de la devise). L’espace insécable n’est pas nécessaire
  dans le code.

Pour appliquer ces règles automatiquement, voir [`../linter/`](../linter/) et la doc Vale du paquet.
