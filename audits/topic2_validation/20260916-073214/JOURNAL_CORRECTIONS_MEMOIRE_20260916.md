# Journal des corrections du mémoire — 16 septembre 2026

Fichiers : `Memoire_LaTeX/main_revised.tex` (10 modifications ciblées, +39/−19 lignes ; original conservé sous
`pristine/main_revised.tex.manuscript_orig`), `Memoire_LaTeX/validation_20260916.tex` (nouvelle annexe datée, incluse
après `topic2_completion.tex`). Aucun chiffre historique modifié ; aucun résultat, référence ou code touché.

| # | Endroit | Correction | Preuve |
|---|---|---|---|
| 1 | Abstract EN / FR | La latence 0,56 s / 0,84 s est qualifiée de temps de calcul post-déclenchement, distinct du délai de sous-titrage, non borné faute de longueur maximale d'énoncé ; ajout du constat de réannotation (7/16 références en+fr présentent des différences, dont 2 sur des hésitations, passages incertains conservés) et du résultat de la révision de sensibilité (ordre préservé, petits contrastes contenant 0) | `09c`, sessions 17:51 ; `reannotation/CHANGELOG`, `revision_v2` |
| 2 | I.1.2 Métriques | Estimateur explicité : moyenne des WER par fichier sur 36 fichiers (24 propres + 12 bruités, en/fr/de), pas WER global pondéré ; WER > 100 % possible ; variantes bruitées = copies dérivées, non indépendantes | scorer `metrics.py` ; `03b_contrasts.md` (63,4 % vs 66,8 % agrégé) |
| 3 | III.3.2 H4 | « strongly supported » → « supported at the script level », effet agrégé non établi, IC [−2,6 ; +7,0] | `revision_v2/REVISION_v2.md` |
| 4 | III.3.2 RQ3 | Trois grandeurs distinguées (RTF, temps post-déclenchement, délai de bout en bout) ; absence de longueur maximale d'énoncé déclarée ; blocs de 70 s et 149 s cités comme observations de l'audit complémentaire du 16 septembre 2026 | `backend/main.py` (aucune borne) ; session 17:51 (149 s clos par `end_signal`) |
| 5 | III.3.2 Diarisation | Ajout des limites du live : fenêtre de 10 s, dernier locuteur attribué au bloc, aucun suivi d'identité ; une étiquette récurrente n'établit pas un locuteur | `backend/main.py` l. 396–413 ; `diarization_20260916/DIAGNOSTIC.md` |
| 6 | III.3.3 Hypothèses revisitées | H4 : support qualitatif au niveau graphie ; effet agrégé non établi | idem 3 |
| 7 | III.3.3 Positionnement | Comparaison qualitative externe signalée en annexe, « not a benchmark » | `09_*`, `09b` |
| 8 | Conclusion | LoRA : « aucun bénéfice établi, équivalence non montrée » ; références : différences après réannotation, niveaux absolus probablement surestimés, ordre préservé, allemand non vérifié | `revision_v2` |
| 9 | Nouvelle annexe A.1–A.7 | Corrections logicielles datées (ingénierie, non validation) ; intégrité des références (16/24, pas totalement à l'aveugle, 2ᵉ écoute non indépendante, passages incertains, convention verbatim) ; révision de sensibilité avec tableaux original/révisé et IC groupés par clip source ; facteurs changés par contraste (B–I change taille **et** backend) ; observations live micro (1 locuteur, pas de causalité) ; AGM 2026 (entités, salutation trilingue, rejeu, comparaison externe non-benchmark, données internes non évaluées) ; diarisation (exécution ≠ précision) ; liste des non-démontrés et classes de données | dossier de validation complet |
| 10 | `\input{validation_20260916}` | inclusion de l'annexe après le complément Topic 2 | — |

Corrections dans les documents d'audit (même date) : diarisation « intermittente » → « réparée à 14:02 par une autre
session » ; bloc de 149 s clos par `end_signal` et non par silence ; annotation « à l'aveugle » → « pas totalement à
l'aveugle, seconde écoute par le même auteur » ; LoRA « bruit » → « aucun bénéfice établi ».

Non fait, volontairement : aucune nouvelle expérience ; aucune longueur maximale d'énoncé implémentée (changerait la
sémantique de latence du mémoire ; laissée en perspective) ; aucune réécriture du protocole initial.

Corrections de formulation (même jour, seconde passe) : « post-submission » → « supplementary audit conducted on
16 September 2026 » / « audit complémentaire du 16 septembre 2026 » ; « références défectueuses » → « sept références
présentent des différences après réannotation », deux sur des hésitations, passages incertains conservés ; langue
forcée nuancée partout (abstract EN/FR, H4, résumé du chapitre III, conclusion, annexe A.3 et A.5) : « peut aider
lorsque la langue attendue est connue et stable, mais ne résout pas les changements de langue au sein d'une même
intervention » ; verdict : « prêt pour relecture scientifique, avec couverture partielle du proposal à apprécier par le
professeur ».
