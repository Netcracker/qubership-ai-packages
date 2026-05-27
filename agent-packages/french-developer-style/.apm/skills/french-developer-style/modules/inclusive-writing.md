# Écriture inclusive

Module **désactivé par défaut**. À charger uniquement si l’utilisateur ou la politique du projet le demande
explicitement.

## 1. Quand activer ce module

- Demande explicite de l’utilisateur (« utilise l’écriture inclusive », « rends le texte non genré »).
- Politique de projet documentée dans `CONTRIBUTING.md`, un style guide interne, ou la charte produit.
- Texte voisin déjà inclusif (point médian régulier, doublets systématiques) à conserver par cohérence.

Sinon, restez sur les règles par défaut du `SKILL.md` (formulation neutre quand possible, sans point médian).

## 2. Priorité aux formulations épicènes

L’approche recommandée est **la reformulation neutre**, pas le point médian. Elle reste lisible, accessible aux
lecteurs d’écran et résistante aux moteurs de traduction.

Techniques principales :

- **Tournures impersonnelles** : `L’équipe peut…`, `Il est possible de…`, `Cette action permet…`.
- **Noms épicènes** : `personne`, `équipe`, `partie prenante`, `responsable`, `membre`.
- **Verbes plutôt que noms d’agent** : `qui développe` à la place de `développeur·euse`,
  `qui contribue` à la place de `contributeur·rice`.
- **Voix passive ciblée** : `La connexion est établie` plutôt que `Vous êtes connecté(e)`.
- **Sujet inversé** : `Pour publier, il faut…` plutôt que `L’auteur doit publier…`.

Exemples :

- `Vous êtes connecté.` → `La connexion est établie.`
- `Utilisateur connecté` → `Connexion établie`
- `Les développeurs peuvent configurer le cache.` → `L’équipe de développement peut configurer le cache.`
  ou `Les personnes qui développent peuvent configurer le cache.` (selon le contexte)
- `L’administrateur doit valider la demande.` → `La demande doit être validée par l’administration.`
  ou `Une validation par l’administration est requise.`
- `Le développeur exécute la commande.` → `Exécutez la commande.` (impératif, public-cible direct)

## 3. Doublets complets

Réservés aux cas où la reformulation épicène nuit clairement à la précision.

- `les développeuses et les développeurs`
- `chaque contributrice ou contributeur`

Évitez les doublets systématiques dans le corps d’un long document : ils alourdissent la lecture.

## 4. Point médian : à éviter par défaut

Le point médian (`développeur·rice`, `utilisateur·ice`) n’est recommandé que si **trois** conditions sont
remplies :

1. le projet l’utilise déjà partout de manière cohérente ;
1. le texte n’est pas une chaîne UI courte ;
1. la lecture par synthèse vocale a été vérifiée.

Sinon, préférez la reformulation. Ne mélangez pas point médian et formulation neutre dans le même fichier.

Variantes admissibles si le projet le précise : point médian (`·`), tiret (`-`), barre oblique (`/`). Choisissez-en
une et tenez-vous-y.

## 5. Ce que ce module n’autorise pas

- Pas de `(e)` dans une chaîne UI : `connecté(e)` est à éviter même en mode inclusif. Reformulez :
  `La connexion est établie`.
- Pas de néologisme pronominal (`iel`, `ielles`) sauf demande explicite. Quand introduits, ils doivent être
  cohérents dans tout le fichier et signalés dans le `CONTRIBUTING.md`.
- Pas de modification d’identifiants de code, de noms de variables, de drapeaux CLI ou de noms d’API pour des
  raisons d’inclusivité.
- Pas de remplacement de termes techniques bien établis (`master/slave` en architecture matérielle, par exemple)
  par effet de zèle : suivez la politique du projet et de l’écosystème en amont.

## 6. Accessibilité

Vérifiez que la formulation choisie reste lisible par un lecteur d’écran. Le point médian est lu comme `point`
dans la plupart des moteurs de synthèse, ce qui rend `développeur·euse` peu compréhensible à l’oral. La
reformulation épicène ne pose pas ce problème.

## 7. Cohérence sur tout le fichier

Quand vous éditez un fichier :

1. Détectez le style inclusif déjà en place (épicène, doublets, point médian).
1. Préservez-le. N’introduisez pas un troisième style.
1. Si plusieurs styles cohabitent, signalez-le dans la PR plutôt que de tout uniformiser dans une PR de style.

## 8. Cas particulier — messages d’erreur et journaux

Dans un message d’erreur destiné à un public mixte, la **forme impersonnelle** est presque toujours préférable,
inclusive ou non. Elle évite le problème d’accord en genre tout en restant courte.

- `Vous n’êtes pas autorisé(e) à effectuer cette action.` → `Action non autorisée.`
- `Vous avez été déconnecté.` → `Session expirée. Reconnectez-vous pour continuer.`
