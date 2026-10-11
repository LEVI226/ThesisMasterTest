# Matrice de conformité — Topic 2 vs Research Proposal (pages 2–3) — 16 septembre 2026

Sources examinées : `Research Proposal.pdf` (texte extrait `tmp/pdfs/research_proposal_review/proposal.txt`),
`Memoire_LaTeX/main_revised.tex` + `topic2_completion.tex` + `validation_20260916.tex` (entrée compilée),
`backend/`, `results/*.csv`, `audits/topic2_validation/20260916-073214/`, `audits/diarization_20260916/`.
Statuts : **satisfait** · **partiellement satisfait** · **non démontré** · **hors périmètre**.
Quatre niveaux distingués : *implémenté* (le code existe) · *exécuté* (une exécution observée) ·
*mesuré* (une performance chiffrée avec référence) · *validé en entreprise* (conditions Nestlé réelles).

## Objectif du Topic 2 (proposal p. 2)

> Develop robust AI-based STT systems that can accurately transcribe corporate meetings and video calls in
> real time, handling multiple speakers, background noise, and multilingual content.

| Composante | Implémenté | Exécuté | Mesuré | Validé entreprise | Section mémoire | Preuve | Statut |
|---|---|---|---|---|---|---|---|
| Transcription STT | oui | oui (468 runs ; AGM 22 min) | oui (WER/CER sur MInDS-14, références partiellement révisées) | non | II.2, III.3, annexe A.3/A.5 | `results/*.csv`, `04_file_smoke_*`, `09_*` | **partiellement satisfait** — mesuré sur téléphonie bancaire, pas sur réunions |
| Temps réel | oui (WebSocket + VAD) | oui (micro, rejeu) | temps de calcul post-déclenchement mesuré ; délai de bout en bout **non mesuré** ; longueur d'énoncé non bornée | non | III.3.2 « Live-Path Latency », annexe A.4 | `live_latency*.csv`, sessions JSONL, `09c` | **partiellement satisfait** |
| Plusieurs locuteurs | oui (pyannote, fichier et live) | oui (chargement vérifié après réparation ; 2 étiquettes sur extrait simulé) | **non** — aucune annotation temporelle fiable, aucun DER défendable | non | III.3.2 diarisation, annexe A.6 | `audits/diarization_20260916/`, `results/meeting_eval_results.csv` (banc artificiel) | **non démontré** (exécution seulement) |
| Bruit de fond | oui (noisereduce, VAD) | oui | oui (12 paires appariées, +35,3 / +36,9 pts, IC excluant 0) | non | III.3.2 H1, annexe A.3 | `stt_eval_pilot_results.csv`, `revision_v2` | **satisfait sur bruit blanc synthétique** ; bruit de réunion réel non testé |
| Multilingue | oui (en/fr/de, auto + forcé) | oui | oui par langue ; changement de langue **intra-énoncé** : modes d'échec observés, non mesurés | non | III.3.2 H4, annexe A.5, `08_codeswitch` | `05_live_sim`, `08_codeswitch_live.json`, `09b`, `09c` | **partiellement satisfait** |

## Questions de recherche (proposal p. 2–3)

| RQ (proposal) | Section mémoire | Preuve | Statut | À expliciter |
|---|---|---|---|---|
| RQ1 — performance des ASR transformeurs en conditions bruitées et multilingues d'entreprise | I.2, III.3 (Whisper ×5, MMS, Conformer) | 468 runs ; échelle monotone ; IC groupés | **partiellement satisfait** — « corporate settings » non testés ; corpus téléphonique | limite déclarée dans le mémoire ; renforcée par A.7 |
| RQ2 — stratégies d'adaptation (transfer learning, fine-tuning) | III.3.2 « RQ2 Completed » (prompt, LoRA) | J0/J appariés : +1,0 [−2,4 ; 5,3] original ; +0,6 [−1,9 ; +3,0] révisé ; prompt −0,5 [−3,2 ; +2,1] | **partiellement satisfait** — aucun bénéfice établi ; vocabulaire Nestlé jamais évalué (entités : 5/9 noms faux sur l'AGM, qualitatif) | formulation corrigée : « aucun bénéfice établi, équivalence non montrée » |
| RQ3 — minimiser la latence sans sacrifier la précision | III.3.2 « Live-Path Latency », annexe A.4 | médiane 0,56 s post-déclenchement (historique) ; blocs de 70 s et 149 s observés ; pas de compromis précision/latence mesuré | **partiellement satisfait** — RTF ≠ délai de sous-titrage ; aucune configuration alternative comparée | corrigé : trois grandeurs distinguées, absence de borne déclarée |

## Méthodologie (proposal p. 3)

| Exigence | Section | Preuve | Statut |
|---|---|---|---|
| Revue de littérature ASR | I | 50 références vérifiées | **satisfait** |
| Collecter/curer des jeux simulant des réunions multilingues et accentuées | II.2.2 | MInDS-14 (téléphonie bancaire, mono-locuteur, 8 kHz) ; 7 réunions simulées par concaténation ; accent : 1 locuteur non natif (annexe A.4) | **partiellement satisfait** — déclaré comme limite ; 7/16 références en/fr présentent des différences après réannotation, dont 2 sur des hésitations, certains passages restant incertains (annexe A.2) |
| Évaluer Whisper, wav2vec 2.0, Conformer | III.3 | les trois, même jeu, même scorer | **satisfait** |
| Réduction de bruit, diarisation, adaptation de domaine | III.3.2 | les trois expérimentés ; diarisation non mesurée en précision | **partiellement satisfait** |
| Prototypes temps réel en réunions Teams simulées | — | aucune intégration Teams ; prototype navigateur adjacent | **non démontré** (déclaré comme tel, complément + A.7) |

## Résultat attendu (proposal p. 3)

> A real-time STT engine optimized for corporate communications, capable of delivering accessible transcripts
> for hearing-impaired employees.

| Élément | Statut | Justification |
|---|---|---|
| Moteur STT temps réel | **partiellement** — fonctionne ; délai non borné sur parole continue ; démarrage perd les premiers mots | A.4 |
| Optimisé pour les communications d'entreprise | **non démontré** — prompt statique protège les marques listées, pas les personnes ; pas de fine-tuning sur vocabulaire Nestlé | A.5 |
| Transcripts accessibles pour malentendants | **hors périmètre** (Topic 3) — aucune évaluation utilisateur ; dit explicitement dans le mémoire | abstract, conclusion |

## Classes de données (à ne pas confondre)

| Classe | Utilisation | Statut de preuve |
|---|---|---|
| MInDS-14 public (CC-BY) | campagne canonique 468 runs | mesuré ; références en/fr révisées, de non vérifiées |
| Audio Nestlé public (AGM 2026 webcast) | 1 fichier, chemin fichier + rejeu live | qualitatif, sans référence |
| Réunions simulées (concaténation MInDS-14) | diarisation | exécution seulement ; étiquettes A/B artificielles |
| Enregistrements internes (`audioReunionréel/*.m4a`) | traités localement une fois ; **non évalués** | aucune preuve ; jamais envoyés à un service externe |
