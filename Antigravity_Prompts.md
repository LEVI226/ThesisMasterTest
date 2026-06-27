# Prompts Antigravity / Claude Code — Topic 2 STT

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
