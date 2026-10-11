# Livraison TeXPage — Mémoire Topic 2 — 16 septembre 2026

Statut : **prêt pour relecture scientifique, avec couverture partielle du proposal à apprécier par le professeur ; compilation et inspection du PDF à faire sur TeXPage.**
Aucun PDF n'a été produit ici.

## Configuration TeXPage

| Réglage | Valeur |
|---|---|
| Fichier principal | `main_revised.tex` |
| Moteur | **pdfLaTeX** (`\UseRawInputEncoding`, `inputenc[utf8]`, `fontenc[T1]` : pas XeLaTeX) |
| Bibliographie | **BibTeX** — `biblatex` avec `backend=bibtex` ; **pas Biber** (sinon toutes les citations sortent en `[?]`) |
| Jobname observé | `output` |

Chaîne (le jobname TeXPage est `output`, le fichier principal reste `main_revised.tex`) :

    pdflatex -jobname=output main_revised.tex
    bibtex   output
    pdflatex -jobname=output main_revised.tex
    pdflatex -jobname=output main_revised.tex

Trois passes après BibTeX : table des matières en fin de document, `shorttoc`, `tocloft`, `hyperref`.
`makeindex` inutile (`\makenomenclature` sans `\printnomenclature`). Vider le cache TeXPage avant de relancer.

## Contenu

| Fichier | Rôle |
|---|---|
| `main_revised.tex` | document principal (corrigé le 16/09/2026, voir journal des corrections) |
| `topic2_completion.tex` | complément Topic 2, inclus par `\input` |
| `validation_20260916.tex` | **annexe datée** : audit complémentaire du 16 septembre 2026, incluse après le complément |
| `bibitem_revised.bib` | 50 entrées |
| `image/logoBIT.png` | seule image référencée ; `image/lami.jpeg` non référencée, conservée |

## Vérifications statiques effectuées (sans compilateur)

- 0 référence de fichier non résolue (`\input`, `\includegraphics`, `\bibliography`)
- 50 clés `\cite` ↔ 50 entrées `.bib`, aucune manquante, orpheline ni dupliquée
- 14 `\label` uniques, 0 `\ref` sans cible (3 labels non référencés : tables listées dans la liste des tableaux)
- environnements `\begin`/`\end` appariés dans les trois fichiers ; aucun chemin absolu
- 0 tableau à largeur fixe en dépassement prévisible (les tableaux dimensionnés par le contenu ne sont
  vérifiables que dans le log)
- 28 paquets, tous standard TeX Live

## Non vérifié ici, à contrôler dans le PDF TeXPage

Compilation sans erreur ; `Overfull \hbox` ; ancres hyperref ; rendu des deux tableaux de l'annexe
(`tab:annex_revision`, `tab:annex_contrasts`) ; nombre de pages (peut changer, l'annexe ajoute ~3 pages) ;
placeholders « To be confirmed » (date, président, examinateur) toujours à renseigner.
Risque résiduel connu : un `é` brut ligne 370 du `.bib` (`\'e` si un caractère parasite apparaît).
