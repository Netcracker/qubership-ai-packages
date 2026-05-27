# Checklist des tics LLM en français

Liste de patrons à repérer en relecture. Ce n’est **pas** un outil de détection ni un guide d’évasion : c’est un
filtre d’édition pour obtenir un français technique plus net.

Méthode : un patron isolé est rarement suffisant pour réécrire. Trois ou quatre dans le même paragraphe, ou un
patron qui revient à chaque section, sont le signal qu’il faut reformuler.

## 1. Connecteurs en surnombre

**Patron.** `Ainsi`, `de plus`, `par ailleurs`, `en outre`, `cependant`, `néanmoins`, `en effet`, `par conséquent`
en tête de phrase, souvent sans articulation logique réelle.

**Pourquoi c’est faible.** Les LLM ouvrent les paragraphes avec un connecteur de remplissage qui n’ajoute pas de
relation.

**Réécriture.** Supprimer le connecteur ; vérifier que la phrase tient toute seule.

- *Avant* : `De plus, le cache invalide les entrées après une heure.`
- *Après* : `Le cache invalide les entrées après une heure.`

## 2. Préambules de signalement

**Patron.** `Il est important de noter que`, `il convient de noter que`, `force est de constater`,
`il est à noter que`, `il faut souligner que`.

**Pourquoi.** Phrases d’annonce sans valeur ajoutée.

**Réécriture.** Supprimer l’en-tête ; garder l’assertion.

- *Avant* : `Il est important de noter que la requête expire après 30 secondes.`
- *Après* : `La requête expire après 30 secondes.`

## 3. Cadres élégants creux

**Patron.** `Dans cette optique`, `à l’aune de`, `s’inscrit dans`, `joue un rôle clé`, `constitue`, `représente`,
`se positionne comme`.

**Pourquoi.** Cadres rhétoriques qui n’apportent ni précision technique ni information factuelle.

**Réécriture.** Remplacer par un verbe précis.

- *Avant* : `Ce service joue un rôle clé dans l’authentification.`
- *Après* : `Ce service gère l’authentification.`

## 4. `permet de` vide

**Patron.** `X permet de` suivi du verbe que `X` fait déjà.

**Pourquoi.** `permet de` est un délégateur. Quand le sujet fait l’action lui-même, c’est du remplissage.

**Réécriture.** Verbe direct.

- *Avant* : `Cette fonction permet de récupérer l’identifiant.`
- *Après* : `Cette fonction retourne l’identifiant.`

À garder : quand `permet de` introduit une vraie capacité (`Le drapeau --json permet de scripter la sortie.`)

## 5. Doublets synonymiques

**Patron.** `simple et intuitif`, `robuste et fiable`, `rapide et performant`, `clair et concis`.

**Pourquoi.** Empilement d’adjectifs qui disent la même chose pour gonfler le ton.

**Réécriture.** Garder un seul terme ou aucun.

- *Avant* : `Une API simple et intuitive.`
- *Après* : `Une API courte.` (ou supprimer le qualificatif si l’exemple suffit)

## 6. Triplets forcés

**Patron.** `Rapide, efficace et fiable`, `simple, lisible et maintenable`, `sécurisé, scalable et performant`.

**Pourquoi.** La triade rhétorique signale presque toujours du marketing inséré par défaut.

**Réécriture.** Supprimer ou ne garder qu’un qualificatif justifié.

## 7. Parallélisme négatif

**Patron.** `Ce n’est pas X, c’est Y`, `Il ne s’agit pas seulement de X, mais aussi de Y`,
`Au-delà de X, c’est Y`.

**Pourquoi.** Rythme d’éditorial, pas de documentation.

**Réécriture.** Ne garder que ce qu’on affirme positivement.

- *Avant* : `Il ne s’agit pas d’un simple outil, c’est une plateforme complète.`
- *Après* : `C’est une plateforme.`

## 8. Verbes pseudo-formels

**Patron.** `effectuer une mise à jour`, `procéder à la suppression`, `réaliser une vérification`,
`disposer de`, `s’avérer`.

**Pourquoi.** Allongent la phrase sans précision.

**Réécriture.** Verbe direct.

- *Avant* : `Le service procède à la validation des données.`
- *Après* : `Le service valide les données.`

## 9. Conclusions génériques

**Patron.** Paragraphe final qui ouvre par `En conclusion`, `Pour résumer`, `En somme`, `Au final` et rappelle ce
qui a déjà été dit.

**Pourquoi.** Une page technique a rarement besoin de péroraison.

**Réécriture.** Supprimer ; arrêter sur la dernière information utile.

## 10. Posture didactique

**Patron.** `Dans cet article, nous allons voir…`, `Comme nous l’avons mentionné précédemment…`,
`Vous découvrirez dans la suite…`.

**Pourquoi.** Méta-discours qui retarde l’entrée dans le sujet.

**Réécriture.** Entrer dans le contenu.

- *Avant* : `Dans cette section, nous allons configurer le cache.`
- *Après* : `## Configurer le cache` puis la première instruction.

## 11. Artefacts conversationnels

**Patron.** `Bien sûr !`, `Excellente question`, `J’espère que cela vous aide`, `N’hésitez pas à me demander`.

**Pourquoi.** Résidus de chat injectés dans une documentation.

**Réécriture.** Supprimer entièrement.

## 12. Prose produit lissée

**Patron.** `Une expérience fluide et sans accroc`, `bénéficiez d’une intégration transparente`,
`profitez d’une performance optimale`.

**Pourquoi.** Marketing déguisé.

**Réécriture.** Indiquer la propriété mesurable ou supprimer.

- *Avant* : `Bénéficiez d’une intégration transparente avec votre stack.`
- *Après* : `S’intègre via un en-tête HTTP standard.`

## 13. Calques `it’s not X, it’s Y` traduits

**Patron.** `Ce n’est pas qu’un simple X, c’est un Y entier`.

**Pourquoi.** Calque direct de l’anglais marketing.

**Réécriture.** Affirmer Y.

## 14. Hyperboles de scalabilité

**Patron.** `À l’échelle planétaire`, `pour les charges les plus exigeantes`, `taillé pour la production
intensive`.

**Pourquoi.** Plus le texte promet d’échelle, moins il dit ce que le système fait réellement.

**Réécriture.** Donner un chiffre, un benchmark ou supprimer.

## 15. Empilement d’adjectifs avant le nom

**Patron.** `Une rapide, légère et puissante bibliothèque de…`.

**Pourquoi.** Le français place rarement plus d’un adjectif épithète antéposé.

**Réécriture.** Postposer ou supprimer.

- *Avant* : `Une rapide et fiable bibliothèque de cache`.
- *Après* : `Une bibliothèque de cache rapide.`

## 16. Hedging excessif

**Patron.** `Il est possible que`, `parfois`, `dans certains cas`, `potentiellement`, `il se peut que` empilés dans
la même phrase.

**Pourquoi.** Une seule modalité suffit. Trois en rafale ne disent plus rien.

**Réécriture.** Un hedge maximum par phrase. Préciser la condition au lieu de l’adoucir.

## 17. Faux modal `est censé`

**Patron.** `Le service est censé répondre en moins de 200 ms.`

**Pourquoi.** Calque flou de l’anglais `is supposed to`. Soit le service répond en moins de 200 ms, soit
l’objectif est documenté ; pas les deux à demi-mot.

**Réécriture.** Affirmer le contrat (`Le service répond…`) ou poser l’objectif (`L’objectif est de…`).

## 18. `notamment` et `parmi lesquels`

**Patron.** Liste ouverte par `notamment`, `parmi lesquels`, `entre autres` répétée à chaque énumération.

**Pourquoi.** Tic d’élégance qui suggère une liste plus large que celle énoncée.

**Réécriture.** Liste fermée si elle est complète ; sinon `comme` ou `par exemple` parcimonieusement.

## 19. `data` toujours pluriel grandiloquent

**Patron.** `Les données vous permettent de prendre des décisions éclairées et stratégiques`.

**Pourquoi.** Combine plusieurs tics : `permet de`, doublet, allusion à un public exécutif.

**Réécriture.** Indiquer quoi est mesuré et pour quelle décision concrète.

## 20. Liste de puces avec terme gras + deux-points par défaut

**Patron.** Tout paragraphe transformé en liste où chaque item s’ouvre par un terme en gras suivi de deux-points et
d’une phrase.

**Pourquoi.** Forme adaptée pour les définitions, mais utilisée à tort comme template d’élégance.

**Réécriture.** Garder la liste à puces gras/deux-points pour de vraies paires terme/définition. Sinon, prose.

## 21. Ouverture par `Imaginez…` ou `Et si…`

**Patron.** `Imaginez un système qui…`, `Et si vous pouviez…`.

**Pourquoi.** Posture commerciale dans une page technique.

**Réécriture.** Décrire directement ce que le système fait.

## 22. `de manière X` adverbialisé

**Patron.** `De manière efficace`, `de façon transparente`, `de manière sécurisée`.

**Pourquoi.** Forme adverbiale longue qui dilue.

**Réécriture.** Adverbe court ou suppression.

- *Avant* : `Le cache invalide les entrées de manière périodique.`
- *Après* : `Le cache invalide les entrées toutes les heures.`

## 23. `souligne l’importance de`

**Patron.** `Cela souligne l’importance d’une bonne configuration`.

**Pourquoi.** Méta-commentaire éditorial.

**Réécriture.** Dire pourquoi c’est important, ou supprimer.

## 24. `n’est pas sans rappeler`

**Patron.** `Cette approche n’est pas sans rappeler X`, `Sans nul doute`, `Force est de constater`.

**Pourquoi.** Tournures littéraires hors de propos dans un README technique.

**Réécriture.** Comparaison directe ou suppression.

## 25. Pivot `de façon à` pour cacher un verbe

**Patron.** `Configurer la file de façon à augmenter le débit` quand on veut juste dire `Augmenter le débit en
ajustant la file`.

**Réécriture.** Sujet + verbe + objectif explicite.

## 26. Métaphores systématiques

**Patron.** `cœur du système`, `clé de voûte`, `pilier`, `colonne vertébrale`, `pierre angulaire`.

**Pourquoi.** Métaphores marketing répétitives.

**Réécriture.** Rôle technique précis.

- *Avant* : `Le bus de messages est le cœur du système.`
- *Après* : `Le bus de messages route toutes les requêtes asynchrones.`

## 27. Anaphore par `cette` / `ce dernier`

**Patron.** `Ce dernier… Cette dernière…` répétés à chaque phrase pour éviter le sujet.

**Pourquoi.** Ralentit la lecture.

**Réécriture.** Reprendre le nom ou utiliser un pronom court.

## 28. Promesses temporelles vagues

**Patron.** `Dès maintenant`, `à l’avenir`, `prochainement`, `dans un futur proche`.

**Pourquoi.** Datent immédiatement le document.

**Réécriture.** Donner une version, une date, ou supprimer.

## 29. Listes vides à puce ouvertes par `permet de`

**Patron.** `- Permet de configurer X` / `- Permet de visualiser Y` / `- Permet de gérer Z`.

**Réécriture.** Sujet réel + verbe.

- *Avant* : `- Permet de gérer les utilisateurs.`
- *Après* : `- Gestion des utilisateurs.`

## 30. Symétrie obsessionnelle des sections

**Patron.** Chaque section a la même longueur, la même structure (`Contexte / Solution / Avantages`), le même
nombre de puces. Lisser n’est pas un objectif.

**Réécriture.** Garder la structure dont le contenu a besoin. Une section courte est légitime.
