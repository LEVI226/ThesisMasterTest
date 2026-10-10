# Prompts Antigravity / Claude Code — Topic 2 STT

> Historique de developpement. Pour l'audit avant soutenance, utiliser `PROMPTS_ANTIGRAVITY_AUDIT_SOUTENANCE.md`. Les blocs ci-dessous contiennent des consignes anciennes et parfois contradictoires : notamment, un changement de WER entre CPU INT8 et GPU float16 n'est pas automatiquement un bug. Ne pas rejouer ces blocs dans les CSV canoniques sans isolation des sorties.

But : faire **tourner** le système (GPU) et me faire **comprendre + défendre** mon propre travail.
Mode recommandé : **Review-driven** (je valide chaque commande/édition).

---

## BLOC 1 — Démarrage & test en temps réel

```
Tu travailles dans ce dépôt (projet thèse STT Nestlé/BIT, FastAPI + faster-whisper).
Fais ceci étape par étape, en t'arrêtant après chacune pour me montrer la sortie :

1. Vérifie que `ollama` tourne et que le modèle llama3.2 est dispo (`ollama list`).
   Si non, lance `ollama run llama3.2`.
2. Lance `uv sync`.
3. Démarre le serveur : `uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001`.
   IMPORTANT : dans les logs de démarrage, dis-moi explicitement si faster-whisper
   se charge sur "CUDA (float16)" ou "CPU (int8)". Je suis sur une machine GPU :
   si c'est CPU, diagnostique pourquoi CUDA n'est pas détecté (torch.cuda.is_available(),
   version torch, drivers).
4. Une fois lancé, appelle `GET http://localhost:8001/health` et montre-moi le JSON.
5. Donne-moi l'URL exacte de Swagger et explique comment uploader un .wav
   sur /transcribe pour voir les champs `duration_seconds` et `processing_time_seconds`.
```

---

## BLOC 2 — Rejouer l'évaluation sur GPU

```
Localise le point d'entrée du harnais d'évaluation dans backend/evaluation/
(probablement run_pilot_matrix.py). Avant de lancer :
- explique-moi ce que fait le script et quelles conditions (A,B,D,E,F) il exécute,
- confirme qu'il écrit dans results/stt_eval_pilot_results.csv.
Puis exécute-le sur le GPU et compare les nouveaux RTF aux anciens (CPU).
Génère un petit tableau "RTF CPU vs GPU" par condition. Ne touche pas aux WER/CER :
ils doivent rester identiques (déterministes). Si un WER change, alerte-moi, c'est un bug.
Enfin, lance `uv run pytest tests/` et montre-moi le résultat.
```

---

## BLOC 4 — Échelle de tailles de modèles (G/H/I) pour le mémoire

```
Objectif : étendre la matrice d'évaluation avec les modèles small, medium et large-v3
sur GPU, pour compléter le tableau "taille de modèle vs précision/vitesse" du mémoire.
Mode review : montre-moi chaque diff avant de l'appliquer, chaque commande avant de la lancer.

1. Ouvre backend/evaluation/run_pilot_matrix.py et montre-moi la liste CONDITIONS
   (lignes ~43-48). Ajoute EXACTEMENT ces 3 lignes après la condition F, sans rien
   modifier d'autre :

    dict(tag="G_model_small", model="small", preprocessing=True, domain_prompt=False, forced_language=None),
    dict(tag="H_model_medium", model="medium", preprocessing=True, domain_prompt=False, forced_language=None),
    dict(tag="I_model_large_v3", model="large-v3", preprocessing=True, domain_prompt=False, forced_language=None),

   (Même config que B/F : preprocessing on, prompt off, langue auto — la comparaison
   B vs F vs G vs H vs I isole uniquement la taille du modèle.)

2. Vérifie que CUDA est bien détecté (torch.cuda.is_available() == True) et dis-moi
   le nom exact du GPU (torch.cuda.get_device_name(0)) — j'en ai besoin pour le mémoire.

3. Lance : uv run python -m backend.evaluation.run_pilot_matrix --max-seconds 3600
   Le script est résumable : il saute les paires (condition, fichier) déjà dans
   results/stt_eval_pilot_results.csv. Relance jusqu'à afficher 288/288
   (36 échantillons × 8 conditions). Si large-v3 échoue par manque de VRAM (<8 Go),
   dis-le-moi et on garde G et H seulement.

4. ATTENTION attendu : les WER/CER des conditions A-F recalculées sur GPU peuvent
   différer légèrement du CSV CPU (int8 vs float16 — ~52/180 divergences déjà
   documentées au Chapitre 3). Ce n'est PAS un bug. Ne touche pas aux anciennes lignes.

5. À la fin, montre-moi un tableau récapitulatif par condition (mean WER, CER, RTF)
   pour B, F, G, H, I, et confirme le chemin du CSV mis à jour.
```

---

## BLOC 5 — Palier 1 : quick wins du proposal (VAD, langue, WebSocket, latence)

```
Objectif : 4 améliorations ciblées avant soutenance. Mode review strict : montre-moi
chaque diff avant de l'appliquer. N'édite RIEN d'autre que ce qui est demandé.
AVANT TOUT : fais une copie de sauvegarde de results/stt_eval_pilot_results.csv
(ex. results/stt_eval_pilot_results_backup_avant_bloc5.csv).

TÂCHE 1 — Condition C (VAD) dans le chemin batch :
- Dans backend/stt/engine.py, ajoute un champ `vad: bool = False` à TranscribeConfig,
  et passe `vad_filter=cfg.vad` à l'appel model.transcribe() de transcribe_file().
  (faster-whisper intègre Silero VAD nativement via vad_filter — c'est le même modèle
  que load_vad_model(), en mieux intégré. Documente ce choix en commentaire.)
- Dans backend/evaluation/run_pilot_matrix.py, ajoute la condition :
    dict(tag="C_vad", model="tiny", preprocessing=True, domain_prompt=False,
         forced_language=None, vad=True),
  et propage le champ vad jusqu'à TranscribeConfig dans runner.py (défaut False
  pour ne rien changer aux conditions existantes).

TÂCHE 2 — Logger la langue détectée :
- Fais persister la langue détectée par Whisper (info.language, déjà retournée par
  transcribe_file) dans une colonne `detected_language` du CSV de résultats.
- ATTENTION : le CSV existant a 288 lignes sans cette colonne. Migre-le proprement
  (charge avec pandas, ajoute la colonne vide pour les anciennes lignes, réécris),
  ou explique-moi une alternative plus sûre avant d'agir.

TÂCHE 3 — Paramétrer le WebSocket :
- Dans le handler de /ws/transcribe (RealTimeSTTHandler), remplace le
  language="fr" hardcodé par un paramètre de connexion (query param `language`,
  valeurs fr|en|de|auto, défaut fr pour compatibilité).
- Remplace le initial_prompt inline par l'import du DEFAULT_DOMAIN_PROMPT partagé
  de backend/stt/engine.py (élimine la dérive entre les deux chemins).

TÂCHE 4 — Mesurer la latence live :
- Instrumente RealTimeSTTHandler : timestamp au déclenchement du seuil de silence
  (fin d'énoncé) et timestamp à l'envoi du transcript ; logge la latence par énoncé
  dans results/live_latency.csv (utterance_id, duration_audio, latency_seconds).
- Puis lance le serveur, ouvre /live, et fais une session de test d'au moins
  15-20 énoncés (lis des phrases à voix haute ou joue tests/sample.wav).
- Donne-moi moyenne, médiane et p95 de la latence.

VALIDATION FINALE :
- Relance uv run python -m backend.evaluation.run_pilot_matrix --max-seconds 3600
  jusqu'à completion (36 nouveaux runs C_vad ; les 288 existants sont sautés).
- Lance uv run pytest tests/ et montre le résultat.
- Récapitule : moyennes WER/CER/RTF de C_vad vs B_noise_reduction, et stats de latence.
```

---

## BLOC 6 — Palier 2 : Fine-tuning LoRA de Whisper small (RQ2 du proposal)

```
Objectif : mesurer l'effet du fine-tuning LoRA vs prompting — la promesse
"transfer learning / domain-specific fine-tuning" du proposal. Mode review strict.
GPU : RTX 4060 8 Go → whisper-small + LoRA en fp16, batch 1-2 + gradient accumulation.

ÉTAPE 1 — Split d'entraînement SANS contamination :
- Télécharge PolyAI/MInDS-14 (HF datasets), sous-ensembles en-US, fr-FR, de-DE.
- Construis un train set de ~80-100 clips par langue en EXCLUANT tout clip dont le
  transcript correspond à un des 36 fichiers d'évaluation de datasets/stt_eval/
  (comparaison par texte de référence normalisé, pas seulement par nom).
- Montre-moi le compte final train/éval et la preuve de non-chevauchement.

ÉTAPE 2 — Entraînement :
- transformers WhisperForConditionalGeneration "openai/whisper-small" + peft (LoRA
  r=16, target q_proj/v_proj), fp16, 3-5 epochs, lr ~1e-4, seed fixé.
- Logge la loss ; sauvegarde l'adaptateur dans models/lora_small_minds14/.
- Si OOM : réduis le batch, puis r=8, puis passe à whisper-base et dis-le-moi.

ÉTAPE 3 — Évaluation comparable :
- Transcris les 36 échantillons canoniques avec le modèle fine-tuné (pipeline HF,
  fp16 GPU, langue auto), et calcule WER/CER avec backend/evaluation/metrics.py
  (le MÊME scoreur que tout le reste — pas jiwer, pas evaluate).
- Écris les résultats dans results/stt_eval_lora_results.csv (mêmes colonnes),
  tag J_lora_small.
- Tableau final : G_model_small (small vanilla, GPU) vs J_lora_small vs
  D_domain_prompt — par langue et par condition de bruit.

HONNÊTETÉ : le train set est du MInDS-14 (banque téléphonique), pas du Nestlé.
On mesure la MÉTHODE (le fine-tuning apporte-t-il plus que le prompting sur un
domaine cible ?), pas un gain Nestlé-spécifique. À dire tel quel.
```

---

## BLOC 7 — Palier 3 : wav2vec 2.0 en face de Whisper + diarization (si temps)

```
TÂCHE A — Benchmark wav2vec 2.0 (promesse "Evaluate Whisper, wav2vec 2.0" du proposal) :
- Transcris les 36 échantillons canoniques avec facebook/mms-1b-all (ou, si trop
  lourd pour 8 Go, jonatasgrosman/wav2vec2-large-xlsr-53-{english,french,german},
  un modèle par langue). GPU fp16.
- Même scoreur (backend/evaluation/metrics.py), résultats tagués K_wav2vec dans
  results/stt_eval_wav2vec_results.csv.
- Tableau comparatif Whisper small/medium vs wav2vec par langue. Note attendue :
  wav2vec sort du texte non ponctué/non cassé — dis-moi comment tu normalises.

TÂCHE B — Réunion simulée : diarization multi-locuteurs + test live
(= la puce "Test prototypes for real-time transcription in simulated Teams
meetings" du proposal) :
- Configure un token Hugging Face (HF_TOKEN) pour pyannote/speaker-diarization.
- Construis 6-8 fichiers "réunion simulée" en concaténant des clips MInDS-14 de
  locuteurs différents (2-3 locuteurs par fichier, vérité terrain = ordre connu),
  dont la moitié avec bruit de fond ajouté (même SNR 8 dB que le dataset).
- Volet batch : passe-les dans transcribe_file() avec diarization active ;
  rapporte l'exactitude d'attribution (bon locuteur par segment) — qualitatif
  accepté, DER si possible.
- Volet live : joue 2-3 de ces fichiers dans la page /live (chemin WebSocket)
  et logge la latence par énoncé (même instrumentation que BLOC 5 TÂCHE 4).
  → Ce test EST la "réunion simulée" du proposal : multi-locuteurs + bruit +
  temps réel, mesuré.
```

---

## BLOC 8 — Benchmark FLEURS (le mètre-étalon du domaine)

```
Objectif : évaluer l'échelle de modèles Whisper sur FLEURS (benchmark multilingue
standard, CC-BY-4.0), pour situer mes chiffres face à la littérature. Mode review.

ÉTAPE 0 — Test de chargement (le bloqueur historique) :
- Vérifie que google/fleurs se charge via HF datasets pour en_us, fr_fr, de_de
  (split 'test'). Contourne le shadow du dossier datasets/ local (retire le projet
  du sys.path avant l'import, comme dans build_train_split.py) et charge avec
  decode=False pour éviter torchcodec (Windows).
- Si le chargement échoue (réseau, taille), DIS-LE-MOI et on s'arrête là.

ÉTAPE 1 — Sous-ensemble comparable :
- Échantillonne 20 clips par langue (en/fr/de) du split test, tirage seedé (seed=42),
  sauvegarde WAV 16 kHz mono dans datasets/fleurs_eval/audio/ + une metadata.csv
  AU MÊME FORMAT que datasets/stt_eval/metadata.csv (colonnes : audio_filename,
  reference_filename, language, noise_condition='clean', speaker_count=1, notes).
  Écris les transcripts de référence dans datasets/fleurs_eval/references/.
- Note honnête à mettre dans le notes : FLEURS = parole lue propre, haute qualité,
  PAS comparable au MInDS-14 téléphonique bruité.

ÉTAPE 2 — Évaluation, échelle complète, MÊME scoreur :
- Réutilise backend/evaluation/metrics.py (wer, cer) — PAS jiwer.
- Transcris les 60 clips (20×3) avec tiny, base, small, medium, large-v3, GPU fp16,
  langue auto, inférence directe model.generate() (comme eval_lora.py, bypass torchcodec).
- Écris results/stt_eval_fleurs_results.csv (mêmes colonnes que le CSV pilote),
  tags FLEURS_tiny, FLEURS_base, FLEURS_small, FLEURS_medium, FLEURS_large_v3.

ÉTAPE 3 — Récapitulatif :
- Tableau WER/CER par modèle et par langue.
- Rappelle : ces chiffres FLEURS (propre) ne se comparent PAS aux chiffres MInDS
  (bruité). Le but est de situer face à la littérature, pas de battre un record.
```

---

## BLOC 3 — Comprendre le code (tuteur, pas rédacteur)

```
Agis comme un tuteur qui me prépare à défendre MON code. Ne réécris rien.
Prends ces fichiers un par un et, pour chacun, explique le rôle puis pose-moi
2 questions de compréhension avant de passer au suivant :

1. backend/stt/engine.py  -> pipeline transcribe_file, INT8 vs float16,
   condition_on_previous_text, pourquoi le VAD Silero n'est utilisé que dans le WebSocket.
2. backend/evaluation/metrics.py -> algorithme Wagner-Fischer, différence WER vs CER,
   pourquoi un WER peut dépasser 100%.
3. backend/main.py -> chemin complet d'une requête /transcribe (upload -> Whisper ->
   ingestion ChromaDB -> réponse), et le rôle d'Ollama dans /ask.

Attends ma réponse à chaque question et corrige-moi.
```

---

## BLOC 4 — Simulation de jury

```
Tu es mon jury de soutenance de master. Pose-moi 15 questions, UNE À LA FOIS,
en te basant uniquement sur le code de ce dépôt et sur results/ + Topic2_Thesis_Rewrite.md.
Inclus obligatoirement ces angles :
- Pourquoi le forçage de langue corrige le script français mais n'améliore pas le WER français ?
- Pourquoi le domain prompt a-t-il DÉGRADÉ la précision sur ce dataset ?
- Pourquoi MInDS-14 et pas un corpus Nestlé réel ? Quelle est la limite ?
- Quelle est la différence entre le chemin batch et le chemin WebSocket ?
- Pourquoi le bruit double-t-il le WER, et que fait noisereduce exactement ?
Après chaque réponse que je donne : note-la /10, dis ce qui manque, puis question suivante.
Sois exigeant comme un vrai jury.
```

---

### Ordre conseillé
BLOC 1 (voir tourner) → BLOC 3 (comprendre) → BLOC 4 (se tester) → BLOC 2 (résultats GPU pour enrichir le chapitre 6).
