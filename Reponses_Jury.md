# Réponses jury — préparation soutenance (Topic 2 STT)

Réponses courtes, honnêtes, ancrées sur les chiffres réels. À dire calmement, sans sur-promettre.

---

## 1. « Pourquoi ne pas simplement utiliser Azure / Google Speech ? »
- **Souveraineté des données** : le pipeline est 100 % local (Phase 1), aucun audio ne quitte la machine. C'est la contrainte n°1 de Nestlé (cf. NesGPT, créé précisément pour garder l'IA générative sous contrôle interne). Un SaaS cloud enverrait de la voix confidentielle à un tiers.
- **Comparaison équitable** : mon protocole compare des modèles **ouverts** sur un **même harnais et un même scorer**. Une API SaaS est une boîte noire non auditable : je ne peux ni mesurer ni adapter sa précision sur l'audio de l'organisation.
- **Preuve que le pipeline n'est pas en cause** : sur parole propre large bande (FLEURS), large-v3 atteint **7,4 %** de WER. La difficulté MInDS-14 vient donc de la téléphonie + bruit + spontanéité, pas de mon pipeline. Un SaaS affronterait exactement la même difficulté acoustique.
- Honnête : « Comparer chiffré à Azure serait une extension utile ; les WER publiés d'Azure peuvent servir d'approximation, mais un test équitable exigerait de faire tourner Azure sur mon jeu, ce qui sort du périmètre master. »

## 2. « n = 36 clips, ce n'est pas statistiquement fragile ? »
- Réponse chiffrée (bootstrap 95 %, `results/bootstrap_ci.md`) :
  - **Gros effets robustes** : écart tiny→large-v3 = **37,6 pts, IC [20,9 ; 53,6]** (exclut 0) ; pénalité bruit = **49,4 pts, IC [23,4 ; 75,8]** (exclut 0).
  - **Petits effets, je ne les survends pas** : LoRA = 1,0 pt, IC **[−15,3 ; 17,8]** → traverse 0, **non significatif**, et ma thèse le dit déjà. Les étapes voisines (medium/large) et l'ordre MMS/Conformer se chevauchent aussi à n=36 : ce sont des points-estimés, pas des écarts prouvés.
- Message : « Mes conclusions fortes tiennent statistiquement ; mes conclusions faibles sont explicitement présentées comme non significatives. C'est une limite assumée, pas cachée. »

## 3. « Votre diarisation fonctionne ? DER = 0,585 »
- Déjà cadré comme **artefact du banc d'essai**, pas qualité de pyannote : la vérité terrain marque tout le clip comme parole (pauses incluses) → « parole manquée » par construction ; les clips concaténés viennent de vrais locuteurs différents → la sur-segmentation est souvent pyannote qui a raison ; les réunions bruitées ont un « meilleur » DER que les propres, ce qui est implausible → preuve que le DER mesure l'artificialité du banc.
- Honnête : « La diarisation tourne mécaniquement de bout en bout ; une mesure de précision valide exige de vraies réunions multi-locuteurs à continuité par locuteur. L'optimisation de la diarisation est hors périmètre de ce mémoire (Topic 2 = STT). »

## 4. « MInDS-14 = téléphonie mono-locuteur, ce ne sont pas des réunions d'entreprise »
- **Vraie limite, assumée en premier plan.** Raisons : pas de données Nestlé (RGPD / confidentialité / délai master) ; les corpus publics recommandés (Common Voice, LibriSpeech, FLEURS, VoxPopuli) impraticables dans l'environnement initial.
- **Argument fort** : à ma connaissance, **aucun corpus public de réunions d'entreprise EN/FR/DE bruitées n'existe** (VoxPopuli = multilingue mais mono-locuteur ; AMI/ICSI = réunions mais anglais seul ; pas de corpus multilingue de réunion). Je ne pouvais pas télécharger ce qui n'existe pas.
- **Mitigation montrée** : réunions multi-locuteurs simulées pour exercer la diarisation, et validité externe FLEURS (parole propre) pour isoler la cause de la difficulté.
- Si demandé « et de vraies réunions ? » : AMI serait le prochain test de validité externe (large-v3, étiqueté à part) — préparé, non lancé faute de temps.

## 5. « FLEURS : pourquoi seulement large-v3 ? Les petits modèles à 900 % ? »
- Ce ne sont pas des erreurs de mesure : c'est un **mode de défaillance long-form documenté** de Whisper (boucle de répétition auto-renforcée, `condition_on_previous_text=True`, sans les gardes `compression_ratio_threshold`/fallback température). Réf : Radford et al. 2023 ; Koenecke et al. 2024 (vérifiée, DOI 10.1145/3630106.3658996).
- J'ai **gardé le même décodage déterministe que la campagne MInDS-14** pour la comparabilité, donc je n'ai pas activé les gardes juste pour FLEURS (ça créerait deux protocoles). J'exclus donc tiny→medium sur FLEURS et ne rapporte que large-v3 (robuste, 7,4 %). La boucle elle-même est un **constat qualitatif citable**.

---

### Rappels de posture
- Dire « à notre connaissance » pour les arguments d'absence de corpus.
- Ne jamais survendre : les effets faibles sont non significatifs, je le dis.
- Chaque chiffre est traçable jusqu'à un CSV de `results/` + scorer `backend/evaluation/metrics.py`.
