# Mode fr-CA / français québécois

Module à activer **uniquement** en mode fr-CA. Il ne s’applique pas par défaut.

## 1. Quand activer

Activez ce module quand au moins une des conditions suivantes est vraie :

- l’utilisateur demande explicitement du français canadien, québécois, ou `fr-CA` ;
- un chemin de fichier contient `fr_CA`, `fr-CA`, `fr_CA.UTF-8` ;
- la configuration de locale (`languages`, `i18n.locales`, gettext, ICU) liste `fr-CA` ;
- le texte voisin utilise déjà `courriel`, `clavardage`, `pourriel`, `magasiner`, `balado`, `fureteur` ;
- le dépôt cible le gouvernement fédéral canadien, le gouvernement du Québec ou un public canadien francophone.

Sinon, restez en fr-FR. Ne forcez pas la terminologie québécoise dans un dépôt fr-FR « pour faire plus
francophone ».

## 2. Sources à privilégier en fr-CA

- **OQLF — Vitrine linguistique** et **Grand dictionnaire terminologique (GDT)** pour la terminologie technique et
  les anglicismes.
- **Bureau de la traduction — Clés de la rédaction** pour le style général et la rédaction administrative.
- Le glossaire interne du projet, qui prime toujours.

Limites :

- Ne transposez pas un terme officiel OQLF dans du fr-FR sans vérifier l’usage réel en France.
- Certaines recommandations OQLF (`baladodiffusion` pour *podcast*, `fureteur` pour *browser`) ne sont pas suivies
  par les développeurs francophones du Québec eux-mêmes. Suivez l’usage du dépôt, pas la prescription.

## 3. Différences typographiques

- Espace insécable : mêmes règles qu’en fr-FR (avant `; : ! ? %`, entre nombre et unité).
- Guillemets : `« … »` également en fr-CA.
- Capitales accentuées : toujours.

## 4. Différences terminologiques courantes

| Anglais | fr-FR par défaut | fr-CA par défaut | Note |
| --- | --- | --- | --- |
| email | e-mail (ou courriel) | courriel | `mél` à éviter dans les deux variantes. |
| spam | spam | pourriel | `pourriel` est largement compris en fr-CA, parfois moins en milieu technique pur. |
| cookie | cookie | cookie | `témoin` seulement si le projet l’utilise déjà. |
| login (verbe) | se connecter | ouvrir une session | `se connecter` reste compréhensible et plus court. |
| login (écran) | connexion | ouverture de session | |
| log out | se déconnecter | fermer la session | |
| chat | chat | clavardage | `clavardage` est l’usage standard en fr-CA. |
| chatbot | chatbot | agent conversationnel / chatbot | |
| shopping | achats | magasinage | Verbe : `magasiner`. |
| podcast | podcast | balado | `baladodiffusion` reste rare ; `balado` suffit. |
| browser | navigateur | navigateur | `fureteur` recommandé par l’OQLF mais peu utilisé dans la pratique. Ne forcez pas. |
| pull request | pull request (PR) | demande de tirage / pull request | « demande de tirage » est OQLF ; en pratique `pull request` reste fréquent. |
| merge request | merge request (MR) | demande de fusion / merge request | `demande de fusion` est compréhensible en fr-FR aussi. |
| issue | issue / ticket / problème | issue / billet / problème | `billet` apparaît dans certaines plateformes francophones. |
| file (verb, in tracker) | ouvrir un ticket | ouvrir un billet | Selon la plateforme. |
| feedback | retour | rétroaction | `rétroaction` est OQLF. `retour` reste correct. |
| feature | fonctionnalité | fonctionnalité | |
| webhook | webhook | webhook | |
| backup | sauvegarde | copie de sauvegarde | |
| spam (verbe) | spammer | polluposter | Rare. |
| upload | téléverser | téléverser | `téléverser` est désormais courant dans les deux variantes. |
| download | télécharger | télécharger | |

## 5. Ce qu’il ne faut pas forcer

Même en mode fr-CA :

- ne traduisez pas systématiquement les termes développeur qui restent en anglais dans la pratique
  (`commit`, `branch`, `rebase`, `endpoint`, `framework`) ;
- ne renommez pas des éléments de code, des drapeaux CLI, des variables d’environnement ou des en-têtes HTTP ;
- ne remplacez pas la terminologie déjà fixée par le dépôt : si le code parle de `pull request`, gardez-le.

## 6. Conservation de la cohérence

Quand vous éditez un fichier déjà localisé :

1. **Détectez la variante** par les indices listés en section 1.
1. **Préservez les choix existants** : si le texte utilise `courriel`, n’introduisez pas `e-mail` ; si le texte
   utilise `connexion`, n’introduisez pas `ouverture de session`.
1. **Signalez les incohérences** au lieu de les corriger silencieusement : un fichier qui mélange `clavardage` et
   `chat` mérite une note dans la PR.

## 7. Particularités grammaticales et lexicales

- Le `on` à valeur indéfinie reste courant en fr-CA, comme en fr-FR. Pas de tic régional à corriger.
- Évitez `bienvenu / bienvenue` comme accusé de réception (`You’re welcome` ≠ `Bienvenue`). Préférez `de rien` ou
  reformulez.
- Les abréviations administratives (`SAAQ`, `RAMQ`, `NAS`) ne se traduisent pas et restent telles quelles dans un
  texte logiciel québécois.

## 8. fr-BE, fr-CH, fr-LU

Ces variantes ne disposent pas d’un module dédié. Suivez fr-FR sauf glossaire de projet contraire :

- n’introduisez pas `septante`, `huitante`, `nonante` si le texte n’en contient pas déjà ;
- préservez les choix de la plateforme cible (par exemple `numéro national` en Belgique) ;
- pour la Suisse romande, suivez les recommandations de la Confédération si le projet l’exige.
