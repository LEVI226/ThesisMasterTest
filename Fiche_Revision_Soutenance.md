# Fiche de révision — Soutenance Topic 2 (STT)

> À connaître par cœur. Tous les chiffres viennent de `results/stt_eval_pilot_results.csv` (run CPU int8) et du Chapitre 6.

## 1. Les chiffres clés

**WER moyen par condition (Table 6.1)**

| Cond. | Description | WER | CER | RTF (CPU) |
|---|---|---|---|---|
| A | Baseline (tiny, auto) | 63.4 % | 43.6 % | 0.323 |
| B | + Noise reduction | 62.2 % | 44.6 % | 0.372 |
| D | + Domain prompt | 61.3 % | 45.2 % | 0.351 |
| E | + Forced language | 59.6 % | 41.1 % | 0.260 |
| F | Base model (sans prompt) | **48.4 %** | 33.6 % | 0.635 |

**Effet du bruit (Table 6.2, baseline A)** : clean **47.0 %** → noisy **96.4 %** (≈ ×2).
Noise reduction sur noisy : 96.4 % → **88.1 %** (−8.3 pts). Sur clean : 47.0 % → 49.2 % (+2.2 pts, petit coût).

**WER par langue (Table 6.3)** : allemand toujours le plus bas, français le plus haut.

| Cond. | EN | FR | DE |
|---|---|---|---|
| A | 69.6 | 69.1 | 51.6 |
| E | 60.2 | 74.8 | **43.9** |
| F | 47.7 | 64.1 | 33.2 |

**Gradient de mismatch détection auto vs forcée** : EN 0 % · DE 17 % (2/12) · FR **42 %** (5/12).

## 2. Les 4 findings (verdict des hypothèses)

1. **Bruit = facteur dominant.** Double le WER, loin devant tout le reste.
2. **H1 partiellement confirmée.** Noise reduction aide le bruité, coûte un peu sur le propre → vrai compromis.
3. **H4 fortement confirmée — LE résultat phare.** Forcer la langue récupère le script FR (fini le cyrillique/hébreu), coût zéro, immédiatement déployable.
4. **H2 non testable.** Le dataset ne contient pas de vocabulaire Nestlé → on ne mesure que le *coût* du prompt (−1 pt + 1 hallucination "Nestlé Ghana"), pas son bénéfice. H3 (RTF < 1) confirmée.

## 3. Réponses aux 5 questions pièges

**Pourquoi forcer la langue corrige le script FR mais ne bouge pas le WER FR ?**
Le WER compare mot à mot : un texte cyrillique (≈100 %) et un texte français inexact (≈85 %) sont tous deux "loin" de la référence. Le gain est qualitatif (lisible par un humain), pas quantitatif. → On rapporte les deux.

**Pourquoi le domain prompt a dégradé la précision ?**
Sur un signal de faible confiance (bruité + détection auto), le décodeur autorégressif se rabat sur son contexte = le prompt injecté, et écho "Nestlé Ghana" dans une transcription allemande. Arme à double tranchant.

**Pourquoi MInDS-14 et pas un corpus Nestlé ?**
Corpus Nestlé confidentiel + pas encore reçu ; CommonVoice/LibriSpeech/FLEURS impraticables dans le sandbox. MInDS-14 = CC-BY-4.0, multilingue, parole spontanée réelle. Choix contraint, documenté, assumé. **Ne jamais dire "pour prouver que ça marche".**

**Batch vs WebSocket — 3 différences techniques :**
(1) VAD Silero seulement dans le WebSocket ; (2) noisereduce seulement dans le batch ; (3) langue paramétrable dans le batch, hardcodée `fr` dans le WebSocket.

**Pourquoi le bruit double le WER / que fait noisereduce ?**
Spectral gating : estime le profil de bruit fréquentiel et atténue les fréquences sous le seuil. Aveugle → sur du propre, il rabote aussi les consonnes fricatives faibles (s, f, ch).

## 4. Réflexes code (à savoir tracer)

- **int8 (CPU) vs float16 (GPU)** : int8 = quantification, ÷4 mémoire + SIMD, faible perte. C'est aussi pourquoi 52/180 WER diffèrent entre CPU et GPU (divergence du décodage).
- **`condition_on_previous_text=True`** : maintient le contexte mais risque d'effet boule de neige sur audio bruité/long.
- **`run_in_executor`** : empêche les appels bloquants (Whisper) de geler la boucle asyncio.
- **RAG** : ChromaDB **cherche** (similarité vectorielle), Ollama/Llama3.2 **génère**. Jamais l'inverse.
- **Gaps assumés** : VAD chargé mais jamais appelé dans `transcribe_file` ; langue détectée non loggée ; `/health` peut répondre "ok" avant que Whisper soit prêt.
