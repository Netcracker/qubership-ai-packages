# Chaînes d’interface et localisation

Module complémentaire à la section 7 du [`SKILL.md`](../SKILL.md). Chargez-le quand vous écrivez ou révisez des
boutons, des libellés de formulaire, des messages d’information, des plurals ICU ou Fluent, des tooltips, des
états vides, des validations, ou tout autre texte d’interface en français.

## 1. Boutons et actions de menu

**Règle.** Infinitif, 1 à 3 mots, **sans point**, sans points d’exclamation. La capitale est sur la première
lettre seulement.

- Action sur l’objet courant : `Enregistrer`, `Supprimer`, `Exporter`, `Annuler`, `Publier`.
- Action lançant un flux : `Créer un projet`, `Ajouter un membre`, `Connecter une base`.
- Bouton de confirmation : nommez le résultat, pas l’assentiment. `Supprimer` plutôt que `Oui`.
  `Enregistrer et fermer` plutôt que `OK`.

Antipatrons :

- `Cliquez ici`, `Cliquez pour continuer` → le bouton est déjà un appel à l’action.
- `Soumettre` calqué sur *submit* → `Envoyer` ou un verbe qui décrit l’action réelle.
- `Sauvegarder` au sens de `Save` → `Enregistrer` (la sauvegarde, c’est `Backup`).
- `Submit` non traduit dans une interface française.

Exemples canoniques :

- `Delete` → `Supprimer`
- `Save` → `Enregistrer`
- `Cancel` → `Annuler`
- `Export` → `Exporter`

## 2. Libellés de champs et titres

Libellé de champ : substantif au nominatif, sans point.

- `Nom du service`, `Port`, `Adresse e-mail`, `Clé d’API`.

Ne transformez pas un libellé en instruction (`Saisissez le nom du service`) : la consigne va dans le placeholder
ou dans une aide contextuelle.

Titres d’écran, de boîte de dialogue, de section : style « phrase normale » — première lettre en capitale, le
reste en minuscules. Pas de point final.

- `Paramètres`, `Configuration du cache`, `Installation interactive`.
- Pas `Configuration Du Cache` (capitalisation à l’anglaise).

Substantif pour les titres `-ing` :

- `Configuring the cache` → `Configuration du cache`
- `Installing Docker` → `Installation de Docker`
- `How to configure TLS` → `Configurer TLS` (tutoriel procédural) ou `Configuration de TLS` (référence).

## 3. Placeholders

Le placeholder donne un **exemple**, pas une consigne. Il ne répète pas le libellé.

- `prod-eu-1`, `user@example.com`, `Entre 1 et 65535`, `ISO-8601, par exemple 2025-01-15`.
- Pas de `Saisissez…`, pas de `Entrez votre…`.

Si le format est spécial, signalez-le brièvement : `UUID, par exemple 7a1b…`.

## 4. Aides contextuelles et tooltips

Courtes, sans point final si la phrase n’en est pas une.

- `Visible uniquement par les membres du projet`
- `Maximum 200 caractères`
- `Cmd+S enregistre le brouillon`

Si l’explication tient sur un paragraphe, déplacez-la vers la documentation et liez-la.

## 5. États vides

Patron : ce qui s’est passé + action à entreprendre.

- `Aucun élément pour le moment. Créez la première règle pour commencer.`
- `Aucune intégration connectée. Ajoutez-en une pour recevoir des notifications.`
- `Aucun résultat. Précisez la recherche ou réinitialisez les filtres.`

Pas de `Oups`, pas de `Désolé`, pas d’`Hélas`.

## 6. Confirmations et avertissements

Question + précision si l’action est irréversible. Verbe à l’infinitif sur les boutons de résultat.

- `Supprimer le projet acme ? Cette action est irréversible.`
- `Voulez-vous vraiment supprimer ce fichier ?`
- Bouton : `Supprimer` ou `Annuler`, pas `Oui` ou `Non`.

`This will overwrite your changes.` → `Cette action écrasera vos modifications.` (à préférer à `Ceci va écraser vos
modifications.`)

## 7. Toasts et notifications

Une ligne, résultat au présent ou au passé composé court, sans point final.

- `Modifications enregistrées`
- `Lien copié`
- `Échec de l’envoi. Réessayez`

Pas de `Vos modifications ont été enregistrées avec succès` : « ont été », « avec succès » et « vos » sont du
remplissage.

## 8. Messages d’erreur

Forme : `Impossible de <action>. <Cause ou recours.>`

- `Cannot save file` → `Impossible d’enregistrer le fichier.`
- `Cannot save file: permission denied` → `Impossible d’enregistrer le fichier. Droits d’écriture manquants sur
  /etc/foo.yaml.`
- `Invalid port` → `Port non valide. Indiquez un nombre entre 1 et 65535.`

Voir le module Erreurs et journaux dans le `SKILL.md` (section 8).

## 9. ICU MessageFormat

Le français CLDR utilise les catégories `one` et `other`. `one` couvre 0 et 1. Inventer `zero`, `two`, `few`,
`many` pour le français est une erreur de syntaxe sauf si le moteur l’exige.

```text
{count, plural,
  one {# fichier sélectionné}
  other {# fichiers sélectionnés}
}
```

Cas zéro distinct (texte spécifique pour « aucun ») : ajoutez `=0` explicitement.

```text
{count, plural,
  =0 {Aucun fichier sélectionné}
  one {# fichier sélectionné}
  other {# fichiers sélectionnés}
}
```

Apostrophe ICU : l’apostrophe est un caractère d’échappement. Pour écrire `l’API` dans un message ICU,
échappez avec deux apostrophes : `l''API`. Vérifiez le moteur cible, certains acceptent UTF-8 brut.

Genre en français : si la chaîne dépend du genre du sujet, utilisez un `select` plutôt qu’une accordance forcée
sur un mot fixe.

```text
{gender, select,
  female {Connectée}
  male {Connecté}
  other {Connexion établie}
}
```

Quand le genre est inconnu, préférez la branche neutre (`Connexion établie`) plutôt que `Connecté(e)`.

## 10. Mozilla Fluent

Préservez la syntaxe Fluent : sélecteurs, variantes, termes (`{-brand-name}`), attributs, variables (`{$count}`).

```fluent
files-selected =
    { $count ->
        [one] { $count } fichier sélectionné
       *[other] { $count } fichiers sélectionnés
    }
```

À ne pas traduire :

- les mots-clés du sélecteur (`one`, `other`) ;
- le marqueur de défaut `*` ;
- les références de variable `{$count}` ;
- les références de terme `{-brand-name}` ;
- les attributs `.label`, `.placeholder`, `.title`.

À ne pas réordonner sans comprendre : le `*[other]` doit rester la branche par défaut.

## 11. Placeholders et variables

Préservez exactement : `%s`, `%d`, `%1$s`, `%(name)s`, `{name}`, `{{name}}`, `${name}`, `{0}`, `{$count}`, balises
HTML/XML en chaîne, ancres Markdown.

- N’adaptez pas les noms : `{userName}` ne devient pas `{nomUtilisateur}`.
- Ne traduisez pas le contenu d’un placeholder.
- Ajustez l’ordre des mots autour, pas l’identifiant : `User {name} logged in` →
  `L’utilisateur {name} s’est connecté.`
- Si la grammaire française demande un mot supplémentaire (préposition, article), placez-le **hors** du placeholder.

Antipatron classique : `Bonjour {0} !` traduit en `Bonjour {prénom} !` — l’identifiant du placeholder appartient au
code.

## 12. Cohérence terminologique

- Choisissez une variante par concept et utilisez-la partout : `e-mail` ou `courriel`, mais pas les deux.
- Si l’interface contient déjà `Tableau de bord`, n’écrivez pas `Dashboard` dans une nouvelle chaîne.
- Pour les noms de produit, suivez exactement la casse officielle : `GitHub`, `GitLab`, `Kubernetes`, `PostgreSQL`.
- Pour les fonctionnalités internes, fixez le terme dans un glossaire de projet et liez-le depuis le `CONTRIBUTING.md`.

Voir [`../references/glossary-fr.tsv`](../references/glossary-fr.tsv) pour la base de départ et
[`fr-ca-overrides.md`](fr-ca-overrides.md) pour les variantes canadiennes.
