# ICU MessageFormat et Mozilla Fluent — référence rapide

Référence courte pour préserver l’intégrité des chaînes localisées en français. Les erreurs de syntaxe ICU et
Fluent ne se voient pas à la relecture ; un linter dédié ou un test de chargement détecte mieux qu’une
inspection humaine.

## 1. Catégories de pluriel en français (CLDR)

Le français utilise deux catégories CLDR : `one` et `other`.

- `one` couvre 0 et 1.
- `other` couvre tout le reste.

Conséquence pratique :

- N’inventez **pas** `zero`, `two`, `few`, `many` pour le français. Si la chaîne source en a, supprimez les
  catégories inutilisées ou laissez le moteur tomber sur la branche `other`.
- Pour distinguer le cas zéro avec un texte spécifique, ajoutez `=0` explicitement.

## 2. Exemple ICU minimal

```text
{count, plural,
  one {# fichier sélectionné}
  other {# fichiers sélectionnés}
}
```

Avec `=0` pour le cas vide :

```text
{count, plural,
  =0 {Aucun fichier sélectionné}
  one {# fichier sélectionné}
  other {# fichiers sélectionnés}
}
```

Le `#` représente la valeur numérique. Pour formater le nombre séparément, utilisez `{count, number}` ailleurs
dans le message ; ne réécrivez pas `#` en `{count}` sans raison.

## 3. Genre via `select`

Quand le texte dépend du genre du sujet, utilisez `select` plutôt que de forcer un accord :

```text
{gender, select,
  female {Connectée}
  male {Connecté}
  other {Connexion établie}
}
```

La branche `other` est la valeur par défaut. Si le genre est inconnu côté serveur, préférez une formulation
neutre (`Connexion établie`) plutôt que `Connecté(e)`. Voir aussi
[`../modules/inclusive-writing.md`](../modules/inclusive-writing.md).

## 4. Apostrophe en ICU

L’apostrophe est un caractère d’échappement dans ICU MessageFormat. Selon le moteur :

- pour insérer une apostrophe littérale, doublez-la : `l''API` → `l’API` au rendu ;
- certains moteurs (Java `MessageFormat`) considèrent que `'…'` désactive l’interpolation : `'{count}'` rend la
  chaîne littérale `{count}`. Utile pour échapper des accolades.
- d’autres (`messageformat`, `Intl.MessageFormat`) acceptent l’apostrophe UTF-8 brute `’` sans échappement.

Quand vous traduisez :

1. vérifiez le moteur cible (Java, JavaScript, iOS, Android, .NET) ;
1. doublez `''` quand le doute existe, c’est sans effet sur les moteurs récents ;
1. testez la chaîne avec un échantillon de valeurs.

## 5. Placeholders à préserver exactement

Quel que soit le format :

- ICU : `{count}`, `{count, number}`, `{count, plural, …}`, `{name, select, …}` ;
- printf : `%s`, `%d`, `%1$s`, `%(name)s` (Python) ;
- ES interpolation : `${name}` ;
- gettext positional : `{0}`, `{1}` ;
- Fluent : `{$count}`, `{-brand-name}`, `{ DATETIME($date) }`.

Règles :

- **Nom et ordre identiques** à la source. `{userName}` reste `{userName}`, pas `{nomUtilisateur}`.
- **Pas de traduction du contenu** : `{name}` n’est pas un mot, c’est une référence.
- **Réordonner autour du placeholder** si la grammaire française l’exige : `User {name} logged in` →
  `L’utilisateur {name} s’est connecté.`
- **Préposition / article hors du placeholder** : ajoutez `l’`, `du`, `pour` autour de la variable, jamais à
  l’intérieur.

## 6. Mozilla Fluent — structure

Exemple complet :

```fluent
files-selected =
    { $count ->
        [one] { $count } fichier sélectionné
       *[other] { $count } fichiers sélectionnés
    }

shared-photos =
    { $userName } a partagé { $photoCount ->
        [one] une photo
       *[other] { $photoCount } photos
    }.

-brand-name = Acme Cloud

welcome-message = Bienvenue dans { -brand-name }.
```

À ne **pas** traduire :

- les identifiants de message (`files-selected`, `shared-photos`) ;
- les noms de sélecteur (`[one]`, `[other]`, `[female]`, `[male]`) ;
- le marqueur de défaut `*` ;
- les références de variable `{ $count }`, `{ $userName }`, `{ $photoCount }` ;
- les références de terme `{ -brand-name }` ;
- les fonctions intégrées : `{ DATETIME($date) }`, `{ NUMBER($n) }`.

À traduire :

- la valeur des termes (par exemple `-brand-name = Acme Cloud` peut devenir `-brand-name = Acme Nuage` si la
  marque est elle-même traduite — généralement non) ;
- les attributs : `.label`, `.placeholder`, `.title`, `.aria-label`.

Exemple avec attributs :

```fluent
delete-button =
    .label = Supprimer
    .title = Supprimer définitivement
    .aria-label = Supprimer cet élément
```

## 7. Pluriel Fluent en français

Comme en ICU : `one` et `other` suffisent.

```fluent
items-count =
    { $count ->
        [one] { $count } élément
       *[other] { $count } éléments
    }
```

La branche `*[other]` doit rester marquée par `*` (valeur par défaut).

## 8. Ce qu’il ne faut pas faire

- **Inventer des catégories** : n’ajoutez pas `[zero]`, `[two]`, `[few]`, `[many]` à une chaîne française.
- **Renommer une variable** : ne transformez pas `{ $userName }` en `{ $nomUtilisateur }`. L’identifiant
  appartient au code.
- **Concaténer en dehors du format** : `"Bonjour " + name + " !"` au lieu de
  `Bonjour {$name} !` casse la localisation.
- **Réordonner les branches de sélecteur** sans comprendre la syntaxe : la branche par défaut peut être en
  dernier (`*[other]`) ; ne la déplacez pas.
- **Mélanger formats** : ne réécrivez pas une chaîne ICU en Fluent ou vice-versa lors d’une traduction.

## 9. Vérifications à automatiser

Ces vérifications ne se font pas en relecture humaine. Ajoutez-les au CI :

- intégrité des placeholders : tous ceux du `msgid` se retrouvent dans le `msgstr` ;
- pas de placeholder inventé ;
- pour le pluriel : présence des catégories CLDR requises pour la locale (`one`, `other` en français) ;
- échappement de l’apostrophe en ICU compatible avec le moteur cible ;
- pour Fluent : présence du `*` sur la branche par défaut.

Outils existants :

- `messageformat-validator` (npm) pour ICU ;
- `fluent-syntax` et `compare-locales` (Mozilla) pour Fluent ;
- `msgfmt -c` pour gettext ;
- scripts maison sur le format propriétaire du projet.

## 10. Cas particulier — Android et iOS

- **Android `strings.xml`** : utilise `<plurals>` avec `quantity="one"` et `quantity="other"` pour le français.
  Échappez l’apostrophe : `\'`. Échappez les guillemets droits : `\"`.
- **iOS `.stringsdict`** : utilise les catégories CLDR (`one`, `other`). Pas d’échappement spécial de
  l’apostrophe en XML.
- **iOS `.strings`** : pas de pluriel natif ; utilisez `.stringsdict` séparé.

Ne convertissez pas un format vers un autre lors d’une traduction. Demandez à l’équipe de localisation.
