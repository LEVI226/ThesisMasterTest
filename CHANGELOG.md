# Changelog — Topic 2 (STT), mémoire BIT/Nestlé

Historique daté du projet. Chaque entrée est ancrée sur une trace vérifiable : commit git, date de
fichier de résultats, ou dossier d'audit. Rien ici n'est reconstitué de mémoire ; si une date vient
d'un horodatage de fichier plutôt que d'un commit, c'est indiqué.

Format : `AAAA-MM-JJ — ce qui a changé — où le vérifier`.

---

## Phase 1 — Construction du prototype et de la campagne (juin – juillet 2026)

**2026-06-14** — Restructuration du code (`git log`).

**2026-06-27** — Campagne pilote CPU exécutée, 180 runs, 5 conditions (A baseline, B réduction de
bruit, D prompt métier, E langue forcée, F modèle base), modèle `tiny`/`base`, INT8 sur CPU.
→ `results/stt_eval_pilot_results_CPU_baseline.csv`. Un run GPU séparé des mêmes conditions est
conservé à part → `results/stt_eval_pilot_results_GPU.csv`.

**2026-06-28** — Plusieurs corrections du prototype live : VAD Silero (fenêtres de 512 échantillons),
diarisation pyannote 4.x (`DiarizeOutput.speaker_diarization`), canvas HiDPI, hallucinations Whisper
(filtre RMS + répétition). Durée audio réelle renvoyée, diarisation découplée du prétraitement.
Archivage des anciens brouillons, correction de DOI, ajout de la section 8.4 (travaux futurs GPU).
→ 8 commits du 28/06.

**2026-07-09** — Correction du nom de l'étudiant sur le Topic 2 (`git log`).

**2026-07-26** — BLOC 5+6 : condition C (VAD via `vad_filter`), colonne `detected_language`,
fine-tuning LoRA de `whisper-small` (300 clips, non-contamination vérifiée). BLOC 7 : benchmark
wav2vec 2.0/MMS-1B et diarisation pyannote sur 7 réunions simulées.
→ `results/stt_eval_lora_results.csv`, `stt_eval_wav2vec_results.csv`, `meeting_eval_results.csv`,
`lora_training_log.csv`, et le CSV canonique consolidé `stt_eval_pilot_results.csv` (324 lignes).

**2026-07-31** — Extension FLEURS, 300 runs, validité externe. Seul `large-v3` (7,4 %) est
exploitable ; les tailles inférieures partent en boucle de répétition et sont écartées.
→ `results/stt_eval_fleurs_results.csv`.

## Phase 2 — Complétion de la campagne et rédaction (août 2026)

**2026-08-20** — Benchmark Conformer (NeMo CTC, checkpoints monolingues en/fr/de), 36 runs.
La campagne canonique atteint **468 runs**. → `results/stt_eval_conformer_results.csv`.

**2026-08-22** — Rédaction de `AI_METHODOLOGY.md` (outils IA utilisés, décisions assistées,
vérifications manuelles, corrections apportées aux sorties IA, limites rencontrées).

**2026-08-27** — Journal de latence live (38 observations, 3 sessions inférées).
→ `results/live_latency.csv`. Révision du mémoire : `main_revised.tex` + `bibitem_revised.bib`
(50 références), correction de la comparaison bruit non appariée → 12 paires appariées,
ajout de la section « Contemporary Meeting Transcription Benchmarks ».

**2026-09-03** — Dernier commit git : mise à jour des fichiers de thèse, scripts et métriques.
*(À partir d'ici, le travail n'est plus committé : les changements sont dans l'arbre de travail.)*

## Phase 3 — Audits avant soumission (10 septembre 2026)

**2026-09-10** — Audit pré-soutenance. Recalcul indépendant des 468 runs avec un scorer
réimplémenté (pas d'appel au scorer du projet) : total conforme, 0 doublon, 0 référence vide,
écart maximal stocké/recalculé 4,6 × 10⁻⁵. Vérification des contrastes, de la biblio (50/50) et
des références croisées. Correction du LaTeX pour TeXPage (geometry, ancres hyperref, polices,
débordements). → `audits/pre_defense/20260910-140354/` (rapports 00 à 07, 11 scripts).

## Phase 4 — Audit de conformité au proposal et validation (16 septembre 2026)

**2026-09-16 (matin)** — Audit de conformité au Topic 2 du Research Proposal : matrice
exigence → preuve → statut, sondes de contrat, recalculs statistiques, smoke test CPU.
→ `audits/topic2_proposal_20260916/`.

**2026-09-16 (journée)** — Validation indépendante. Trois défauts de contrat reproduits **avant**
correction, corrigés, couverts par des tests de régression (suite : 51 → 68 tests, 0 échec) :
langue ignorée à l'upload, dernière phrase perdue à l'arrêt, collisions de fichiers de
transcription. Journalisation par session (modèle réellement chargé, device, précision, versions).
Essais réels bornés (GPU float16 et CPU int8 forcé), essais micro, rejeu de l'AGM Nestlé.
Réannotation à l'écoute de 16 références sur 24 : 7 diffèrent de la source publiée. Révision de
sensibilité avec intervalles bootstrap groupés par clip source.
→ `audits/topic2_validation/20260916-073214/` (22 rapports, 19 scripts, `SUMMARY.md`).

**2026-09-16 (14h02)** — Réparation de l'environnement de diarisation : Lightning 2.4.0,
CTranslate2 4.6.0, appel pyannote corrigé sur le chemin fichier. pyannote se charge désormais ;
la précision des attributions n'est toujours pas établie.
→ `audits/diarization_20260916/DIAGNOSTIC.md`.

**2026-09-16 (soir)** — Corrections du mémoire (10 modifications ciblées) et ajout de l'annexe
datée `validation_20260916.tex`. Livraison TeXPage préparée.
→ `audits/topic2_validation/20260916-073214/JOURNAL_CORRECTIONS_MEMOIRE_20260916.md`,
`CONFORMITE_TOPIC2_20260916.md`, `VERDICT_20260916.md`.

**2026-09-16 (seconde passe)** — Corrections de formulation : chronologie (« audit complémentaire
du 16 septembre 2026 »), références (« présentent des différences après réannotation », pas
« défectueuses »), langue forcée nuancée, verdict reformulé.

---

## Ce qui n'est pas committé

Depuis le 2026-09-03, tout le travail est dans l'arbre de travail (10 fichiers modifiés,
15 non suivis au 16/09). Les dossiers `audits/`, `Memoire_LaTeX/texpage_delivery_20260916/`,
`training/` et `audioReunionréel/` ne sont pas sous git.

**Action recommandée avant la soutenance** : committer au moins `audits/`, le mémoire corrigé et
`tests/test_contract_regressions.py`. Sans cela, l'historique de cette phase de validation repose
uniquement sur des horodatages de fichiers.

## Invariants respectés tout au long

- Les CSV canoniques de `results/` et les références de `datasets/stt_eval/references/` n'ont
  **jamais** été modifiés. Chaque révision vit à côté, datée.
- Le hash SHA-256 de `results/live_latency.csv` a été contrôlé après chaque exécution live.
- Aucune inférence nouvelle n'a été lancée pour produire les chiffres révisés : les hypothèses
  stockées dans les CSV ont été rescorées.

## Phase 4 — Étude de validation sur réunions réelles (octobre 2026)

**2026-10-10** — Instantané de l'état soutenable : commit `9054422`, tag `defense-baseline`.
`.gitignore` exclut désormais l'audio privé, les sondes d'audit et `tmp/`. Ouverture de la branche
`study/real-meetings` ; spec (`53248d7`) et plan d'implémentation rédigés. Les réunions privées sont
exclues faute de consentement. → `docs/specs/`, `docs/plans/`.

**2026-10-11** — Exécution des runs de test du protocole gelé (tag `protocol-frozen`, `eb080cb`) :
6 systèmes via `run_experiments --plan ALL --split test` (un système par processus), puis H5
(`run_streaming`) et D1 (`run_diarization`). `runs.csv` : 26 463 lignes (whisper-small 6 580,
whisper-large-v3 7 595, conformer-ctc-large 4 151, mms-1b-all 4 151, hf-whisper-small 1 993,
hf-whisper-small-lora 1 993), toutes sur le commit `eb080cb`, sans doublon ni « -dirty ».
`streaming.csv` : 60 lignes ; `diarization.csv` : 3 réunions. Incidents : whisper-large-v3 a planté
après ~1 h 20 (MemoryError « bad allocation » puis 3 relances immédiates en CUDA out of memory) ;
les autres systèmes sont passés (conformer : 3 échecs de démarrage avant réussite) ; relance
isolée de whisper-large-v3 le lendemain (1 h 07, reprise sans doublon). La première tentative de
`run_streaming` a échoué au chargement de large-v3 (CUDA OOM, aucun CSV écrit) ; relancée seule
après libération du GPU, terminée en ~1 h 38. Ancrage externe : WER des transcriptions publiées ASRU
2023 sur nos segments SUMM-RE de test 0,297 contre 0,301 pour notre whisper-large-v3 (cohérent).
→ `results/real_meetings/`, journaux dans `results/real_meetings/logs/`.
