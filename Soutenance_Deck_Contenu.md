# Contenu du deck de soutenance — Topic 2 STT

> Pour Claude Design : 1 idée par slide, les tableaux sont les héros (reproduire fidèlement, chiffres exacts). Palette sobre corporate/BIT. Les blocs « Note orateur » ne vont PAS sur les slides — ils servent à la répétition. 18 slides principales + 6 backups (après « Merci », montrées uniquement sur question du jury). Durée cible ~22 min.

---

## Slide 1 — Titre
**Advanced Speech-to-Text Models for Noisy, Multilingual Corporate Meetings**
Evaluation of a Whisper-Based Pipeline for Workplace Accessibility

- OUEDRAOGO Yannick Ulrich Levi — Master Artificial Intelligence
- Burkina Institute of Technology (BIT) · Collaboration Nestlé/BIT
- Encadrant : Dr.-Ing. Lebian Wilfried NIKIEMA
- [Date de soutenance]

*Note orateur : 15 s. « J'ai mesuré, plutôt que supposé, ce qu'un pipeline de transcription open-source peut faire pour les employés malentendants en réunion d'entreprise. »*

---

## Slide 2 — Le problème humain
**Pour un employé malentendant, le transcript n'est pas un confort — c'est l'accès à la réunion.**

- Réunions multinationales : bruit de fond, alternance EN/FR/DE, vocabulaire métier
- Ce sont exactement les conditions où les ASR généralistes se dégradent
- Les chiffres publiés (benchmarks propres, monolingues) ne disent pas ce qui se passe en vraie réunion
- Contexte : plateforme d'accessibilité Nestlé/BIT à 3 volets — OCR / **STT (mon sujet)** / personnalisation

---

## Slide 3 — Question de recherche & objectifs
**Objectif général : évaluer et optimiser, en conditions contrôlées et reproductibles, un pipeline STT Whisper CPU pour l'audio de réunion bruité et multilingue.**

- SO1 — Construire un dataset d'évaluation multilingue avec vérité terrain (propre + bruité)
- SO2 — Implémenter un pipeline configurable (prétraitement, prompt métier, langue forcée, VAD)
- SO3 — Mesurer WER/CER/RTF et interpréter honnêtement, résultats négatifs compris

4 questions : effet du bruit ? · stratégies d'adaptation ? · fiabilité de la détection de langue ? · précision vs vitesse selon la taille du modèle ?

---

## Slide 4 — Positionnement
**Le créneau : personne ne mesure les trois difficultés EN MÊME TEMPS sur un pipeline réellement déployable.**

- Robustesse au bruit / adaptation de domaine / diarisation : abondamment étudiées, mais isolément
- Rare : UN pipeline CPU tenu fixe, où l'on mesure l'**effet marginal** de chaque technique sur le même dataset
- Design en conditions chaînées : chaque comparaison adjacente isole exactement une intervention

*Note orateur : réponse à « quelle est votre contribution ? ». Tableau de synthèse critique en backup (B1).*

---

## Slide 5 — Démarche
**Six étapes, hypothèses fixées AVANT de mesurer (pré-enregistrement).**

1. Revue de littérature → 2. Dataset (MInDS-14 + bruit contrôlé) → 3. Pipeline faster-whisper → 4. Conditions & hypothèses H1-H4 spécifiées → 5. Campagne (468 runs) → 6. Analyse contre les hypothèses

- H1 : réduction de bruit aide sans coûter · H2 : prompt métier aide sur les entités · H3 : RTF < 1 sur CPU · H4 : forcer la langue bat l'auto-détection

*Note orateur : pré-enregistrement = on ne peut pas m'accuser d'avoir ajusté les hypothèses après coup. H1 partielle, H2 non testable, H3 confirmée, H4 fortement confirmée — je l'assume d'avance.*

---

## Slide 6 — Le système construit
**Plateforme 100 % locale (Phase 1) — l'audio ne quitte jamais la machine.**

- Backend FastAPI : `/transcribe` (batch) + `/ws/transcribe` (live, VAD Silero, langue paramétrable)
- Moteur : faster-whisper (INT8 CPU / float16 GPU) · prétraitement noisereduce · prompt métier optionnel
- Diarisation pyannote · couche RAG (ChromaDB + Ollama) : interroger une réunion passée
- Choix local = souveraineté des données, même logique que NesGPT chez Nestlé

*Note orateur : « pourquoi pas Copilot ? » → 3 étages : souveraineté, accessibilité-first, mesurabilité (backup B6).*

---

## Slide 7 — Dataset & protocole
**36 échantillons, 3 langues, 2 conditions de bruit — vérité terrain réelle.**

- MInDS-14 (CC-BY-4.0) : parole téléphonique spontanée réelle — 8 propres + 4 bruités (SNR 8 dB) × EN/FR/DE
- Bruit synthétique sur les MÊMES énoncés → isole l'effet du bruit du contenu
- Conditions chaînées : A base → B +noisereduce → C +VAD → D +prompt → E +langue forcée · F-I : échelle de tailles
- **468 runs** (180 CPU pré-spécifiés + 288 extensions GPU), incluant MMS et Conformer, traçables aux CSV

*Note orateur : pourquoi pas un corpus Nestlé ? Confidentiel, non disponible — substitution documentée. Ne jamais dire « pour prouver que ça marche ».*

---

## Slide 8 — Résultat 1 : effet du bruit sur les mêmes phrases
**Sur 12 paires, le bruit ajoute 35,3 points de WER ; IC 95 % [7,0 ; 60,0].**

| Condition A (tiny) | WER |
|---|---|
| Audio propre apparié (12 fichiers) | 61,1 % |
| Audio bruité (8 dB) | 96,4 % |

- Réduction de bruit : −8,3 pts sur bruité, MAIS +2,2 pts sur propre → vrai compromis
- VAD : effet miroir — aide sur propre (−3,8), dégrade sur bruité (+6,0)
- **Conclusion : aucun interrupteur de prétraitement n'est activable aveuglément**

*Note orateur : H1 partielle — la nuance (coût sur propre) n'était pas anticipée, et c'est un résultat, pas un échec.*

---

## Slide 9 — Résultat 2 : forcer la langue (le résultat phare)
**L'auto-détection échoue sur 42 % des clips français — parfois catastrophiquement.**

- Taux de désaccord auto vs forcé : EN 0 % · DE 17 % · **FR 42 %**
- Exemple réel : « bonjour je voudrais changer d'adresse » → transcrit **en cyrillique** (puis hébreu, turc, chinois ailleurs)
- Forcer `fr` récupère un texte français lisible dans 100 % des cas — **coût : zéro**
- Le WER agrégé bouge peu (cyrillique et français-inexact sont tous deux « loin » de la référence) → gain qualitatif, d'où l'importance de rapporter les deux

*Note orateur : H4 fortement confirmée. Recommandation immédiate : forcer la langue par réunion/canal.*

---

## Slide 10 — Résultat 3 : la taille du modèle est le levier dominant
**Courbe strictement monotone sur 5 tailles — rendements décroissants après medium.**

| Modèle | Params | WER | WER bruité | RTF (GPU) |
|---|---|---|---|---|
| tiny | 39M | 62,2 % | 88,1 % | 0.144 |
| base | 74M | 48,3 % | 79,2 % | 0.188 |
| small | 244M | 33,3 % | 56,7 % | 0.146 |
| medium | 769M | 25,9 % | 43,3 % | 0.195 |
| large-v3 | 1.55B | **24,6 %** | **40,7 %** | 0.359 |

- La taille fait plus contre le bruit (88→41 %) que tout prétraitement explicite
- **small = meilleur rapport précision/coût · medium = sweet spot si GPU**

*Note orateur : piège — RTF de ce tableau tous GPU fp16 (backend constant). Sur CPU, seuls tiny/base mesurés (<1).*

---

## Slide 11 — Résultat 4 : adaptation — prompting ET fine-tuning mesurés
**Les deux stratégies à bas coût atterrissent au même endroit : ≈ 1 point.**

- Prompt métier : −0,9 pt WER... et un risque mesuré : hallucination « Nestlé Ghana » injectée dans une transcription allemande (prompt leakage)
- LoRA fine-tuning (300 clips, contamination vérifiée, éval appariée) : −1,0 pt ; par fichier 7↑ 6↓ 23=
- Raison : le domaine d'entraînement était déjà couvert par le pré-entraînement de Whisper → peu d'écart à combler
- **La valeur du fine-tuning se joue sur du vocabulaire réellement divergent (Nestlé) — non testable ici, confidentialité déclarée**

*Note orateur : H2 non testable telle que formulée — on a mesuré le COÛT du prompting, pas son bénéfice. Réponse RQ2 : adaptation ≈1 pt, ordre de grandeur sous la taille de modèle.*

---

## Slide 12 — Temps réel
**Étude historique : médiane 0,56 s, p95 0,84 s, maximum 1,18 s sur 20 observations hors premiers énoncés.**

Le journal actuel contient 38 observations : hors premiers énoncés, n=35, médiane 0,575 s, p95 1,614 s, maximum 11,021 s. Sessions non caractérisées dans le CSV ; ce résumé est descriptif. Le délai est mesuré côté serveur avant envoi, sans le rendu navigateur ni la fenêtre de silence. Aucun optimum précision/latence n'est établi.

- Chemin WebSocket : VAD Silero segmente, transcription du buffer à la fin d'énoncé
- Délai perçu ≈ 1,2 s (latence + fenêtre de silence 0,6 s) — hors cold-start (~3 s, mitigé par pré-chargement)
- RTF < 1 sur 93,9 % des 180 runs CPU → temps réel tenable SANS GPU pour tiny/base
- Répond à la RQ3 du proposal

*Note orateur : mesure informelle (22 énoncés) — pas de WER rapporté, pas de vérité terrain, et je le dis avant qu'on me le demande.*

---

## Slide 13 — Extensions : wav2vec 2.0 et diarisation
**Les deux dernières promesses du proposal, mesurées — pièges déjoués.**

- **MMS-1B (wav2vec 2.0)** : WER 35,4 % vs Whisper-small 31,2 % ; parité sur bruité ; 10× plus rapide (CTC) — MAIS confound déclaré : MMS reçoit la langue par construction (≈ langue forcée) → une partie de son avantage FR, c'est mon finding H4 dans une autre architecture
- **Diarisation pyannote, 7 réunions simulées** : DER 0,585 — chiffre qui mesure l'artificialité du testbed, pas pyannote : la « sur-segmentation » = pyannote a raison (vrais locuteurs différents) ; preuve : les réunions bruitées ont un « meilleur » DER — impossible pour un vrai gain
- Pipeline diarisation fonctionnel de bout en bout ; éval valide ⇒ vraies réunions (données confidentielles)

*Note orateur : la slide « je sais lire des métriques ». Si le jury creuse le DER, dérouler les 3 preuves.*

---

## Slide 14 — Ce que Nestlé peut faire dès lundi
**Trois recommandations chiffrées, une par levier.**

1. **Modèle : small (CPU costaud) ou medium (GPU)** — le levier n°1, mesuré sur 5 tailles
2. **Forcer la langue par réunion/canal** — coût zéro, corrige les échecs catastrophiques du français
3. **Prétraitement : à activer selon la salle**, pas globalement (noisereduce aide en salle bruyante, coûte en salle calme ; VAD, l'inverse)
- Architecture 100 % locale = compatible avec la doctrine de souveraineté qui a produit NesGPT ; Phase 2 Azure = intention documentée, non réalisée

*Note orateur : slide « impact ». Rester sobre : pas de ROI inventé, pas de chiffres business.*

---

## Slide 15 — Limites (assumées, pas subies)
**Chaque limite est déclarée dans le mémoire, à l'endroit où elle agit.**

- Échelle pilote : 36 clips → findings directionnels, pas d'intervalles de confiance
- Bruit synthétique (blanc, 8 dB) ≠ brouhaha réel, réverbération, codec
- Pas de données Nestlé (confidentialité) → bénéfice du prompt métier non mesurable
- Réunions simulées séquentielles → cross-talk non testé
- 1 run par paire → RTF indicatifs
- Gaps d'implémentation du pilote (VAD non câblé, langue non loggée) : **découverts, déclarés, puis corrigés et mesurés**

*Note orateur : la dernière ligne est la botte secrète — les gaps sont devenus des conditions mesurées.*

---

## Slide 16 — Conclusion
**Ce mémoire apporte 468 transcriptions traçables sur un corpus contrôlé.**

- Le bruit ajoute 35,3 points sur 12 paires ; la taille du modèle apporte le plus grand gain de précision observé
- La taille du modèle est le levier n°1 (63 → 25 % WER) ; l'adaptation à bas coût pèse ≈ 1 pt
- Forcer la langue : le gain le plus actionnable, coût zéro
- Un pipeline temps réel local fonctionne (médiane 0,56 s) — sans cloud, sans fuite de données
- Méthode : hypothèses pré-enregistrées, comparaisons appariées à backend constant, chaque chiffre traçable au CSV

---

## Slide 17 — Perspectives
**Le pipeline est prêt pour la question suivante.**

- Fine-tuning LoRA (machinerie validée) sur du vocabulaire réellement divergent : glossaires de marques, comptes-rendus écrits (text-only fine-tuning)
- RTF CPU des tailles small+ → déployabilité sans GPU
- Vraies réunions multi-locuteurs → évaluation valide de la diarisation et du cross-talk
- Intégration Teams/Outlook (Phase 2) + couche personnalisation (Topic 3)

---

## Slide 18 — Merci
**Questions bienvenues.**

- OUEDRAOGO Yannick Ulrich Levi · Master AI, Burkina Institute of Technology
- Code, données et 468 runs : dépôt Git du projet ; chaque chiffre doit être associé au CSV et à son périmètre

*Note orateur : respirer. Tu as construit, mesuré et compris chaque pièce. Les questions sont des occasions.*

---
---

# SLIDES BACKUP (après « Merci », uniquement sur question du jury)

---

## Slide B1 — Backup : Synthèse critique de l'état de l'art
**5 familles d'approches, forces et limites (Chapitre I, Table I.1)**

| Catégorie | Travaux | Force | Limite |
|---|---|---|---|
| Architectures ASR | Whisper (Radford 2023) | Multilingue, robuste aux accents | Benchmarks propres ; hallucinations ; 1 langue/segment |
| | wav2vec 2.0 (Baevski 2020) | Pré-entraînement auto-supervisé | Fine-tuning GPU requis par domaine |
| | Conformer (Gulati 2020) | Convolution + attention | Pas de checkpoint multilingue public comparable |
| Robustesse bruit | SpecAugment (Park 2019) | Augmentation à l'entraînement | Inapplicable à un checkpoint gelé |
| | Beamforming (Chen 2018) | Filtrage spatial, parole superposée | Exige des réseaux de micros |
| Adaptation | Fine-tuning (Daouad/Polat 2024) | Adapte aux variétés sous-représentées | Audio étiqueté + GPU ; gains selon volume |
| | Benchmarks d'entités (Durmus 2026) | Révèle les échecs cachés par le WER agrégé | Diagnostic, pas mitigation |
| Streaming/diarisation | RNN-T (Sainath 2020) | Vrai temps réel frame-synchrone | Pas de checkpoint multilingue ouvert |
| | pyannote (Bredin 2020) | Diarisation end-to-end ouverte | Dégradée en chevauchement |
| Accessibilité | Kadoma 2026 | Les erreurs ASR altèrent la perception du locuteur | La précision seule ne suffit pas |

**Positionnement : mesurer l'effet marginal de chaque technique sur UN pipeline CPU déployable, quand bruit + multilinguisme + vocabulaire métier sont présents ensemble.**

---

## Slide B2 — Backup : Résultats complets par condition et par langue
**Campagne pilote CPU (n=36 par condition)**

| Condition | WER | CER | RTF (CPU) | WER propre | WER bruité |
|---|---|---|---|---|---|
| A — Baseline (tiny, auto) | 63,4 % | 43,6 % | 0.323 | 47,0 | 96,4 |
| B — + Noise reduction | 62,2 % | 44,6 % | 0.372 | 49,2 | 88,1 |
| C — + VAD (GPU, vs B-GPU) | 62,2 % | 45,6 % | 0.130* | 47,7 | 91,0 |
| D — + Domain prompt | 61,3 % | 45,2 % | 0.351 | 49,5 | 84,9 |
| E — + Forced language | 59,6 % | 41,1 % | 0.260 | 47,3 | 84,1 |
| F — Base model | 48,3 % | 33,6 % | 0.635 | 32,9 | 79,2 |

*C mesurée sur GPU fp16 — comparable à B-GPU (0.144), pas à la colonne CPU.

**WER par langue** : DE toujours le meilleur (51,6 → 33,2 de A à F) · FR le pire en D/E (74,8) · chaîne A→E sur bruité : 96,4 → 84,1 (cumul −12,3 pts).

---

## Slide B3 — Backup : Preuve de non-contamination (LoRA)
**« Votre modèle a-t-il vu les données de test ? » — Non, preuve à l'appui.**

- Exclusion de tout clip d'entraînement dont le transcript normalisé correspond à une référence d'évaluation
- Comptes d'exclusion : **EN 8/563 · FR 12/539 (8 refs + 4 doublons corpus) · DE 8/611**
- Vérification d'encodage UTF-8 explicite (« möchte » correct)
- Tirage aléatoire seedé (seed=42) : 100 clips/langue → 300
- **Assertion finale automatisée : CONTAMINATION CHECK: PASS**
- Éval appariée : mêmes 36 clips, même chemin d'inférence, même scoreur — seuls les poids diffèrent

---

## Slide B4 — Backup : L'implémentation pèse autant que l'adaptation
**Mêmes poids nominaux (whisper-small), 2,1 points d'écart.**

| Chemin d'inférence | Préproc. | WER |
|---|---|---|
| G — faster-whisper (CTranslate2, fp16 GPU) | noisereduce | 33,3 % |
| J0 — HuggingFace/PyTorch (fp16 GPU) | aucun | 31,2 % |

- Écart G vs J0 (2,1 pts) ≈ effet du fine-tuning LoRA lui-même (1,0 pt)
- **D'où la discipline appliquée partout : ne comparer qu'à backend, pipeline et prétraitement constants**

---

## Slide B5 — Backup : Architecture et chemins batch vs live
**Un backend, deux chemins de transcription.**

Frontend → FastAPI → { `/transcribe` (batch) · `/ws/transcribe` (live) · `/ask` (RAG) }

| | Batch | Live (WebSocket) |
|---|---|---|
| VAD Silero | via `vad_filter` (Condition C) | natif (segmentation) |
| noisereduce | optionnel | non |
| Langue | paramètre | `?lang=fr/en/de/auto` (défaut auto) |
| Prompt métier | optionnel | supprimé (hallucinations sur silence) |

---

## Slide B6 — Backup : « Nestlé a déjà Teams + Copilot, à quoi servez-vous ? »
**Réponse en trois étages.**

1. **Souveraineté** : Copilot = cloud Microsoft. Nestlé a créé NesGPT pour du GenAI interne sécurisé → mon Phase 1 100 % local suit cette doctrine
2. **Accessibilité d'abord** : Copilot fait des notes génériques — pas de couche malentendants, aucune garantie mesurée sur le code-switching ni le vocabulaire de marque
3. **Mesurable et adaptable** : mon pipeline expose ses paramètres et ses résultats (468 runs), avec prompt et LoRA. Un service fermé peut aussi être évalué sur ses sorties avec des références ; aucune supériorité sur Copilot n'a été mesurée ici.
