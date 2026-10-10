# Dossier de compilation TeXPage — Mémoire Topic 2

Révision 5. Traite le dernier avertissement de police restant après la
compilation précédente.

## Statut

**Sources préparées ; rendu à vérifier sur TeXPage.**

## Configuration

| Réglage | Valeur |
|---|---|
| Fichier principal | `main_revised.tex` |
| Moteur | pdfLaTeX |
| Outil bibliographique | BibTeX |
| Jobname | `output` |

### Chaîne de compilation

pdfLaTeX s'exécute sur `main_revised.tex`; seul BibTeX prend le jobname :

    pdflatex -jobname=output main_revised.tex
    bibtex   output
    pdflatex -jobname=output main_revised.tex
    pdflatex -jobname=output main_revised.tex

Il n'existe pas de fichier `output.tex` : `pdflatex output` échouerait.

Les **trois** passes pdfLaTeX après BibTeX sont nécessaires : la table des
matières est en fin de document, et `shorttoc`, `tocloft` et `hyperref` ont
besoin d'un cycle supplémentaire pour stabiliser pagination et ancres.

## Correctifs de cette révision

| # | Avertissement du log | Cause | Correctif |
|---|---|---|---|
| 1 | Overfull ~24.8 pt, table III.7 | 7 colonnes × 12 pt de `\tabcolsep` = 84 pt de marges internes | `\tabcolsep` 6 pt → 3.5 pt dans cette table seule (libère 35 pt). `\small` conservé, aucune réduction de police supplémentaire |
| 2 | Justification excessive, couverture | colonnes `p{}` justifiées par défaut | `\raggedright` sur les colonnes 2 et 3 du tableau du jury |
| 3 | `name{page.1}` dupliquée | la couverture est la page arabe 1 et le corps redémarre à la page arabe 1 | `\pagenumbering{Roman}` avant `\begin{titlepage}` |
| 4 | `T1/lmss/bx/sc` et `T1/lmss/m/sc` indisponibles (l. 129, 135, 670) | Latin Modern Sans n'a **pas** de petites capitales | `\textsc` retiré à ces trois endroits |
| 5 | `T1/lmr/bx/sc` indisponible (l. 254) | Latin Modern Roman n'a **pas** de petites capitales grasses | `\scshape` retiré du `\titleformat{\chapter}` |
| 6 | `T1/lmss/m/sc` en taille 12 (l. 672) | **pas dans le balisage** : biblatex compose les libellés « URL » et « DOI » en petites capitales via `\mkbibacro`, dans un document rendu sans-serif par le canevas | `\mkbibacro` redéfini pour sélectionner explicitement le romain (`T1/lmr/m/sc`) |

Aucune prose, aucun chiffre, aucune référence modifiés.

### Sur les petites capitales — correction d'une affirmation précédente

La révision précédente ajoutait `lmodern` en affirmant qu'il fournirait la
variante grasse en petites capitales. **C'était faux.** Latin Modern ne
possède ni `bx/sc` en romain, ni aucune petite capitale en sans-serif. Le log
l'a montré : les quatre avertissements ont persisté après son ajout.

La correction retenue est celle demandée : n'utiliser que des variantes
réellement disponibles. Aux quatre endroits concernés, LaTeX substituait déjà
la variante sans petites capitales (`lmss/bx/n`, `lmr/bx/n`) — c'est ce que
montre le PDF à 51 pages. Retirer `\textsc` et `\scshape` produit donc
**exactement le même rendu**, sans avertissement.

`lmodern` est conservé, mais pour la seule raison qui tient : il fournit des
fontes T1 vectorielles et évite le repli sur des bitmaps. Il ne joue aucun
rôle dans les petites capitales.

**Pourquoi tout le document est en sans-serif.** Le canevas contient, à la
ligne 90, `\renewcommand{\familydefault}{\sfdefault}`. La famille par défaut
est donc Latin Modern Sans, qui ne possède aucune petite capitale — d'où tous
les avertissements `T1/lmss/.../sc`. Cette ligne n'a pas été touchée : elle
définit l'apparence voulue par le canevas.

Le dernier avertissement ne venait pas du balisage mais de biblatex, qui
compose « URL » et « DOI » en petites capitales dans chaque entrée. La
redéfinition de `\mkbibacro` encadre ces deux libellés par `\rmfamily`, c'est-
à-dire exactement la famille que LaTeX substituait déjà : **le rendu de la
bibliographie est inchangé**, la substitution n'est simplement plus implicite.
Si cette redéfinition posait problème, l'alternative est de l'accepter telle
quelle : il s'agit d'une notice de substitution, pas d'une erreur, et le texte
produit est correct.

### Sur l'ancre `page.1` — pourquoi `plainpages=false` ne suffisait pas

`plainpages=false` demande à hyperref de nommer l'ancre d'après `\thepage`.
Or la couverture était la page **1 en chiffres arabes**, et le corps redémarre
à la page **1 en chiffres arabes** (`\pagenumbering{arabic}` puis
`\setcounter{page}{1}`). Les deux ancres s'appelaient donc réellement `page.1`,
et l'option ne pouvait pas les distinguer.

En numérotant la couverture en romain, son ancre devient `page.I`. La
`titlepage` utilise `\thispagestyle{empty}` : **aucun numéro n'apparaît sur la
couverture**, avant comme après. La séquence `II, III, IV…` de la dédicace et
la reprise arabe du corps sont inchangées, et le canevas n'est pas réorganisé.

## Bibliographie : ce que le log dit vraiment

Trois messages distincts, à ne pas confondre :

1. `Using fall-back bibtex backend: functionality may be reduced/unavailable`
   — **informatif**, conséquence normale de `backend=bibtex`. Pas une erreur.
2. `Please (re)run BibTeX on the file(s): output and rerun LaTeX afterwards`
   — message standard de biblatex quand le `.bbl` est plus ancien que la liste
   de citations du `.aux`. Il disparaît quand la chaîne complète est allée à
   son terme. Après une modification du source, il réapparaît au premier
   passage : c'est attendu.
3. Les « références non résolues » proprement dites se signalent par des lignes
   `LaTeX Warning: Citation '...' undefined` ou
   `There were undefined references`. **Ces lignes ne figurent pas dans
   l'extrait fourni**, et ne peuvent donc pas être identifiées ici.

Ce qui est vérifié dans le source et dans le PDF à 51 pages :

- 50 clés `\cite` ↔ 50 entrées du `.bib`, aucune manquante ni orpheline ;
- 12 `\label`, aucun dupliqué, aucun `\ref` sans cible ;
- dans le PDF, les appels vont de [1] à [50] et la bibliographie liste bien
  50 entrées numérotées ; aucun `[?]` n'a été repéré.

Si le log signale encore des références non résolues après une chaîne complète,
il faut le `output.blg` et les lignes `Citation ... undefined` pour les nommer.

## Contenu

| Fichier | Rôle |
|---|---|
| `main_revised.tex` | fichier principal |
| `topic2_completion.tex` | inclus par `\input` |
| `bibitem_revised.bib` | 50 entrées |
| `image/logoBIT.png` | seule image utilisée |
| `image/lami.jpeg` | non référencée, conservée |

Risque résiduel non traité : `bibitem_revised.bib` l. 370, un `é` brut dans un
champ `note={}`. Si un caractère parasite apparaît dans la bibliographie,
remplacer par `\'e`.

## Marges appliquées (rappel)

| Zone | Marges |
|---|---|
| Couverture → Dédicace | `total={170mm,257mm}, left=20mm, top=20mm` |
| Remerciements → fin | `\newgeometry{left=2.25cm, top=2.2cm, bottom=2.2cm}` |

Il n'y a **aucun `\restoregeometry`** : la seconde `\newgeometry` gouverne tout
le corps, bibliographie et complément Topic 2 compris. La largeur de texte y
est calculée par `geometry` et ne vaut pas 170 mm.

## Contrôles après compilation

1. Log : relever tous les `Overfull \hbox` restants, ligne et ampleur, et les
   examiner un par un — aucun seuil d'acceptation automatique.
2. Log : plus de `Font shape ... undefined` ni de `... not available`.
3. Log : plus de `destination with the same identifier (name{page.1})`.
4. `output.blg` : BibTeX se termine sans erreur ni clé absente.
5. Log : les lignes `Citation ... undefined`, s'il en reste, avec leurs clés.
6. PDF, table III.7 : les sept colonnes tiennent dans la justification, les
   valeurs restent lisibles et exactes.
7. PDF, couverture : le nom du directeur n'est plus étiré ; les champs
   administratifs affichent toujours « To be confirmed ».
8. PDF, couverture : toujours aucun numéro de page visible.
9. PDF : dédicace en II, corps redémarrant en 1, séquence inchangée.
10. PDF : signets menant à la bonne section (Topic 2 Completion Audit,
    Dédicace, Résumé, Abstract, General Introduction).
11. PDF : intégrité du contenu — chapitres, tableaux, figures, bibliographie
    à 50 entrées, complément Topic 2 en fin de document.

La pagination peut légitimement changer. Ce qui doit être contrôlé est le rendu
et l'intégrité du contenu, pas la conservation d'un nombre de pages.
