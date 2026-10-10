# Audit Topic 2 contre le Research Proposal

Audit du 16 septembre 2026. Racine : `C:\Users\ulric\Documents\ThesisMasterTest`.
Source des attentes : `C:\Users\ulric\Downloads\Research Proposal.pdf`, pages 2–3, section « Topic 2: Advanced Speech-to-Text Models for Noisy, Multilingual Meetings ».

## Verdict

Le projet contient un prototype STT, une revue des approches ASR et une campagne expérimentale réelle. Les résultats enregistrés sont recalculables. La couverture du proposal est **partielle**, principalement faute de validation représentative des réunions et de mesure contrôlée précision/latence. Plusieurs défauts techniques doivent aussi être traités avant une nouvelle campagne.

Il faut distinguer : fonction présente dans le code, exécution observée, performance mesurée et validité pour l'usage entreprise. Aucune note ou probabilité de réussite à la soutenance ne se déduit de cet audit.

## Ce qui est réellement demandé

Le proposal demande de développer un système STT pour réunions et appels vidéo en temps réel, avec plusieurs intervenants, du bruit et plusieurs langues. Il pose trois questions : performance des modèles en contexte bruyant/multilingue, bénéfice des stratégies d'adaptation au domaine, réduction de latence sans sacrifier la précision.

| Attente explicite | Preuves trouvées | État et clôture attendue |
|---|---|---|
| Revue de littérature ASR avancé | `Memoire_LaTeX/main_revised.tex`, chapitre scientifique ; `bibitem_revised.bib` | Présente. Qualité bibliographique non réauditée source par source dans cette intervention. |
| Constituer des données simulant des réunions multilingues avec accents | MInDS-14 : 36 fichiers, 24 références, EN/FR/DE ; 7 assemblages de réunions | Partiel. Parole bancaire à un locuteur, pas de catégories d'accents documentées ni de référence vocale fiable pour les assemblages. Ajouter une évaluation de réunions avec voix/annotations vérifiées. |
| Évaluer des modèles tels que Whisper, wav2vec 2.0, Conformer | 324 lignes pilote, 72 LoRA, 36 MMS, 36 Conformer | Réalisé sur un petit corpus. « Such as » donne des exemples, et non une obligation de fine-tuner chaque architecture. Documenter les langues fournies aux modèles et les périmètres de mesure. |
| Expérimenter la réduction du bruit | Comparaisons avec/sans prétraitement ; 12 variantes bruit blanc, SNR vérifié à 8 dB | Réalisé dans une condition contrôlée ; robustesse générale non démontrée. Ajouter plusieurs bruits/niveaux dans une extension séparée si cette généralisation est revendiquée. |
| Expérimenter la diarisation | `build_meetings.py`, `eval_meetings.py`, 7 scores DER ; chemins live et fichier | Expérience exécutée, référence d'identité insuffisante. Mesurer « qui parle quand » sur de vraies identités stables, y compris chevauchement si revendiqué. |
| Expérimenter l'adaptation au domaine | Prompt Nestlé ; LoRA bancaire, adaptateur et journal d'entraînement présents | Réalisé méthodologiquement, bénéfice sur le domaine cible non établi. Évaluer les termes métier sur un jeu distinct contenant ces termes et des témoins sans ces termes. |
| Minimiser la latence sans perdre en précision | WebSocket, VAD, RTF, 38 lignes de latence serveur | Partiel. Mesurer WER et latence jusqu'au rendu sur les mêmes paroles, plusieurs configurations et répétitions ; conserver échecs et démarrages. |
| Tester le prototype dans des réunions Teams simulées | Pages `/live` et interface principale ; protocole dans `COMPLEMENTS_TOPIC2.md` | Pas de rapport d'essai Teams contrôlé trouvé dans les éléments pertinents inspectés. Exécuter et documenter le routage des voix locales/distantes. |
| Fournir des transcriptions exploitables pour les employés malentendants | Texte/segments, affichage live, export texte | Prototype présent. Utilité utilisateur et système optimisé en entreprise non démontrés. Ne pas confondre affichage du texte et accessibilité validée. |

Le proposal ne donne **aucun seuil chiffré** de WER, DER ou latence, aucun effectif minimal, et n'exige pas un gain LoRA positif. Un résultat négatif correctement analysé répond à une question de recherche. Les effectifs proposés dans le plan de tests sont des pilotes pratiques, pas des obligations contractuelles ni une preuve de puissance statistique.

L'extension Chrome, un connecteur Teams natif, Azure et un déploiement en production ne sont pas des exigences propres au Topic 2. Le test de réunion Teams simulée, lui, est explicite. L'intégration globale Outlook/Teams concerne l'ensemble des topics. OCR = Topic 1 ; personnalisation, études utilisateurs et apprentissage par retours = Topic 3. Le code-switching intra-phrase est un test pertinent pour les affirmations multilingues, mais n'est pas une clause séparée explicitement imposée.

## Parcours du dossier

| Zone | Utilité pour Topic 2 / constat |
|---|---|
| `backend/stt/engine.py` | faster-whisper, prétraitement, sélection CPU/GPU, chargement VAD/pyannote, transcription fichier. |
| `backend/main.py` | Routes fichiers, direct, pages et ingestion RAG ; orchestration et mesures live. |
| `backend/evaluation/` | WER/CER/RTF, chargement corpus, matrices, bootstrap, audit de latence et tableau de preuves. |
| `backend/training/`, `models/lora_small_minds14/` | Construction apprentissage, LoRA et évaluations MMS/Conformer/diarisation ; adaptateur réellement présent. |
| `datasets/stt_eval/`, `datasets/lora_train/`, `datasets/meetings/` | Corpus et annotations effectivement présents. Les 300 fichiers d'apprentissage sont retrouvés. |
| `results/` | Campagne principale, copies CPU/GPU, LoRA/MMS/Conformer, latence et diarisation. Les sauvegardes ne sont pas de nouvelles observations indépendantes. |
| `datasets/fleurs_eval/`, `results/stt_eval_fleurs_results.csv` | Extension existante de 300 résultats, distincte du corpus principal. Ses échecs/répétitions doivent rester visibles si on la réanalyse ; ne pas la fusionner silencieusement à MInDS-14. |
| `audioReunionréel/` | Audios de réunions, assemblées, appels et PDF. Ressources candidates ; présence d'un audio ou d'un discours écrit ne garantit pas un verbatim aligné. |
| `frontend/index.html`, `live_transcribe.html`, `research.html` | Interfaces opérationnelles prévues pour import, direct et consultation des preuves. |
| `frontend/accessibility_prototype.html` | Contient de la simulation (dont export via alerte), à distinguer des pages connectées au backend. |
| `tests/` | 51 tests existants, axés métriques, métadonnées, runner et tableau de preuves ; pas de validation complète réelle ASR/Teams. |
| `Memoire_LaTeX/main_revised.tex`, `topic2_completion.tex` | Texte de travail à utiliser. Résumé anglais distingue l'étude historique de latence ; résumé français au début du même fichier garde encore une formulation moins explicite sur ce point. |
| `ETAT_ACTUEL.md`, `COMPLEMENTS_TOPIC2.md`, audits antérieurs | Repères utiles, mais vérifiés contre fichiers et code. Certaines formulations sont périmées : commentaire VAD « omis » dans `run_pilot_matrix.py` alors que la condition C existe ; commentaire audio « déjà 16 kHz » dans Conformer alors que les WAV contrôlés sont à 8 kHz. |
| `_archive/`, anciens DOCX/Markdown/LaTeX, `appsexemple/`, `topic1/` | Versions anciennes, exemples externes ou autres topics ; ne constituent pas automatiquement la version soutenue ou une fonctionnalité implémentée. |

Audit ciblé sur les fichiers et chaînes pertinents au Topic 2, pas écoute exhaustive de tous les audios ni audit de chaque fichier tiers.

## Vérifications effectivement exécutées

- Suite existante : **51 passed**, 0 échec. Avertissement `cache_dir` dû à la désactivation volontaire du plugin cache pendant cette exécution.
- 468 lignes de résultats principales rescorrées avec le scorer actuel : écart maximal WER **0,0000462**, compatible avec l'arrondi à quatre décimales ; aucune référence/hypothèse vide ni erreur déclarée dans ces lignes ; aucun doublon par fichier/condition au sein de chaque CSV.
- 36 audios et 24 fichiers de référence présents ; tous les audios à **8 kHz** ; SNR mesuré des 12 copies bruitées entre environ **7,9999 et 8,0001 dB**.
- 300 audios LoRA présents, 100 par langue. Aucun recoupement exact des textes normalisés ni des empreintes de fichiers avec l'évaluation. Cela ne garantit pas l'indépendance des voix ni l'absence de quasi-doublons.
- Bootstrap relancé : effet bruit **+35,3 points [7,0 ; 60,0]** ; gain LoRA **1,0 point [−2,4 ; 5,3]**.
- Journal live réanalysé : 38 observations, dont 35 hors premiers énoncés ; médiane **0,575 s**, p95 **1,614 s**, maximum **11,021 s**, temps serveur après détection de fin de parole uniquement.
- Deux sondes de contrat exécutées avec ASR/VAD/RAG simulés : elles reproduisent les défauts de passage de langue et de vidage du buffer ; elles ne mesurent aucune qualité ASR.
- Test réel limité de l'ASR CPU : **4 inférences achevées**, tiny CPU/int8 sans prompt ni débruitage, voir `smoke_cpu.json` et `SMOKE_CPU.md`. Une phrase FR propre est correcte selon sa référence ; les autres sorties présentent des erreurs, dont deux mauvaises langues détectées. Son périmètre est explicitement isolé de la diarisation, du navigateur, du RAG et de Teams.

Recalculer un WER prouve la cohérence entre référence et hypothèse stockées, pas la fidélité de la référence à l'audio. Une vérification à l'écoute reste indispensable pour de nouvelles données. Les chiffres sont des moyennes de WER par fichier, pas nécessairement un WER agrégé sur tous les mots.

## Défauts et risques avant nouvelle campagne

### Confirmés par sonde ou fichiers

1. **Langue de l'import non transmise comme attendu.** `frontend/index.html:791` envoie `language` en formulaire multipart ; `backend/main.py:128` attend un paramètre de requête. Sonde : formulaire `fr` -> moteur reçoit `None` ; URL `?language=fr` -> moteur reçoit `fr`. Un choix dans le menu ne prouve donc pas que la langue a été forcée. Corriger le contrat puis le retester avant les comparaisons.
2. **Audio final non vidé sur déconnexion.** `RealTimeSTTHandler.process` ne transcrit qu'après silence. Sonde : un bloc parlé d'une seconde suivi d'une déconnexion laisse **32 000 octets** en attente et **0 appel** de transcription. Les pages arrêtent aussi le micro sans envoyer de message de fin garantissant un vidage. Tester arrêt immédiat, silence final et reconnexion.
3. **Écrasement des fichiers texte auxiliaires.** `backend/evaluation/runner.py` construit les noms avec prétraitement/prompt/langue, sans modèle ni VAD. **72 chemins partagés** ; **219 hypothèses de lignes diffèrent du fichier texte actuellement désigné**. Les colonnes `reference_text` et `hypothesis_text` des CSV permettent toujours le recalcul. Toute nouvelle expérience doit avoir ses propres sorties et des identifiants complets.

### Limites établies par lecture, incidence à mesurer

4. **LoRA absent du moteur applicatif.** L'adaptateur est utilisé dans `eval_lora.py`, pas chargé par `backend/stt/engine.py` ni le direct. L'application live n'est pas une démonstration du modèle LoRA. L'intégrer n'est nécessaire que si ce comportement est annoncé.
5. **Chemins fichier/direct différents.** Fichier : débruitage et prompt par défaut ; direct : VAD, pas de prompt, pas du même prétraitement. Ne pas transposer un score fichier au live.
6. **Chronomètres différents.** Le temps renvoyé par `transcribe_file` exclut chargement initial et diarisation ; le runner englobe l'appel complet ; certains benchmarks dédiés chronomètrent l'inférence après échauffement. Aucun classement strict de vitesse n'est honnête sans harmoniser ces périmètres.
7. **Attente de silence non égale à un délai fixe perçu de 0,6 s.** Les pages envoient des blocs d'environ une seconde ; le VAD décide à l'échelle du bloc. La mise en paquets peut ajouter une attente. Il faut mesurer jusqu'au rendu, pas simplement additionner 0,6 au CSV.
8. **Diarisation live locale à une fenêtre.** Dernières 10 secondes, dernier label attribué à l'énoncé ; pas de suivi explicite d'identités globales. Les silences hors énoncés sont exclus du compteur temporel. Vérifier stabilité A/B/A, deux voix dans un même énoncé et correspondance des horodatages à l'enregistrement.
9. **Compatibilité pyannote fichier à retester.** Le live et `eval_meetings.py` gèrent `speaker_diarization` des sorties récentes ; le chemin fichier appelle directement `itertracks`. Selon le retour réel de la version installée, l'erreur pourrait être capturée et laisser les locuteurs vides. C'est un risque, pas un échec d'inférence démontré ici.
10. **Erreurs live peu visibles.** Silence faible, texte vide et répétitions rejetées peuvent sortir avant journalisation ; une erreur de diarisation peut interrompre l'envoi du texte. Les tests doivent compter aussi les paroles sans résultat.
11. **Exécution longue et concurrente à tester.** Générateur de segments consommé dans la coroutine après appel de `transcribe`, VAD partagé et mémoire audio accumulée : candidats à blocages/interférences/croissance mémoire. Ne pas revendiquer plusieurs utilisateurs ou réunions longues sans mesure.
12. **Configuration matériel.** `load_model()` choisit CUDA si disponible, sinon CPU/int8. Le bouton ou le nom du modèle ne prouve pas le matériel réellement utilisé. Les prochaines sorties doivent enregistrer matériel et précision.
13. **Avertissement de décodage pyannote observé.** L'import réel signale que les bibliothèques TorchCodec ne se chargent pas et que le décodage intégré échouera. La cause exacte (DLL, compatibilité ou dépendance) n'a pas été isolée. Le chemin fichier doit être essayé avec la diarisation active ; le passage d'un waveform déjà décodé constitue un chemin différent. Le test ASR réalisé désactive explicitement la diarisation et ne clôt pas ce point.
14. **Référence anglaise à vérifier à l'écoute en priorité.** Dans `minds14_en_clean_01`, le smoke test et plusieurs hypothèses historiques contiennent une proposition finale absente du texte de référence (« how do I proceed… »). Cela pourrait être une insertion du modèle ou une référence incomplète : l'accord de modèles ne permet pas de trancher. Écouter l'audio avant toute conclusion sur ce cas ; si la référence change, conserver l'original et rescorrer toutes les configurations dans une révision séparée.

Ces constats ne signifient pas que toutes les fonctions échouent. Ils déterminent ce qu'il faut vérifier avant d'affirmer leur validité.

## Ce que tu peux dire aujourd'hui

« J'ai construit un prototype et comparé plusieurs modèles et stratégies sur un corpus contrôlé trilingue. J'ai mesuré l'effet du bruit et un gain LoRA incertain. La représentativité des réunions, l'adaptation au vocabulaire cible et le compromis de bout en bout précision/latence demandent une validation complémentaire. »

Éviter : « modèle optimisé pour Nestlé », « LoRA améliore les noms Nestlé », « diarisation fiable à 41,5 % », « toujours sous une seconde », « RTF faible donc adapté aux malentendants », « conformité complète au proposal ». Une intégration ou une extension supplémentaire ne remplace pas ces mesures.

Suite opérationnelle : `PLAN_TESTS_ET_RETOUR.md`. Consigne prête à transmettre à Antigravity : `PROMPT_ANTIGRAVITY.md`.
