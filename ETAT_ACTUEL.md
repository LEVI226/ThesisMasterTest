# État actuel du projet — Mémoire Topic 2 (STT)

> Document de référence (« source de vérité ») pour tout agent qui reprend le projet.
> Dernière mise à jour : audit des insuffisances du Topic 2, 10 septembre 2026.
> Lire `COMPLEMENTS_TOPIC2.md` et `results/topic2_readiness_audit.md` avant de préparer la soutenance.
> L'utilisateur confirme une soutenance en anglais : préparation bilingue dans `GUIDE_SOUTENANCE_ANGLAIS_FR_EN.md`, questions et audios dans `training/english_defense/`.
> **Périmètre du mémoire : Topic 2 (Speech-to-Text) UNIQUEMENT.** L'OCR (Topic 1) et la
> couche de personnalisation / étude utilisateur (Topic 3) sont portés par d'autres et
> ne font PAS partie de ce mémoire.

---

## 1. Identité

- **Titre** : *Advanced Speech-to-Text Models for Noisy, Multilingual Corporate Meetings: Evaluation of a Whisper-Based Pipeline for Workplace Accessibility*
- **Auteur** : OUEDRAOGO Yannick Ulrich Levi — **Directeur** : Dr.-Ing. Lebian Wilfried NIKIEMA
- **École** : Burkina Institute of Technology (BIT), Master Intelligence Artificielle
- **Langue de soutenance indiquée dans le projet : ANGLAIS.** La version corrigée de travail est `main_revised.tex`, avec `bibitem_revised.bib`. `main.tex` est une version antérieure ; ne pas la confondre avec la révision. `main_FR.tex` est une traduction bonus non synchronisée.

---

## 2. Jeu de données CANONIQUE (à ne jamais changer)

- **Corpus** : PolyAI/MInDS-14 (licence CC-BY-4.0), parole téléphonique bancaire réelle, mono-locuteur, **8 kHz**.
- **Langues** : anglais (en), français (fr), allemand (de).
- **Jeu d'évaluation : 36 clips** = 24 propres (8/langue) + 12 bruités (4/langue).
- **Bruit : bruit blanc synthétique à 8 dB de SNR** (PAS 10 dB).
- **Split d'entraînement LoRA** : 300 clips (100/langue), non-contamination vérifiée (exclusions en=8, fr=12, de=8 ; graine=42 ; assertion finale : aucun recoupement train/éval).
- **Scorer** : implémentation Levenshtein autonome dans `backend/evaluation/metrics.py` (WER + CER), normalisation = minuscules + suppression ponctuation + réduction espaces. **Même scorer pour TOUS les modèles.**

⚠️ **Ne PAS utiliser** MLS / FLEURS / Common Voice / VoxPopuli comme jeu principal, ni un SNR de 10 dB, ni 8 clips. Tout artefact de ce type est un pipeline parallèle égaré, hors mémoire.

---

## 3. Campagne expérimentale — 468 runs de transcription (tous vérifiés)

Même jeu (36 clips) + même scorer partout. Chiffres = WER moyen sauf mention.

### 3.1 Pilote CPU (INT8), 180 runs — 5 conditions chaînées
| Cond. | Modèle | WER | Note |
|---|---|---|---|
| A Référence | tiny | 63,4 % | baseline |
| B Réduction bruit | tiny | 62,2 % | spectral gating |
| D Prompt métier | tiny | 61,3 % | vocabulaire Nestlé |
| E Langue forcée | tiny | 59,6 % | |
| F Modèle base | base | 48,3 % | |

Effet du bruit sur **12 paires : 61,1 % → 96,4 %, +35,3 points, IC 95 % [7,0 ; 60,0]**. Le contraste 47,0 % (24 propres) contre 96,4 % (12 bruités) est descriptif, car les groupes ne contiennent pas les mêmes phrases.

### 3.2 Extension GPU (RTX 4060, float16), 288 runs
- **Échelle de tailles** (G/H/I = small/medium/large-v3) : WER 33,3 / 25,9 / 24,6 %. Échelle complète tiny→large-v3 : **63,4 → 24,6 %**, bruité 88,1 → 40,7 %. Monotone, rendements décroissants après medium.
- **Condition C (VAD)**, 36 runs : compromis miroir (propre −3,8, bruité +6,0 ; réf = B re-mesurée sur GPU).
- **LoRA appariée (J0/J)**, 72 runs : whisper-small 31,2 % → 30,2 % (≈1 pt, non significatif à n=36).
- **wav2vec 2.0 / MMS**, 36 runs : 35,4 % (langue donnée par construction).
- **Conformer / NeMo CTC (nvidia/stt_{en,fr,de}_conformer_ctc_large)**, 36 runs : **26,3 %** global ; par langue de 15,3 / fr 23,6 / en 39,8 ; propre 17,5 / bruité 43,7 ; RTF médian 0,014. Langue donnée par construction.

### 3.3 Hors WER
- **Diarisation** : 7 réunions simulées, pyannote 3.1, DER moyen 0,585 (à lire comme artefact du banc d'essai, pas qualité de pyannote).
- **Latence historique** : 22 observations, dont 20 hors premiers énoncés ; médiane 0,555 s, p95 0,844 s, maximum 1,177 s. **Journal actuel** : 38 observations ; 35 hors premiers énoncés, médiane 0,575 s, p95 1,614 s, maximum 11,021 s. Les paramètres des sessions ne sont pas consignés ; résumé descriptif seulement. Chronomètre serveur avant envoi, pas mesure du rendu client.

### 3.4 Constats clés (défendables, tracés jusqu'aux CSV)
1. Le **bruit augmente le WER de 35,3 points** sur les 12 paires ; l'incertitude reste large.
2. La **taille du modèle** est le levier de précision n°1 (échelle monotone).
3. La **langue fournie** corrige plusieurs sorties dans un mauvais alphabet ; le désaccord auto/forcé ne constitue pas une mesure directe d'exactitude de détection de langue.
4. **Prompting et LoRA ≈ 1 point** chacun. LoRA : IC groupé [-2,4 ; 5,3], donc gain non établi. L'absence de vocabulaire cible empêche de conclure sur Nestlé ; la couverture du domaine par le préentraînement est une hypothèse, pas un résultat mesuré.
5. **Fuite de prompt** mesurée (« Nestlé Ghana » halluciné).
6. MMS/Conformer rapides (CTC) mais **langue donnée par construction** → comparaison honnête = entre eux ; Whisper reste le meilleur pour l'usage réel (détection multilingue native, ponctuation, horodatage, robustesse téléphonie bruitée).

---

## 4. Cartographie des fichiers (racine : `ThesisMasterTest/`)

- `Memoire_LaTeX/main_revised.tex` — **révision anglaise de travail**, statistiques corrigées et complément Topic 2 ; compiler avec sa bibliographie révisée. `main.tex` conservé comme version antérieure.
- `Memoire_LaTeX/main_FR.tex` — traduction française (bonus). **PAS encore synchronisée avec Conformer** (à faire).
- `Memoire_LaTeX/bibitem_revised.bib` — bibliographie de la révision ; `bibitem.bib` appartient à la version antérieure.
- `Memoire_LaTeX/main_backup_withdash.tex`, `main_backup_predash.tex` — sauvegardes.
- `backend/evaluation/metrics.py` — scorer WER/CER canonique ; `dataset.py` — chargement du jeu.
- `backend/training/` — scripts d'éval : `eval_wav2vec.py` (MMS), `eval_conformer.py` (nouveau), `eval_lora.py`, `train_lora.py`, `build_train_split.py`, `build_meetings.py`, `eval_meetings.py`.
- `results/` — CSV de résultats, un par étude (dont `stt_eval_conformer_results.csv`, `stt_eval_wav2vec_results.csv`, résultats pilote/GPU/LoRA/diarisation/latence). **Ce sont les sources de vérité chiffrées.**
- `Soutenance_Deck_Contenu.md`, `Message_Superviseur.md`, `Audit_Bibliographie.md`, `Fiche_Revision_Soutenance.md`, `Antigravity_Prompts.md`.

Environnement code : Windows, `.venv` (torch 2.6.0+cu124, CUDA RTX 4060, NeMo 3.0.0). Le LaTeX ne compile PAS dans un sandbox sans babel-french/biblatex — utiliser Overleaf/TeXPage.

---

## 5. Ce qui est FAIT
- Thèse rédigée ; révision de travail `main_revised.tex`. La validation complète du Topic 2 reste partielle.
- Les **3 baselines ASR obligatoires** (Whisper + wav2vec 2.0/MMS + Conformer) évaluées → R4 couvert.
- Tous les chiffres re-vérifiés contre les CSV (Conformer re-scoré indépendamment : 0,266 vs 0,263 stocké).
- Bibliographie auditée (45 refs, dont Koenecke 2024 vérifiée pour les boucles), tirets cadratins retirés, LaTeX équilibré.
- **`AI_METHODOLOGY.md`** rédigé (couvre les 4 sections obligatoires du challenge).
- **Bootstrap corrigé** : `python -m backend.evaluation.run_statistical_audit`. Bruit apparié +35,3 pts [7,0 ; 60,0] ; taille B−I 37,6 pts [24,3 ; 50,7] ; LoRA 1,0 pt [-2,4 ; 5,3]. Les copies propres/bruitées restent groupées pour les comparaisons de systèmes. `results/bootstrap_ci.md` est historique et ne doit pas remplacer cet audit. La partie latence du script utilise le journal courant.
- **Validité externe FLEURS** (large-v3 uniquement, 7,4 %) ajoutée à `main.tex`, étiquetée hors campagne canonique.

## 6. Ce qui est EN ATTENTE
- Synchroniser `main_FR.tex` avec l'ajout Conformer (468 runs + sous-section).
- (Optionnel, réserve GPU) **Test AMI** (validité externe multi-locuteurs) : large-v3 seul, ~20 segments courts, scorer canonique, étiqueté à part. À ne lancer que s'il reste du temps ; jamais fusionné.
- Envoyer le PDF au Dr Nikiema (message prêt dans `Message_Superviseur.md`).
- **FLEURS** : DÉJÀ lancé (`results/stt_eval_fleurs_results.csv`, 300 runs, propre uniquement). NON intégrable en l'état — boucles de répétition sur tiny→medium (WER jusqu'à ~900 %). Seul **large-v3 (7,4 %)** est exploitable et a été ajouté comme note de validité externe. **Ne PAS rapporter** les autres tailles FLEURS ni fusionner dans les tableaux MInDS-14.
- Répétition de soutenance.

## 7. À NE PAS FAIRE (hors périmètre)
- Ne pas construire OCR (Topic 1), couche perso/étude utilisateur (Topic 3), ni déploiement Azure/Teams/Outlook.
- Ne pas fusionner de résultats issus d'un autre jeu de données ou d'un autre SNR (ex. pipeline 8 clips / 10 dB / MLS) dans les tableaux canoniques.
- Ne pas coller de chiffres non tracés jusqu'à un CSV. Tout nombre du mémoire doit être reproductible.
