# Journal des prompts et méthodes IA

Ce fichier garde la mémoire des prompts utiles, des méthodes de travail et des règles qui
ont permis d'obtenir de bons résultats. Il ne contient volontairement aucun secret.

## Règle principale

Quand un prompt donne un bon résultat :

1. copier le prompt ou le résumer fidèlement ;
2. noter le contexte du dépôt ;
3. noter les fichiers modifiés ou produits ;
4. noter les commandes lancées ;
5. noter les corrections nécessaires ;
6. transformer le résultat en méthode réutilisable.

## Prompts déjà conservés dans le projet

### `Antigravity_Prompts.md`

Contient les blocs historiques de développement :

- démarrage serveur et vérification CUDA ;
- relance de l'évaluation GPU ;
- extension de la matrice de modèles ;
- ajout VAD, langue détectée, WebSocket paramétrable, latence ;
- entraînement et évaluation LoRA ;
- benchmark wav2vec/MMS ;
- diarisation.

Attention : certains prompts anciens contiennent des hypothèses ensuite corrigées. Exemple :
un changement de WER entre CPU INT8 et GPU float16 n'est pas forcément un bug.

### `PROMPTS_ANTIGRAVITY_AUDIT_SOUTENANCE.md`

Contient une méthode d'audit stricte avant soutenance :

- inventaire de l'état réel du dépôt ;
- séparation des sorties d'audit ;
- conformité au Topic 2 ;
- intégrité du dataset ;
- recalcul indépendant des résultats ;
- vérification des limites et contradictions.

C'est le meilleur modèle pour demander à une IA de contrôler le projet sans simplement le
confirmer.

### `AI_METHODOLOGY.md`

N'est pas un prompt, mais un journal de méthode :

- IA utilisée pour recherche, code, rédaction, vérification ;
- erreurs rejetées ;
- citations vérifiées ;
- résultats re-scorés ;
- bugs rencontrés ;
- limites et risques de l'assistance IA.

## Prompt réutilisable : reprendre le projet proprement

```text
Tu reprends le projet ThesisMasterTest pour le mémoire Topic 2 STT.
Avant toute modification, lis README.md, ETAT_ACTUEL.md, AI_METHODOLOGY.md,
MAINTENANCE_GUIDE.md, CHANGELOG.md et PROMPTS_JOURNAL.md.

Objectif : comprendre l'état réel du projet, pas confirmer une histoire favorable.
Ne modifie rien tant que tu n'as pas identifié :
- la version de mémoire de travail ;
- les CSV sources de vérité ;
- les scripts qui produisent les résultats ;
- les limites scientifiques principales ;
- les modifications Git déjà présentes.

Produis ensuite un court état des lieux avec :
1. ce qui est prouvé ;
2. ce qui est implémenté mais fragile ;
3. ce qui est hors périmètre ;
4. les commandes de vérification minimales.
```

## Prompt réutilisable : corriger sans casser les preuves

```text
Corrige le problème suivant dans ThesisMasterTest : [décrire le problème].

Contraintes :
- ne réécris pas les CSV canoniques sans sauvegarde et justification ;
- ne modifie pas les résultats historiques pour les faire correspondre à une conclusion ;
- garde les sorties d'erreur si elles expliquent un choix ;
- touche le minimum de fichiers ;
- ajoute ou lance un test proportionné ;
- à la fin, indique exactement les fichiers modifiés, les commandes lancées et les limites restantes.
```

## Prompt réutilisable : auditer un chiffre du mémoire

```text
Vérifie ce chiffre du mémoire : [coller le chiffre ou la phrase].

Méthode attendue :
1. retrouve le fichier LaTeX ou Markdown où il apparaît ;
2. retrouve le CSV ou rapport source ;
3. recalcule le chiffre avec le scorer ou la fonction appropriée ;
4. vérifie le périmètre : corpus, modèle, backend, condition, langue, bruit ;
5. indique si le chiffre est correct, arrondi, ambigu ou faux ;
6. propose une formulation défendable pour la soutenance.

Ne remplace pas un chiffre par une valeur plausible. Il doit venir des artefacts.
```

## Prompt réutilisable : préparer une réponse de soutenance

```text
Aide-moi à répondre en anglais à cette question de jury :
[question]

Contraintes :
- réponse courte, orale, niveau soutenance ;
- ne pas sur-vendre le système ;
- mentionner clairement les limites si nécessaire ;
- distinguer résultat mesuré, prototype implémenté et travail futur ;
- donne aussi une explication simple en français pour que je comprenne ce que je dis.
```

## Prompt réutilisable : ajouter une nouvelle expérience

```text
Je veux ajouter une nouvelle expérience à ThesisMasterTest : [objectif].

Avant de coder :
- dis si elle appartient à la campagne canonique ou à une validation externe ;
- propose un chemin de sortie isolé ;
- liste les variables à garder constantes ;
- liste les métriques et tests à produire ;
- explique le coût probable : temps, GPU, téléchargements, taille disque.

Ensuite seulement, propose les modifications minimales.
```

## Skills et méthodes qui ont servi

Les traces du projet montrent plusieurs méthodes utiles :

- `brainstorming` : clarifier l'objectif avant d'implémenter ;
- `impeccable` : concevoir et auditer l'interface `/research` ;
- `graphify` : explorer la structure du dépôt et ses relations ;
- vérification avant conclusion : ne pas déclarer "c'est bon" sans test ;
- debugging systématique : reproduire, isoler, corriger, re-tester ;
- review-driven work : montrer les diffs et les sorties avant d'avancer sur les parties
  risquées ;
- audit scientifique : distinguer preuve, hypothèse, limite et résultat attendu.

## Ce qu'il faut toujours noter après une session IA

```text
Date :
Objectif :
Prompt principal :
Outils / skills :
Fichiers lus :
Fichiers modifiés :
Commandes lancées :
Résultat :
Erreurs rencontrées :
Corrections appliquées :
Ce qui reste incertain :
Comment reproduire :
```

## Journal rapide de cette session

Date : 2026-09-22.

Objectif : transformer l'historique IA du projet en système maintenable.

Actions :

- inspection du dépôt, docs, état Git et graphify ;
- lecture de `README.md`, `AI_METHODOLOGY.md`, `CONTEXT.md`, `DESIGN.md`,
  `ETAT_ACTUEL.md`, prompts Antigravity et audit ;
- création de `MAINTENANCE_GUIDE.md`, `CHANGELOG.md`, `PROMPTS_JOURNAL.md` ;
- ajout de liens dans le README.

Limite : les prompts exacts qui n'ont jamais été sauvegardés dans le dépôt ou dans la
conversation ne peuvent pas être reconstruits mot pour mot. Ce journal capture ce qui est
présent dans les artefacts visibles.


## 2026-10-11 — Runs de test de l'étude réunions réelles

Exécution des runs de test de l'étude réunions réelles (Claude Code, développement piloté par
sous-agents) — prompts et décisions consignés dans
`.superpowers/sdd/2026-10-10-real-meetings-study-pipeline/progress.md`.
