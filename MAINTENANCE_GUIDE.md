# Guide de maintenance IA du projet

> Objectif : pouvoir reprendre, réparer et expliquer ce projet sans dépendre d'une IA
> qui serait seule à comprendre ce qu'elle a produit.

Dernière mise à jour : 2026-09-22.

Ce guide complète `README.md`, `ETAT_ACTUEL.md`, `AI_METHODOLOGY.md`,
`Antigravity_Prompts.md` et `PROMPTS_ANTIGRAVITY_AUDIT_SOUTENANCE.md`.

## 1. Ce que ce projet est

Le dépôt `ThesisMasterTest` contient un prototype académique pour le mémoire Topic 2 :

**Advanced Speech-to-Text Models for Noisy, Multilingual Corporate Meetings: Evaluation
of a Whisper-Based Pipeline for Workplace Accessibility.**

Le coeur défendable du mémoire est le STT :

- transcription multilingue français / anglais / allemand ;
- robustesse au bruit ;
- comparaison Whisper, wav2vec 2.0 / MMS, Conformer ;
- adaptation par prompt et LoRA ;
- latence et transcription live avec limites clairement nommées ;
- diarisation expérimentale sur réunions simulées.

Le projet contient aussi OCR, RAG et frontend, mais ces parties ne doivent pas voler le
centre du mémoire. Pour la soutenance, le périmètre principal reste Topic 2.

## 2. Sources de vérité

Lire dans cet ordre avant toute modification :

1. `ETAT_ACTUEL.md` : état scientifique courant, chiffres canoniques, limites.
2. `AI_METHODOLOGY.md` : usage de l'IA, erreurs rejetées, vérifications humaines.
3. `README.md` : lancement, architecture, endpoints.
4. `PROMPTS_JOURNAL.md` : prompts et méthodes réutilisables.
5. `CHANGELOG.md` : évolution synthétique du projet.
6. `PROMPTS_ANTIGRAVITY_AUDIT_SOUTENANCE.md` : protocole d'audit strict avant soutenance.
7. `results/` : source de vérité chiffrée, surtout les CSV.

Règle simple : un nombre écrit dans le mémoire doit pouvoir être retracé jusqu'à un CSV,
un script, ou une note d'audit.

## 3. Structure utile

```text
backend/
  main.py                         FastAPI, endpoints, WebSocket live STT
  stt/engine.py                   moteur Whisper/faster-whisper, VAD, diarisation
  stt/session_log.py              journalisation optionnelle des sessions STT
  evaluation/
    metrics.py                    WER/CER/RTF canonique
    dataset.py                    lecture de metadata.csv
    runner.py                     boucle d'évaluation générique
    run_pilot_matrix.py           matrice historique Whisper
    run_statistical_audit.py      intervalles et contrastes importants
    research_dashboard.py         données du dashboard /research
    topic2_readiness.py           audit de préparation Topic 2
  training/
    build_train_split.py          split LoRA sans contamination
    train_lora.py                 entraînement adaptateur LoRA
    eval_lora.py                  évaluation LoRA vs vanilla
    eval_wav2vec.py               benchmark MMS/wav2vec
    eval_conformer.py             benchmark Conformer
    build_meetings.py             réunions simulées
    eval_meetings.py              diarisation sur réunions simulées

frontend/
  index.html                      interface principale
  live_transcribe.html            page live STT
  research.html                   dashboard de preuves /research

datasets/
  stt_eval/                       36 clips canoniques + références + metadata.csv
  meetings/                       réunions simulées

results/
  *.csv                           résultats canoniques et journaux
  transcripts/                    hypothèses générées
  *.md                            rapports d'audit et de synthèse

Memoire_LaTeX/
  main_revised.tex                version anglaise de travail
  bibitem_revised.bib             bibliographie de la révision
  main.tex                        version antérieure
  main_FR.tex                     traduction bonus, pas toujours synchronisée
```

## 4. Lancer le projet

Prérequis principaux :

- Python compatible avec `pyproject.toml` ;
- `uv` ;
- environnement Windows/GPU si l'on veut reproduire les campagnes lourdes ;
- Ollama + `llama3.2` pour la partie RAG locale ;
- dépendances système possibles : ffmpeg, Tesseract, Poppler selon OCR/audio.

Commande de base :

```powershell
uv sync
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001
```

URLs utiles :

- plateforme : `http://localhost:8001`
- live STT : `http://localhost:8001/live`
- dashboard recherche : `http://localhost:8001/research`
- API docs : `http://localhost:8001/docs`
- health check : `http://localhost:8001/health`

## 5. Vérifier avant de modifier

Commandes légères :

```powershell
uv run pytest
uv run python -m backend.evaluation.topic2_readiness
uv run python -m backend.evaluation.run_statistical_audit
```

Avant une modification scientifique :

1. Noter l'état Git : `git status --short`.
2. Identifier les fichiers qui seront touchés.
3. Vérifier si la modification change un CSV canonique.
4. Si une nouvelle expérience est lancée, écrire dans un dossier ou fichier isolé.
5. Ne jamais écraser les anciens résultats sans sauvegarde et justification.

Pour des campagnes lourdes, utiliser des chemins de sortie isolés et garder les logs.
Le projet a déjà eu des erreurs de dérive entre pipelines ; il faut préserver les
artefacts défavorables au lieu de les lisser.

## 6. Jeu de données canonique

Ne pas changer sans créer une section "hors campagne canonique" :

- corpus : PolyAI/MInDS-14, licence CC-BY-4.0 ;
- langues : en, fr, de ;
- évaluation : 36 clips = 24 propres + 12 bruités ;
- bruit : bruit blanc synthétique à 8 dB SNR ;
- split LoRA : 300 clips, exclusion des références d'évaluation ;
- scorer : `backend/evaluation/metrics.py`.

Ne pas fusionner dans les tableaux principaux :

- pipelines MLS / FLEURS / Common Voice / VoxPopuli utilisés comme tests latéraux ;
- runs à 10 dB SNR ;
- expériences 8 clips ;
- résultats non traçables à des CSV.

## 7. Réparer les problèmes fréquents

### CUDA non détecté

1. Appeler `/health` et regarder `stt_device` / `stt_compute_type`.
2. Vérifier `torch.cuda.is_available()` dans l'environnement `uv`.
3. Comparer les versions torch / CUDA / ctranslate2.
4. Sous Windows, le projet épingle `ctranslate2==4.6.0` pour éviter des conflits DLL.

### WER différent entre CPU et GPU

Ne pas conclure automatiquement à un bug. Les backends INT8 CPU et float16 GPU peuvent
produire des hypothèses légèrement différentes. Comparer seulement des runs qui gardent
le même backend, le même modèle, le même prompt, la même langue et le même prétraitement.

### NeMo / Conformer casse

Points historiques :

- dépendance `hydra` manquante ;
- NeMo 3.x peut retourner des objets `Hypothesis`, pas des chaînes ;
- certains modèles Conformer sont langue donnée par construction.

Toujours classer Conformer/MMS comme comparaison CTC avec langue fournie, pas comme
preuve directe que Whisper-auto serait inférieur.

### Live STT lent ou instable

Le live actuel est une transcription batch segmentée par VAD, pas du streaming
frame-synchrone. Le CSV `results/live_latency.csv` ne mesure pas tout le rendu client.
Pour une nouvelle étude live, loguer : session, modèle, device, endpointing, final speech,
server send, browser receive/render, hypothèse et référence.

### Diarisation

Les réunions sont simulées et les labels peuvent refléter une alternance artificielle de
clips. Ne pas présenter le DER comme une validation complète de réunions réelles.

### LaTeX

`main_revised.tex` est la révision de travail. Le sandbox local peut manquer de paquets
LaTeX ; TeXPage ou Overleaf sont plus fiables. Ne pas confondre `main.tex` et
`main_revised.tex`.

## 8. Règles anti-boîte noire

- Garder le prompt exact quand il a produit un résultat utile.
- Noter les réglages, le modèle, le device, le chemin de sortie et le résultat.
- Ajouter les corrections dans `CHANGELOG.md`.
- Ajouter les prompts réutilisables dans `PROMPTS_JOURNAL.md`.
- Garder les échecs importants : ils expliquent les choix.
- Ne pas accepter une citation, un chiffre ou un tableau parce qu'il "sonne bien".
- Ne pas coller de secret dans un prompt. Les clés déjà exposées doivent être révoquées
  et régénérées.

## 9. Checklist avant soutenance

- `ETAT_ACTUEL.md` relu.
- `main_revised.tex` et `bibitem_revised.bib` alignés.
- Tous les chiffres clés retracés vers `results/`.
- `AI_METHODOLOGY.md` prêt à expliquer l'usage de l'IA.
- Limites répétées clairement : MInDS-14 ≠ réunions Nestlé réelles, pas d'étude
  utilisateur, live segmenté, diarisation expérimentale.
- Les prompts d'audit de `PROMPTS_ANTIGRAVITY_AUDIT_SOUTENANCE.md` ont été rejoués ou
  utilisés comme grille de contrôle.
- PDF final exporté et vérifié visuellement.

