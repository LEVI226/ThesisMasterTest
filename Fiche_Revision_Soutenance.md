# Fiche de révision — Soutenance Topic 2 (STT)

> À connaître par cœur. Tous les chiffres viennent de `results/stt_eval_pilot_results.csv` (run CPU int8) et du Chapitre 6.

## 0. NOUVEAU — Échelle complète des tailles de modèles (runs GPU, RTX 4060 Laptop 8 Go)

| Modèle | Params | WER | CER | WER propre | WER bruité | RTF (GPU fp16) |
|---|---|---|---|---|---|---|
| tiny (B) | 39M | 62.2 % | 44.6 % | 49.2 % | 88.1 % | 0.144 |
| base (F) | 74M | 48.3 % | 33.6 % | 32.9 % | 79.2 % | 0.188 |
| small (G) | 244M | 33.3 % | 24.6 % | 21.6 % | 56.7 % | 0.146 |
| medium (H) | 769M | 25.9 % | 21.1 % | 17.3 % | 43.3 % | 0.195 |
| large-v3 (I) | 1.55B | **24.6 %** | **20.5 %** | 16.6 % | **40.7 %** | 0.359 |

**Par langue (WER)** : FR s'effondre 64.1 (base) → 33.5 (small) → 21.8 (large-v3). DE atteint **8.3 %**. EN devient la PIRE langue à grande taille (43.8 %) — tiré par quelques clips difficiles persistants.

**Les 3 phrases clés :**
1. Courbe **strictement monotone** tiny→large-v3, rendements décroissants après medium (medium→large-v3 = seulement −1.3 pt).
2. La taille du modèle fait plus contre le bruit (88→41 %) que noisereduce (−8.3 pts) — c'est le levier dominant.
3. En déploiement : **small = meilleur rapport précision/coût** (WER 33 %, RTF 0.146), **medium = sweet spot** si GPU dispo.

**3 nouvelles questions pièges :**
- *Pourquoi small est aussi rapide que tiny sur GPU (0.146 vs 0.144) ?* → Le RTF dépend aussi de la longueur de sortie : les gros modèles arrêtent le décodage plus tôt au lieu d'étendre des hallucinations longues sur l'audio difficile — ça compense le coût par pas.
- *Peut-on comparer les RTF CPU (tableau principal) et GPU (échelle) ?* → NON, backends différents. La colonne RTF de l'échelle est 100 % GPU fp16 (tiny/base re-mesurés). Et aucun RTF CPU n'a été mesuré pour small+ → on ne PRÉTEND PAS que medium tourne en temps réel sur CPU.
- *Les WER de G/H/I sont-ils comparables à ceux de A-F ?* → Presque : G/H/I sont fp16-GPU, A-F canoniques sont int8-CPU. La divergence inter-backend mesurée (52/180 à tiny/base) est petite devant des effets de 14-24 points. C'est dit tel quel dans le mémoire.

## 0bis. Alignement Proposal BIT/Nestlé → Mémoire (question piège n°1 du jury)

> « Le proposal promettait X, qu'avez-vous livré ? » — Phrase cadre : *« Le proposal définit un programme de recherche à 3 topics ; mon mémoire livre un pilote mesuré du cœur du Topic 2, avec chaque écart documenté et justifié dans le texte. »*

| Promesse du proposal (Topic 2) | Livré | Où / justification |
|---|---|---|
| ASR transformers en bruité/multilingue | ✅ complet | 288 runs, bruit ×2, EN/FR/DE, échelle tiny→large-v3 |
| Adaptation (transfer learning, fine-tuning) | ✅ mesuré | Prompting testé (−0,9 pt + hallucination) ET LoRA fine-tuning testé (−1,0 pt, apparié, contamination PASS). Les deux ≈ 1 pt = ordre de grandeur sous la taille de modèle. Reste hors périmètre : fine-tuning sur vocabulaire Nestlé réel (données confidentielles) |
| Temps réel / latence | ✅ mesuré | RTF < 1 (CPU et GPU) + latence live mesurée : médiane 0.56 s, p95 1.18 s (~1.2 s perçu). Pas de Teams réel ni streaming frame-synchrone (hors périmètre déclaré) |
| wav2vec 2.0, Conformer | ✅/🟡 | wav2vec 2.0 (MMS-1B) benchmarké sur les 36 clips (section 0quinquies) · Conformer discuté avec justification |
| Diarization multi-locuteurs | ✅ exercée | pyannote 3.1 sur 7 réunions simulées, DER rapporté AVEC caveats testbed (section 0quinquies) |
| Datasets "réunions simulées" | ✅ construits | MInDS-14 CC-BY + 7 réunions multi-locuteurs simulées (EN/FR/DE clean+noisy + trilingue), ground truth JSON |
| Intégration Outlook/Teams | ❌ non fait | Phase 2 Azure = intention documentée dans le code, jamais présentée comme réalisée |

## 0ter. « Nestlé a déjà Teams + Copilot qui transcrivent — à quoi sert votre système ? »

Réponse en 3 étages :
1. **Souveraineté des données** : Copilot = cloud Microsoft. Nestlé a créé NesGPT précisément pour avoir du GenAI *interne et sécurisé* → mon Phase 1 100 % local (audio/transcripts/embeddings ne quittent jamais la machine) suit exactement cette logique d'entreprise.
2. **Accessibilité d'abord** : Copilot fait des notes de réunion génériques ; il n'offre ni couche personnalisée pour malentendants, ni garantie mesurée sur le code-switching FR/EN/DE ou le vocabulaire marque. Mon travail mesure précisément ces cas d'échec.
3. **Mesurable et adaptable** : Copilot est une boîte noire — impossible d'en mesurer le WER sur son propre audio ou de le fine-tuner. Mon pipeline est instrumenté (288 runs traçables) et adaptable (prompt métier, LoRA).

## 0quater. NOUVEAU — LoRA fine-tuning (BLOC 6) : la réponse mesurée à la RQ2

**Setup** : 300 clips MInDS-14 (100/langue), contamination check PASS (exclusions EN 8, FR 12 dont 4 doublons corpus, DE 8 ; seed 42 ; assertion finale). LoRA r=16 sur q/v_proj = 1,77M params entraînés (0,73 %), 3 epochs fp16, loss 4,71 → 1,95 en ~2 min.

**Éval APPARIÉE** (même chemin d'inférence HF direct, même scoreur — seuls les poids changent) :

| | WER | CER | Propre | Bruité | EN | FR | DE |
|---|---|---|---|---|---|---|---|
| J0 vanilla (HF) | 31.2 % | 24.2 % | 21.0 | 51.7 | 44.1 | 31.0 | 18.6 |
| J LoRA (HF) | 30.2 % | 23.0 % | 19.2 | 52.2 | 43.0 | 31.0 | 16.8 |

**Par fichier : 7 améliorés, 6 dégradés, 23 identiques** → −1,0 pt NON significatif à n=36. À dire tel quel.

**LA phrase RQ2** : *« Les deux stratégies d'adaptation à bas coût — prompting (−0,9 pt) et LoRA in-domain (−1,0 pt) — atterrissent au même endroit : un point, soit un ordre de grandeur sous l'effet taille de modèle (14-38 pts). Raison déclarée : le domaine d'entraînement est déjà couvert par le pré-entraînement de Whisper. La valeur du fine-tuning se joue sur un vocabulaire réellement divergent — Nestlé — que la contrainte de données interdisait de tester. »*

**3 pièges :**
- *« Pourquoi si peu de gain ? »* → Pas un échec de la méthode (loss 4,7→1,9, pipeline validé) : il n'y avait presque pas d'écart de domaine à combler. Et 300 clips / 3 epochs = pilote.
- *« Votre modèle a-t-il vu les données de test ? »* → Non : exclusion par transcript normalisé (8-12/langue), tirage seedé, assertion finale PASS. Chiffres à réciter.
- *« Pourquoi J0 (31,2) ≠ G (33,3) alors que même modèle ? »* → 2,1 pts d'écart = implémentation (HF/PyTorch vs CTranslate2) + noisereduce. Leçon : l'implémentation pèse autant que l'adaptation étudiée — d'où la discipline "comparaison à backend constant" de tout le Chapitre 3.

## 0quinquies — BLOC 7 : wav2vec/MMS + diarization (les 2 dernières cases du proposal)

**wav2vec 2.0 (MMS-1B-all) vs Whisper-small (J0), mêmes 36 clips, même scoreur :**

| | WER | CER | RTF | EN | FR | DE | Bruité |
|---|---|---|---|---|---|---|---|
| K MMS | 35.4 | **23.6** | **0.028** | 60.0 | **25.4** | 20.7 | 51.4 |
| J0 Whisper-small | **31.2** | 24.2 | 0.085 | **44.1** | 31.0 | **18.6** | 51.7 |

- *Piège : « MMS bat Whisper en français ! »* → Confound déclaré : MMS reçoit la langue PAR CONSTRUCTION (1 adaptateur/langue = langue forcée), J0 était en auto. C'est en partie ton finding H4 qui ressurgit dans une autre architecture.
- Verdict : Whisper reste le bon choix (détection auto, ponctuation, timestamps) ; MMS = alternative CTC crédible si langue connue d'avance (10× plus rapide).

**Diarization — 7 réunions simulées, DER moyen 0.585. LA réponse piège :**
*« DER 58 %, c'est mauvais non ? »* → Ce chiffre mesure l'artificialité du testbed, pas pyannote, et c'est démontrable 3 fois : (1) le "missed" vient des pauses internes aux clips que mon ground truth compte comme parole ; (2) la "sur-segmentation" (3-7 locuteurs détectés) = pyannote a RAISON, les clips MInDS sont de vrais locuteurs différents, c'est mon étiquette A/B qui est la fiction ; (3) preuve : les réunions bruitées ont un MEILLEUR DER (0.505) que les propres (0.644) — impossible pour un vrai gain, c'est le bruit qui masque les voix. Conclusion : pipeline diarization fonctionnel de bout en bout ; une éval valide exige de vraies réunions (données confidentielles = la borne de tout ce travail).

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

**Batch vs WebSocket — état APRÈS le BLOC 5 (à jour) :**
(1) VAD Silero : désormais dans les DEUX chemins (WebSocket depuis toujours ; batch via `vad_filter` natif de faster-whisper → Condition C mesurée) ; (2) noisereduce seulement dans le batch ; (3) langue : paramétrable partout — batch par argument, WebSocket par `?lang=fr|en|de|auto` (défaut auto) ; (4) l'initial_prompt du WebSocket a été SUPPRIMÉ (hallucinations sur silence — cohérent avec le finding "Nestlé Ghana").

**NOUVEAU — Condition C (VAD batch), comparaison même backend GPU fp16 :**

| | WER | CER | RTF | WER propre | WER bruité |
|---|---|---|---|---|---|
| B (GPU) | 62.7 % | 46.4 % | 0.144 | 51.5 % | 85.0 % |
| C_vad (GPU) | 62.2 % | 45.6 % | 0.130 | **47.7 %** | **91.0 %** |

Lecture : gain modeste en agrégé, mais **miroir du compromis noisereduce** — le VAD aide sur le propre (−3.8, il coupe les silences hallucinables) et dégrade le bruité (+6.0, il classe de la parole noyée comme non-parole et la jette). Conclusion : aucun interrupteur de prétraitement n'est activable aveuglément.

**Piège : « le VAD rend 2.9× plus rapide ? »** NON — c'était une comparaison C(GPU) vs B(CPU), interdite. Même backend : 0.144 → 0.130, soit ~10 %. Toujours comparer à backend constant.

**NOUVEAU — Latence live mesurée (RQ3 du proposal)** : 22 énoncés, 2 sessions, RTX 4060 fp16. **Médiane 0.56 s, p95 1.18 s** (hors cold-start de 2.6-3.6 s au 1er énoncé — mitigé en prod par le pré-chargement lifespan). Nuance à connaître : mesuré du seuil de silence → envoi du transcript ; le délai *perçu* ajoute la fenêtre de silence de 0.6 s → ~1.2 s perçu en médiane.
- *Piège : « quel est le WER de la session live ? »* → AUCUN chiffre : pas de référence ground truth. On rapporte la latence (mesurée) et le qualitatif ("Magie" pour Maggi = problème d'entités du Ch. 1 reproduit en live). Ne JAMAIS citer un WER estimé à l'oreille.

**Pourquoi le bruit double le WER / que fait noisereduce ?**
Spectral gating : estime le profil de bruit fréquentiel et atténue les fréquences sous le seuil. Aveugle → sur du propre, il rabote aussi les consonnes fricatives faibles (s, f, ch).

## 4. Réflexes code (à savoir tracer)

- **int8 (CPU) vs float16 (GPU)** : int8 = quantification, ÷4 mémoire + SIMD, faible perte. C'est aussi pourquoi 52/180 WER diffèrent entre CPU et GPU (divergence du décodage).
- **`condition_on_previous_text=True`** : maintient le contexte mais risque d'effet boule de neige sur audio bruité/long.
- **`run_in_executor`** : empêche les appels bloquants (Whisper) de geler la boucle asyncio.
- **RAG** : ChromaDB **cherche** (similarité vectorielle), Ollama/Llama3.2 **génère**. Jamais l'inverse.
- **Gaps assumés** : VAD chargé mais jamais appelé dans `transcribe_file` ; langue détectée non loggée ; `/health` peut répondre "ok" avant que Whisper soit prêt.
