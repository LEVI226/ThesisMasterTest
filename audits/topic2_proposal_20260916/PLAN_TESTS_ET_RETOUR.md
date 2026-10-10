# Plan concret de tests — Topic 2

À lire après `AUDIT_TOPIC2.md`. Objectif : produire des preuves, y compris d'échec, comparables au proposal. Un test manuel est recevable s'il conserve l'audio, la référence, les conditions et le résultat. « Ça marche » ou une capture seule ne mesure pas la précision.

## Ordre de travail

1. **P0 — Fiabiliser le banc de test** : passage de langue, arrêt de microphone, chemins de résultats uniques, configuration et journalisation. Conserver un résultat avant/après pour chaque correction.
2. **P1 — Valider le cœur promis** : référence de réunion fiable, plusieurs locuteurs, transcription en direct, mesure précision/latence et essai Teams.
3. **P1 — Vérifier l'adaptation métier** : test avec termes professionnels et témoins ; prompting séparé du LoRA.
4. **P2 — Étendre la portée des conclusions** : code-switching, accents documentés, plusieurs bruits/niveaux, sessions longues et stabilité.

Tous les nouveaux résultats vont dans `audits/topic2_validation/<run_id>/`. Préserver les résultats historiques, les modèles entraînés et le corpus principal. Les scripts pilotes existants écrivent parfois dans des chemins fixes : les adapter ou les isoler avant de les relancer. Ne pas simplement relancer `run_pilot_matrix.py` dans le dossier principal.

Les nombres ci-dessous sont des volumes pilotes proposés. Aucun ne rend automatiquement l'étude suffisante pour généraliser à Nestlé. Si le temps est court, terminer moins d'essais mais conserver leurs preuves complètes.

## T0 — Fonctionnement des commandes et du prototype

À faire par Antigravity, puis vérifier visuellement les commandes utilisées pendant la démonstration.

- Vérifier import WAV puis un MP3/M4A réellement décodable ; résultat non vide et langue réellement transmise.
- Vérifier accès aux pages `/`, `/live`, `/research`. Ne pas utiliser la maquette `accessibility_prototype.html` comme preuve d'une fonction serveur.
- Vérifier auto/fr/en/de : tracer la valeur reçue par le moteur, pas seulement lire la sortie.
- Tester arrêt immédiat après le dernier mot, arrêt après deux secondes de silence, déconnexion puis reconnexion ; compter les mots finaux perdus et les doublons.
- Tester silence pur puis voix faible ; absence d'hallucinations ET absence de suppression excessive de voix faible.
- Si diarisation indisponible : l'état doit être explicite ; distinguer texte transcrit et identification de locuteur absente.
- Exporter le texte et vérifier qu'il correspond au texte affiché, accents et dernières phrases compris.
- Vérifier le modèle réellement chargé, CPU/GPU, int8/float16 ; confirmer séparément si LoRA est chargé. Ne pas prétendre que le prototype utilise l'adaptateur sans le vérifier.

Preuves : journal, étapes, réponse API, capture ou courte vidéo de l'interface ; test avant/après pour toute correction. Critère logiciel : paramètres reçus identiques à la sélection, aucune dernière phrase perdue dans le scénario défini, erreurs déclarées. Ce critère n'est pas une exigence chiffrée du proposal.

## T1 — Réunion et diarisation avec vraies identités

Pilote : trois enregistrements de 3–5 minutes avec 2–3 personnes consentantes, sur des sujets de travail non confidentiels. Viser davantage de réunions indépendantes ensuite ; trois réunions ne suffisent pas à une conclusion générale.

- Réunion A : tours séparés, pauses et retour du locuteur initial A/B/A.
- Réunion B : quelques interruptions et chevauchements explicitement annotés.
- Réunion C : alternance de langues réellement maîtrisées par les participants ; ne pas confondre langue différente et personne différente.
- Conserver une piste audio continue, sans retirer les silences du fichier de référence.
- Construire à l'écoute `start_s`, `end_s`, `speaker_id`, `text`, `language`. Vérifier les mots exacts et l'identité stable des personnes avant de consulter les prédictions.
- Faire comparer les mêmes audios par le modèle de référence et la configuration retenue. Donner exactement le même nombre de locuteurs aux configurations si cette information est utilisée, et le déclarer.
- Calculer WER et DER avec définition du collar/tolérance et du traitement des chevauchements. Ne pas appeler « accuracy » le complément du DER.
- Conserver les sorties de diarisation brutes (RTTM/JSON), pas seulement un score. Si possible ajouter une métrique de mots attribués aux locuteurs avec une implémentation de référence ; ne pas rebaptiser un WER ordinaire en cpWER/tcpWER.

Retour minimum : audio, annotation de référence, sorties par modèle, scores par réunion, erreurs et configuration. Des identités A/B arbitraires selon le numéro du clip ne conviennent pas.

## T2 — Adaptation métier : prompting puis LoRA

Pilote : 20 phrases contenant des termes cibles + 20 phrases témoins sans ces termes. Les nombres sont exploratoires ; répartir par langue si plusieurs langues sont revendiquées.

- Avant le test, définir un glossaire de termes réellement utiles, les variantes orthographiques acceptées et des phrases que des personnes prononceront.
- Conserver voix et phrases d'évaluation distinctes des données utilisées pour ajuster le modèle ou le prompt.
- Comparer le même modèle, sur les mêmes fichiers, sans prompt puis avec prompt. Ne changer aucune autre option. Ne jamais fournir toute la transcription attendue comme prompt.
- Mesurer WER, nombre d'occurrences cibles, termes correctement reconnus et termes ajoutés à tort dans les témoins.
- Pour LoRA : comparaison base/adaptateur sur le même backend et décodeur. L'adaptateur bancaire existant peut être testé, mais ne devient pas « entraîné Nestlé ». Un nouvel entraînement demande un jeu distinct et sa traçabilité.
- Conserver les résultats où l'adaptation dégrade la sortie. Une absence de gain est un résultat, pas un test à supprimer.

Retour : glossaire figé, audios, références, sorties sans/avec prompt, éventuelle comparaison LoRA séparée, configuration et comptage des termes. Pour « Navratil devient Naruto », fournir le même audio et les sorties avant/après ; sinon c'est une observation anecdotique.

## T3 — Bruit

Pilote : 10 extraits propres réservés, leurs variantes avec deux bruits distincts documentés (par exemple clavier et voix concurrentes) à deux SNR fixés avant l'essai. Ces nouveaux SNR ne remplacent pas les 8 dB historiques.

- Faire calculer le SNR, contrôler saturation et mêmes durées ; enregistrer la source/licence du bruit et la graine.
- Comparer sans/avec débruitage sur chaque version, en gardant modèle, langue et décodage identiques.
- Rapporter les scores sur propre aussi : le débruitage peut détériorer les mots.
- Conserver ensemble les dérivés du même audio dans les analyses statistiques.
- Si tu utilises seulement un ventilateur réel ou du bruit via haut-parleur : noter la configuration, mais ne pas inventer un SNR précis. La réduction de bruit du navigateur peut aussi intervenir.

Retour : fichiers propres/bruités, source bruit et réglages, mêmes références, sorties et scores appariés. La réverbération est une autre condition, non validée par ce seul mélange additif.

## T4 — Changements de langue et accents

Ton observation « quand je mélange les langues, ça casse » devient exploitable si elle est enregistrée.

Pilote : dix phrases FR/EN mélangées + dix phrases monolingues témoins, prononcées par les mêmes personnes. Annoter les changements. Exemple de contenu de test : « On valide the delivery date demain matin. » Ce texte est un stimulus proposé, pas une transcription observée.

- Tester auto puis langue forcée sur les mêmes fichiers ; une langue forcée unique est un contrôle, pas la solution présumée au code-switching.
- Employer `task=transcribe` pour la comparaison ; une traduction n'est pas une transcription fidèle de la langue originale.
- Classer les échecs : mots manquants, traduction involontaire, mauvaise langue, répétition, texte absent, erreur logicielle.
- Mesurer WER global et examiner les mots proches des transitions. Ne pas déduire une exactitude de détection de langue de l'accord auto/forcé.
- Pour les accents : obtenir plusieurs personnes et noter leur profil linguistique avec leur accord, sans déduire une origine de leur voix. Un essai avec ta voix renseigne sur ta voix ; il ne valide pas tous les accents ouest-africains.

Retour : audio, référence, sortie, mode auto/forcé, personne/session, fréquence comptée des types d'erreurs (ex. 4/10), pas « souvent » seul.

## T5 — Précision et latence de bout en bout

À préparer par Antigravity, puis exécuter sur le même chemin navigateur/WebSocket que la démonstration.

Pilote : mêmes 10 énoncés réservés, deux modèles raisonnables pour la machine, trois répétitions par configuration ; ordre alterné/randomisé. Commencer avec le même seuil de silence. Une deuxième passe peut comparer 0,3/0,6/0,9 s après vérification des contraintes du code.

- Envoyer l'audio à vitesse réelle ; un fichier transmis aussi vite que possible n'est pas une simulation live.
- Consigner taille réelle des paquets, fréquence d'échantillonnage, options micro du navigateur, modèle, backend, matériel, précision numérique, diarisation activée ou non, charge et versions.
- Pour chaque énoncé : fin de parole connue, fin de détection, fin du calcul, envoi serveur, réception puis affichage. Utiliser une horloge commune ou une synchronisation démontrée ; ne pas soustraire directement des horloges client/serveur indépendantes.
- Solution manuelle : enregistrer l'audio et l'écran dans une même vidéo, puis mesurer l'écart entre dernier son et premier rendu du texte correspondant. Déclarer la précision de lecture et les limites de capture.
- Conserver la transcription finale complète et sa référence pour calculer le WER sur les mêmes contenus que la latence.
- Rapporter médiane, p95, maximum, première phrase séparée, nombre de répétitions et paroles sans résultat. Les essais sans sortie restent des échecs, pas des latences nulles à supprimer.
- Sur au moins une session prolongée (par exemple 10 minutes), vérifier accumulation de retard, mémoire, perte de phrases et changement des identifiants de locuteurs.

Retour : observations individuelles et configurations, pas uniquement les moyennes. On ne peut parler de « compromis » qu'en comparant ensemble vitesse et erreurs. Si un seuil d'usage est choisi, le définir avant de regarder les résultats et expliquer son origine ; il ne vient pas du proposal.

## T6 — Réunion Teams simulée

Pilote : deux essais de 5 minutes avec interlocuteur distant, mêmes étapes. Participants informés, contenu de test non confidentiel.

- Consigner comment le prototype reçoit le microphone local ET les voix distantes (micro, loopback, audio partagé, dispositif virtuel, etc.).
- Faire parler séparément le participant local et le distant, puis alterner, puis provoquer une interruption ; vérifier échos et doublons.
- Conserver le son effectivement reçu par le prototype ainsi qu'une référence des paroles attendues. Si une voix distante n'arrive pas dans l'entrée, c'est un problème de capture à distinguer des erreurs ASR.
- Mesurer mots manquants, WER, délai et attribution des locuteurs selon les protocoles précédents.
- Capturer une courte vidéo, export final et logs. Ouvrir Teams à côté du prototype ne constitue pas à lui seul un test de transcription de l'appel.

Une capture audio autorisée pour un essai peut suffire à tester le prototype en réunion simulée ; elle n'est pas une intégration native Teams et ne doit pas être présentée comme telle.

## Ressources déjà disponibles

Le dossier `audioReunionréel/` contient notamment :

- `Investor & analyst call Nestlé Half-year results 2025.mp3` et `half-year-results-investor-call-transcript-2025.pdf` : premier couple candidat à vérifier par écoute ; un PDF édité peut différer du verbatim. Extraire des fenêtres continues avec timestamps et corriger la référence avant scoring.
- Audios AGM 2026 EN/FR/DE : utiles éventuellement pour parole institutionnelle ou interprétée. La langue du nom de fichier ne suffit pas à prouver son contenu ; les traductions d'un même événement ne sont pas des réunions indépendantes.
- `speeches-annual-general-meeting-2025-en.pdf` : ne pas l'aligner automatiquement avec un audio 2026.
- Enregistrements `.m4a` datés et `Reunion Dhis2.m4a` : candidats seulement après clarification de l'usage autorisé, de la langue et des personnes ; à conserver localement. Aucun upload externe requis pour cet audit.

Commencer par 2–3 extraits courts dont la référence peut être vérifiée. L'absence de données Nestlé de production n'empêche pas un test de réunion contrôlé ou de vocabulaire lu ; déclarer précisément ce que chaque donnée représente.

## Ce que tu dois me retourner

Un dossier par session contenant :

```text
run_id/
  manifest.json             # date, version, machine, configuration, origine
  audio/                    # audio réellement soumis au prototype
  references/               # verbatim relu AVANT analyse des prédictions
  hypotheses/               # sorties brutes, une par configuration
  observations.jsonl        # une ligne par essai, y compris échecs
  speakers.json             # si plusieurs personnes : temps et identités
  logs/                     # stderr/stdout, configuration effective
  evidence/                 # vidéo/captures utiles pour le comportement live
  SUMMARY.md                # ce qui a été testé, résultat, limites
```

Dans chaque observation : `test_id`, `run_id`, `audio_file`, `reference_file`, `hypothesis_file`, `model`, `backend`, `device`, `compute_type`, `language_mode`, `prompt_enabled`, `prompt_text`, `denoise_enabled`, `vad_enabled`, `diarization_enabled`, `repeat`, `audio_duration_s`, `processing_scope`, `processing_s`, `end_to_end_s`, `status`, `error`, `notes`. Utiliser `null` si non mesuré, jamais 0 par défaut. Les métriques seront recalculées à partir des textes.

Pour un retour manuel simple : « T4, auto, modèle X, phrase 03, voici audio + texte attendu + résultat ; le français a été traduit en anglais ». Je pourrai alors vérifier le résultat et t'aider à le défendre.

Ne pas corriger l'hypothèse avant scoring. Si la référence doit être corrigée après découverte d'une annotation erronée, documenter la correction et rescorrer toutes les configurations, sans écraser l'ancienne version.
