# Reproduction — comment refaire chaque vérification sans aide

Ce document liste les commandes exactes pour rejouer toute vérification du projet. Chaque contrôle
est un script sauvegardé : tu peux l'ouvrir, le lire, le modifier et le relancer. Aucun ne dépend
d'une conversation.

**Prérequis** : PowerShell ou Git Bash à la racine `C:\Users\ulric\Documents\ThesisMasterTest`.
L'interpréteur est `.venv\Scripts\python.exe` (Python 3.13, torch 2.6.0+cu124, faster-whisper 1.2.1,
CTranslate2 4.6.0, pyannote.audio 4.0.4). Toutes les commandes ci-dessous sont **en lecture seule**
sur les données historiques, sauf mention contraire.

Pour l'affichage des accents et de l'API : préfixer par `PYTHONIOENCODING=utf-8` en Git Bash, ou
`$env:PYTHONIOENCODING="utf-8"` en PowerShell.

---

## 1. La suite de tests

```
.venv\Scripts\python.exe -m pytest tests/ -q --basetemp=tmp\pytest
```

Attendu : **68 passed, 0 failed**. Le `--basetemp` est nécessaire : le dossier temp par défaut de
pytest n'est pas accessible en écriture sur cette machine (8 erreurs sinon, qui ne sont pas des
régressions). `tests/test_contract_regressions.py` couvre les trois défauts de contrat corrigés
le 16/09 ; les autres fichiers couvrent le harnais d'évaluation.

## 2. Recalculer les 468 runs avec un scorer indépendant

```
.venv\Scripts\python.exe audits\pre_defense\20260910-140354\recalc.py sortie.md
```

Réimplémente Levenshtein (DP à deux lignes) sans appeler `backend/evaluation/metrics.py`, pour
qu'un bug du scorer du projet ne puisse pas se valider lui-même. Vérifie le total de 468, les
doublons, les références vides, et compare chaque WER stocké au WER recalculé.
Attendu : total conforme, 0 doublon, écart maximal ≈ 4,6 × 10⁻⁵ (arrondi CSV à 4 décimales).

## 3. Recalculer les contrastes principaux

```
.venv\Scripts\python.exe audits\pre_defense\20260910-140354\contrasts.py
```

Effet du bruit sur les 12 paires appariées (et non sur les groupes 24/12 non comparables),
bootstrap apparié, échelle de tailles, comparaisons inter-architectures, et sensibilité de
l'estimateur (moyenne des WER par fichier vs WER agrégé).

## 4. Vérifier la bibliographie et les références croisées du mémoire

```
.venv\Scripts\python.exe audits\pre_defense\20260910-140354\checkbib.py
.venv\Scripts\python.exe audits\pre_defense\20260910-140354\checkrefs.py
.venv\Scripts\python.exe audits\topic2_validation\20260916-073214\check_syntax.py
.venv\Scripts\python.exe audits\topic2_validation\20260916-073214\check_specials.py
```

Clés `\cite` vs entrées `.bib`, `\label` vs `\ref`, accolades et environnements appariés, chemins
absolus, caractères spéciaux non échappés. Attendu : 50/50 citations, 14 labels uniques,
0 `\ref` orphelin.

## 5. Vérifier que la livraison TeXPage est autonome

```
.venv\Scripts\python.exe audits\topic2_validation\20260916-073214\verify_delivery.py
```

Résout chaque `\input`, `\includegraphics` et `\bibliography` dans le dossier de livraison.
Attendu : **0 référence non résolue**.

## 6. Reproduire les trois défauts de contrat

```
.venv\Scripts\python.exe audits\topic2_validation\20260916-073214\repro_defects.py AFTER
```

Sondes avec dépendances simulées (faux ASR, faux VAD) : ce sont des tests de **contrat logiciel**,
jamais une preuve de qualité ASR. Pour voir l'état d'avant correction, le fichier
`01_repro_defects_BEFORE.json` est conservé dans le même dossier.

## 7. Inférence réelle bornée (chemin fichier)

```
.venv\Scripts\python.exe audits\topic2_validation\20260916-073214\file_smoke.py gpu_fp16
```

Pour forcer le CPU malgré la présence de CUDA :

```
$env:STT_DEVICE="cpu"; $env:STT_COMPUTE_TYPE="int8"
.venv\Scripts\python.exe audits\topic2_validation\20260916-073214\file_smoke.py cpu_int8
```

5 clips en/fr/de, propre et bruité, auto et langue forcée. Écrit dans le dossier d'audit
uniquement. `get_model_info()` rapporte le modèle **réellement** chargé.

## 8. Chemin live sans micro ni navigateur

```
.venv\Scripts\python.exe audits\topic2_validation\20260916-073214\live_sim.py
.venv\Scripts\python.exe audits\topic2_validation\20260916-073214\live_sim_flush.py
.venv\Scripts\python.exe audits\topic2_validation\20260916-073214\live_codeswitch.py
```

Vrais modèles (Whisper + Silero VAD), socket simulé. `live_sim_flush.py` compare le handler
corrigé au handler d'origine (copie dans `pristine/`) sur des clips coupés en pleine parole.
Ces scripts redirigent leurs sorties : ils n'écrivent **jamais** dans `results/live_latency.csv`.

## 9. Rescorer avec les références réannotées

```
.venv\Scripts\python.exe audits\topic2_validation\20260916-073214\reannotation\ingest_sheet.py
```

Lit la feuille `07b_transcription_sheet_BLIND.csv`, versionne chaque transcription sous
`references_v2/` avec annotateur, date et raison, rescore les 468 hypothèses stockées (sans
nouvelle inférence) et recalcule les intervalles bootstrap groupés par clip source.
Les originaux de `datasets/stt_eval/references/` ne sont jamais touchés.

Pour re-trier quels clips écouter en priorité :

```
.venv\Scripts\python.exe audits\topic2_validation\20260916-073214\reference_triage.py
```

## 10. Lancer l'application

```
$env:STT_SESSION_LOG_DIR="audits\<run>\sessions"
$env:LIVE_LATENCY_CSV="audits\<run>\live_latency.csv"
uv run uvicorn backend.main:app --port 8001
```

Sans `--reload` (le rechargement des modèles GPU prend ~40 s). Les deux variables redirigent les
journaux hors de l'historique ; **sans elles, l'application écrit dans `results/live_latency.csv`**.

Avant toute démonstration, vérifier `http://localhost:8001/health` :

```json
{"whisper_model":"small","stt_device":"cuda","stt_compute_type":"float16",
 "vad_available":true,"diarization_available":true}
```

Si `diarization_available` est `false`, relancer le serveur — les locuteurs sortiraient tous en
`SPEAKER_UNKNOWN`.

Port occupé sous Windows : `netstat -ano | grep ":8001 "` puis `taskkill //F //PID <pid>`.

---

## Règles de sécurité des données (à ne jamais enfreindre)

1. Ne jamais écrire dans `results/*.csv` ni dans `datasets/stt_eval/references/`. Toute révision
   vit dans un dossier daté à côté.
2. Vérifier le hash après une exécution live :
   `sha256sum results/live_latency.csv` → doit rester `25edc394…`.
3. Les enregistrements de `audioReunionréel/*.m4a` sont internes : traitement **local uniquement**,
   jamais vers un service externe. L'audio public de l'AGM Nestlé, lui, peut sortir.
4. Ne jamais produire une référence de transcription avec un outil ASR : c'est le raisonnement
   circulaire que tout le travail cherche à éviter.
