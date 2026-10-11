# Topic 2 : insuffisances, corrections et validation restante

Date : 10 septembre 2026. Document de preparation et protocole prospectif.

## 1. Ton sujet et ce que signifie le couvrir

Le Topic 2 du Research Proposal porte sur les modeles de transcription pour les reunions bruyantes et multilingues. Il demande une comparaison des modeles, des strategies d'adaptation et un travail sur la rapidite. Plusieurs intervenants et un prototype en situation de reunion font partie de l'objectif. L'OCR et la personnalisation des interfaces appartiennent aux autres topics.

Une fonction programmee, une experience executee et une conclusion scientifique sont trois choses differentes. Avoir un bouton de diarisation prouve que tu as prevu cette fonction. Executer le traitement prouve qu'il fonctionne sur un fichier. Mesurer sa precision exige une reference correcte indiquant qui parle et quand. Une bonne performance sur plusieurs reunions independantes serait une preuve plus forte.

Ce document couvre toutes les insuffisances identifiees en explicitant leur traitement. Il ne declare pas terminees les experiences pour lesquelles les enregistrements, annotations ou mesures manquent. Aucune nouvelle transcription ASR n'a ete executee dans cette intervention. Les corrections chiffrees reposent sur les CSV existants.

## 2. Etat des preuves

| Attente | Preuve presente | Insuffisance | Statut apres cette intervention |
|---|---|---|---|
| Comparer les modeles | 468 transcriptions MInDS-14 ; Whisper, MMS, Conformer | Petit corpus ; langues fournies a certains modeles | Comparaison pilote disponible, generalisation partielle |
| Mesurer le bruit | 12 paires propres/bruitees | Un bruit blanc, un SNR, pas une salle reelle | Analyse appariee corrigee et reproduite |
| Plusieurs langues | EN/FR/DE | Pas de validation de changement de langue au sein d'une phrase | Evaluation trilingue disponible, code-switching non valide |
| Plusieurs intervenants | 7 assemblages et sorties de diarisation | Identites A/B attribuees sans preuve d'identite vocale | Test d'integration seulement |
| Adapter au domaine | Prompt et LoRA sur parole bancaire | Pas de test contenant le vocabulaire cible de Nestle | Effet sur domaine cible non etabli |
| Reduire le delai sans perdre en precision | CSV live et RTF | Pas de WER live couple, pas de chronometrage navigateur | Audit par session ajoute ; optimisation non validee |
| Simuler une reunion Teams | Prototype WebSocket | Pas de compte rendu d'un essai Teams controle | Protocole defini, essai a realiser |

## 3. Chiffres a apprendre avec leur sens

### 3.1 Pourquoi 36 fichiers ne sont pas 36 observations independantes

Il y a 24 enregistrements propres. Douze ont aussi une copie a laquelle on a ajoute du bruit. Cela donne 36 fichiers mais seulement 24 paroles sources distinctes. Une copie bruitee ne devient pas une nouvelle personne ni une nouvelle phrase.

Pour mesurer le bruit, on compare les 12 phrases avec leur propre copie : 61.1 % de WER avant bruit, 96.4 % apres, soit 35.3 points supplementaires. L'intervalle bootstrap a 95 % vaut [7.0 ; 60.0] points. Sa largeur rappelle le petit nombre de phrases.

Le WER compte les mots substitues, supprimes et ajoutes, puis divise par le nombre de mots de reference. Un ajout excessif de mots peut produire un WER superieur a 100 %. Ne dis pas que 96.4 % de WER signifie exactement 96.4 % des mots faux : les insertions comptent aussi.

La moyenne sur les 24 fichiers propres vaut 47.0 %. Comparer directement cette moyenne aux 12 bruites melange l'effet du bruit avec la difficulte differente des phrases. Ce contraste reste descriptif, pas l'estimation appariee.

### 3.2 Pourquoi le gain LoRA reste incertain

LoRA ajuste une petite partie des parametres du modele. Ici, la comparaison utilise le meme chemin d'execution et les memes fichiers : 31.2 % avant adaptation, 30.2 % apres. Le gain moyen est environ 1 point.

Le bootstrap recompose des echantillons en gardant ensemble une phrase propre et sa copie bruitee. L'intervalle obtenu [-2.4 ; 5.3] contient zero. Cela signifie que les donnees ne permettent pas d'etablir un gain fiable ; cela ne prouve ni que LoRA est inutile, ni que les deux systemes sont equivalents.

Surtout, apprendre sur du vocabulaire bancaire ne prouve pas une amelioration des marques et termes de Nestle. La couverture supposee du domaine bancaire par le preentrainement reste une explication possible, pas une observation directe de ses donnees d'apprentissage.

### 3.3 Pourquoi il existe maintenant deux resumes de latence

L'etude historique contient les 22 premieres lignes du journal : 2 premiers enonces mis a part, 20 suivants. Mediane 0.555 s, p95 0.844 s, maximum 1.177 s. Le p95 est un percentile calcule par interpolation, pas le maximum.

Le journal courant contient 38 lignes et une troisieme session inferable par le retour de l'identifiant a 1. Sur les 35 lignes hors premiers enonces : mediane 0.575 s, p95 1.614 s, maximum 11.021 s. La troisieme session seule donne un p95 de 4.814 s sur 15 observations. Le rapport `results/topic2_readiness_audit.md` conserve cette observation lente.

Le CSV ne contient ni date, ni modele, ni appareil, ni charge systeme. On ne peut pas attribuer le ralentissement a une cause precise ni garantir la comparabilite des sessions. Le premier enonce est un indicateur de demarrage, pas une mesure isolee du chargement du modele.

Dans `backend/main.py`, le chronometre est lu avant l'envoi WebSocket. Il n'inclut pas la reception et l'affichage dans le navigateur. Ajouter 0.6 s de silence donne une approximation supplementaire, jamais une mesure complete du delai percu. Les sorties vides ou rejetees peuvent sortir de la fonction avant journalisation : le CSV ne mesure donc pas le taux global d'echec.

## 4. Protocole A : vraies reunions et vrais locuteurs

### Le probleme

`backend/training/build_meetings.py` attribue A aux clips impairs et B aux clips pairs. Cela ne garantit pas que tous les clips A proviennent de la meme voix. Meme une diarisation correcte peut alors sembler fausse. Le DER de 0.585 ne permet pas de conclure a une precision de 41.5 % sur des personnes reelles.

### Ce qu'il faut obtenir

Utiliser un corpus de reunions avec fichiers audio, transcription et identites de locuteurs documentees, ou des enregistrements internes autorises et annotes. Les corpus de reunions cites dans la bibliographie revisee sont des candidats, pas des fichiers deja presents dans ce depot. Verifier disponibilite, conditions d'utilisation, canaux et annotations avant selection.

Pour une extension pilote, fixer avant inference une liste d'au moins cinq reunions independantes et des fenetres continues d'une duree documentee. C'est un minimum pratique propose, pas une justification de puissance statistique. Un corpus anglais valide seulement cette extension anglaise ; le volet trilingue demeure distinct.

### Etapes

1. Enregistrer l'origine, la licence, la version, la reunion, les canaux, les intervalles choisis et les empreintes des fichiers dans un manifeste.
2. Separer les reunions de developpement et d'evaluation. Choisir les options uniquement sur le developpement.
3. Verifier sur ecoute les frontieres de parole et les identites reelles. Garder des identites stables a travers une reunion. Conserver les chevauchements de parole.
4. Documenter le canal choisi et toute conversion audio. Un micro proche n'est pas equivalent a un micro distant.
5. Executer le modele de reference et le modele retenu sur les memes fenetres, avec et sans diarisation si applicable. Garder configurations, versions, sorties et erreurs.
6. Calculer WER avec le scorer canonique, DER avec la bibliotheque existante et un score de mots attribues aux locuteurs avec une implementation de reference. Documenter tolerance aux frontieres et traitement du chevauchement. Ne pas appeler un WER ordinaire cpWER ou tcpWER.
7. Presenter les resultats par reunion et leur agregat. Reechantillonner les reunions, pas chaque petit segment comme s'il etait independant.

Le WER evalue les mots. Le DER evalue le temps de parole manque, ajoute ou attribue au mauvais locuteur. Les scores de transcription attribuee aux locuteurs verifient les mots ET leur attribution. Ces mesures repondent a des questions differentes.

Critere de cloture : fichiers et annotations valides, sorties reproductibles, taux d'echec explicite, scores par reunion et limites documentees. Un script pret sans execution ne clot pas cette insuffisance.

## 5. Protocole B : vocabulaire professionnel

Un prompt est une liste d'indices fournie au modele avant transcription. Il peut aider a reconnaitre une marque, mais aussi faire apparaitre cette marque alors que personne ne l'a prononcee.

Construire un petit jeu specifique avec des phrases prononcees par des personnes consentantes. Une proposition pratique est 60 phrases, reparties EN/FR/DE : moitie avec termes cibles, moitie sans eux. Diversifier les voix et garder des voix d'evaluation distinctes du developpement. Ce volume reste exploratoire.

Definir un glossaire a partir de documents autorises avant de consulter les sorties. Le glossaire contient les formes attendues et les variantes orthographiques acceptees. Il ne doit jamais contenir les phrases de reference du test. Des enregistrements lus constituent un test de termes lus, pas des conversations spontanees de Nestle.

Comparer d'abord le meme modele sans prompt puis avec prompt, sans modifier simultanement langue, pretraitement ou decodage. Tester LoRA seulement avec un apprentissage distinct ; le LoRA bancaire existant doit rester etiquete comme tel.

Mesurer WER, nombre d'occurrences de termes attendues et reconnues, rappel des termes, et occurrences de termes hallucinees dans les phrases temoins. Expliquer la regle d'alignement et les variantes acceptees avant scoring ; une recherche approximative opportuniste pourrait artificiellement ameliorer le score. Conserver les cas de degradation.

Critere de cloture : audio reel, references verifiees, glossaire fige, comparaisons appariees et effets secondaires rapportes. Un texte invente ou une voix synthetique peut tester le logiciel, pas remplacer une validation sur voix humaines.

## 6. Protocole C : bruit et changement de langue

Le bruit blanc a 8 dB est une condition controlee. Il ne represente pas a lui seul une ventilation, des voix concurrentes ou la reverberation d'une salle.

Sur un jeu externe reserve, conserver les versions propres et creer des variantes avec des bruits documentes a plusieurs niveaux fixes avant inference. La proposition est 5, 10 et 20 dB ; ces niveaux sont des nouvelles conditions et ne remplacent jamais les 8 dB canoniques. Verifier la puissance du signal, la definition du SNR, la graine et l'absence d'ecretage. Ne pas changer la reference textuelle entre variantes. Garder toutes les copies d'une source dans le meme groupe statistique.

Pour le changement de langue, enregistrer ou obtenir des phrases contenant une transition annotee et connue. Comparer l'auto-detection a une strategie explicite autorisant plusieurs langues. Une langue forcee unique est un point de comparaison, pas une solution generale a une phrase bilingue. Reporter les erreurs par langue et autour de la transition.

Critere de cloture : donnees et configurations archivees, comparaisons appariees et plusieurs situations effectivement testees. Trois langues dans trois dossiers ne prouvent pas la gestion du code-switching.

## 7. Protocole D : rapidite et precision ensemble

Le RTF est le temps de calcul divise par la duree audio : 2 s de calcul pour 10 s d'audio donnent 0.2. Cela indique la vitesse moyenne de traitement ; le sous-titre peut quand meme arriver tard si le systeme attend la fin de la phrase.

Utiliser un enregistrement reserve, ses references et le meme chemin WebSocket que le prototype. Envoyer l'audio a vitesse reelle. Un envoi aussi rapide que possible mesure une autre situation.

Une grille pilote raisonnable compare deux tailles de modele et trois fenetres de silence (0.3, 0.6 et 0.9 s), avec trois repetitions par configuration et ordre randomise. Ces valeurs sont proposees pour une nouvelle etude, pas deja executees. Verifier les unites et contraintes du code avant application. Garder la taille de paquet fixe au premier essai.

Pour chaque enonce, journaliser identifiant de session, configuration, materiel, debut/fin de parole connus, declenchement de fin, fin de calcul, envoi serveur, reception et rendu navigateur. Utiliser des durees monotones ; ne pas soustraire des horloges client et serveur non synchronisees. Journaliser aussi silence, resultat vide, rejet et erreur.

Calculer le WER sur la transcription finale reconstituee et les memes references. Presenter mediane, p95, maximum et demarrage par configuration, avec nombre d'observations, taux d'echec et charge systeme. Conserver les ralentissements, investiguer leurs causes avec des traces supplementaires.

Un compromis est un choix entre plusieurs mesures : une configuration peut etre plus rapide mais faire davantage d'erreurs. Ne retenir un choix que selon une contrainte explicite definie pour l'etude. Ni un seuil acceptable pour des utilisateurs malentendants ni une garantie de service ne se deduisent du seul WER.

Critere de cloture : WER et delai de bout en bout mesures sur les memes contenus, repetitions et configurations connues. Les journaux actuels ne suffisent pas.

## 8. Protocole E : reunion simulee dans Teams

Organiser une session d'essai avec participants consentants et paroles sans contenu confidentiel. Preciser comment l'audio atteint le prototype : microphone, capture de sortie ou autre chemin autorise. Une page de transcription ouverte a cote de Teams n'est pas automatiquement une integration Teams.

Documenter appareil, routage, echo, canal, participants, alternance des tours, interruption et changement de langue. Conserver une reference relue et mesurer les sorties comme dans les protocoles precedents. Fournir un compte rendu reproductible avec erreurs observees. Une demonstration visuelle seule ne valide pas la precision.

L'etude utilisateur d'accessibilite releve du Topic 3. Ton livrable reste la transcription exploitable et documentee ; tu ne peux pas conclure a une amelioration mesuree de l'accessibilite sans cette etude.

## 9. Commandes disponibles et fichiers

Depuis la racine du depot, dans PowerShell :

```powershell
.\.venv\Scripts\python.exe -m backend.evaluation.topic2_readiness
.\.venv\Scripts\python.exe -m backend.evaluation.run_statistical_audit --output tmp/topic2_statistical_check.md
.\.venv\Scripts\python.exe -m pytest tests/test_topic2_readiness.py tests/test_statistics.py -q
```

La premiere commande regenere l'audit de latence et l'empreinte du CSV. La deuxieme recalcule les contrastes depuis les CSV ; sa partie latence porte sur toutes les lignes actuelles. La troisieme teste les calculs et la detection des sessions mal formees. Aucune ne lance un modele ASR.

`Memoire_LaTeX/main_revised.tex` est la revision anglaise de travail, avec `bibitem_revised.bib` et `topic2_completion.tex`. Les guides et le support de soutenance utilisent les corrections. Le fichier `main.tex` anterieur et la traduction francaise ne doivent pas etre utilises comme substitutes de cette revision.

## 10. Reponses a comprendre avant de memoriser

**Pourquoi votre sujet parle-t-il de reunions alors que les donnees sont bancaires ?**

Mon objectif concerne les reunions. Mon experience principale isole des composants sur un corpus accessible et controle. Elle repond partiellement au sujet ; la validation externe sur reunions doit encore etre executee. Je distingue cette limite du fonctionnement du prototype.

**Avez-vous valide plusieurs locuteurs ?**

J'ai execute la chaine de diarisation sur des assemblages. Les etiquettes de personnes de ce jeu ne constituent pas une reference d'identite vocale verifiee. Le resultat valide l'integration, pas une precision de reconnaissance des locuteurs.

**Le systeme est-il toujours sous une seconde ?**

Non. L'etude historique avait un p95 serveur de 0.844 s hors premiers enonces. Le journal etendu comporte un maximum de 11.021 s et un p95 de 1.614 s. Il manque une etude controlee du delai jusqu'au navigateur et de la precision associee.

**Votre adaptation ameliore-t-elle le vocabulaire Nestle ?**

Ce n'est pas etabli. Le test principal ne contient pas ce vocabulaire. Le gain LoRA bancaire est petit et son intervalle contient zero. Un test specifique doit mesurer les termes reconnus et les termes ajoutes a tort.

**Pourquoi ne pas annoncer que toutes les insuffisances sont corrigees ?**

Une limite experimentale se leve avec des donnees et des mesures. Les analyses existantes ont ete corrigees et les experiences manquantes sont definies. Je ne presente pas une experience planifiee comme une preuve acquise.

## 11. Routine pour te l'approprier

Jour 1 : dessine audio -> traitement -> texte -> comparaison a la reference. Explique WER avec une phrase de cinq mots et une substitution : 1/5 = 20 %.

Jour 2 : explique les 24 sources et 12 copies. Refais 96.4 - 61.1 = 35.3 et explique pourquoi 47.0 correspond a un autre ensemble.

Jour 3 : ouvre le CSV de latence, retrouve les trois retours a 1 et la ligne 11.021. Lance l'audit puis explique mediane, p95 et maximum sans regarder le guide.

Jour 4 : ouvre `build_meetings.py`, repere A/B et explique pourquoi une etiquette ne garantit pas une voix. Repere dans `eval_meetings.py` la construction de reference et le calcul du DER.

Jour 5 : explique prompt, LoRA et separation apprentissage/evaluation. Formule ce qui reste inconnu sur Nestle.

Jour 6 : presente les trois questions du Topic 2, chacune avec une preuve, une limite et la prochaine experience. Enregistre une presentation de cinq minutes.

Jour 7 : reponds aux cinq questions ci-dessus en anglais puis reformule en francais. Une hesitation indique le passage a revoir. Reviens sur les memes questions deux jours puis une semaine apres.

Pour chaque reponse, garde cet ordre : ce que je cherchais, ce que j'ai fait, ce que j'ai mesure, ce que cela permet de conclure. Tu dois pouvoir retrouver un chiffre dans un fichier et expliquer comment il est calcule.
