# La méthode d'audit, en tant que système réutilisable

Ce document décrit *comment* les vérifications de ce projet ont été menées, indépendamment de
l'outil qui a aidé à les mener. C'est la partie transférable : les scripts sont spécifiques au
Topic 2, la méthode ne l'est pas.

À lire avant la soutenance : si un membre du jury demande « comment savez-vous que vos chiffres
sont justes ? », la réponse est dans ces sept règles, pas dans un logiciel.

---

## 1. Reproduire le défaut avant de le corriger

Un correctif dont on n'a pas vu l'échec initial ne prouve rien. Avant chaque correction, le défaut
a été reproduit avec des chiffres : « 32 000 octets en attente, 0 appel de transcription »,
« la langue envoyée par formulaire arrive à `None` », « 72 chemins partagés entre modèles ».
Les deux états sont conservés côte à côte (`01_repro_defects_BEFORE.json` / `_AFTER.json`).

**Règle** : pas de « c'est corrigé » sans un avant chiffré.

## 2. Ne jamais laisser un outil se valider lui-même

Le scorer WER du projet a été vérifié par une **réimplémentation indépendante** (autre algorithme,
autre fichier), pas en l'appelant. Les références de transcription n'ont **jamais** été produites
par un modèle ASR : ce serait mesurer un modèle contre un modèle. Trois architectures indépendantes
ont servi uniquement à *trier* quels fichiers écouter en priorité — jamais à trancher.

**Règle** : l'instrument de mesure et l'objet mesuré doivent avoir des origines différentes.

## 3. Séparer quatre niveaux de preuve

| Niveau | Signifie | Exemple dans ce projet |
|---|---|---|
| Implémenté | le code existe | pyannote est appelé dans `main.py` |
| Exécuté | une exécution observée | pyannote charge et rend deux étiquettes |
| Mesuré | une performance chiffrée contre une référence | WER 50,6 % sur 36 fichiers, IC [35,0 ; 65,4] |
| Validé en conditions réelles | dans l'environnement cible | *jamais atteint ici* |

La confusion entre ces niveaux est l'erreur la plus fréquente dans les rapports assistés par IA.
« La diarisation fonctionne » peut vouloir dire quatre choses très différentes.

**Règle** : chaque affirmation porte son niveau.

## 4. Un statut explicite par affirmation

Quatre statuts seulement : **vérifiée**, **contredite**, **partiellement vérifiée**, **non testée**
(+ **bloquée**, avec la raison). Chacun accompagné du chemin du fichier de preuve.

Le pouvoir de cette grille est qu'elle rend le « non testé » aussi visible que le « vérifié ».
Une exigence non satisfaite reste une limite affichée, jamais un silence.

**Règle** : pas de statut sans preuve ; pas de preuve sans chemin de fichier.

## 5. Ne jamais réécrire l'historique

Les CSV canoniques et les références d'origine n'ont pas été modifiés une seule fois. Chaque
révision vit dans un dossier daté, à côté, avec la valeur d'origine en regard. Le hash SHA-256 du
journal de latence a été contrôlé après chaque exécution.

Cela permet de dire au jury : « voici ce qui a été mesuré, voici ce qu'une révision donnerait, et
voici pourquoi je n'ai pas remplacé l'un par l'autre ».

**Règle** : on ajoute, on ne remplace pas.

## 6. Interpréter les intervalles honnêtement

Un intervalle de confiance qui contient zéro **n'établit ni l'absence d'effet ni l'équivalence**.
La formulation fidèle est : « aucun bénéfice établi sur cet échantillon, estimation +0,6 point,
intervalle [−1,9 ; +3,0] ».

Corollaire observé ici : l'estimation LoRA a bougé entre −0,5 et +1,0 selon la version des
références. Un effet plus petit que la sensibilité de la mesure n'est pas un effet.

**Règle** : dire l'estimation *et* l'intervalle, jamais un verdict binaire.

## 7. Un facteur à la fois, et le dire quand ce n'est pas le cas

Chaque comparaison doit nommer ce qui change. Quand deux choses changent en même temps, il faut
l'écrire : la comparaison tiny → large-v3 change **la taille et le backend** (CPU/INT8 →
GPU/float16), et la divergence inter-backend a été mesurée séparément (−1,1 et −3,5 points) pour
qu'on puisse juger de son poids.

**Règle** : un contraste sans inventaire des variables changées n'est pas une mesure.

---

## Ce que la méthode a produit ici

Sans lancer une seule expérience nouvelle, elle a fait apparaître :

- trois défauts logiciels qui auraient été démontrés en direct devant le jury ;
- sept références du corpus public qui diffèrent après réécoute, découvertes parce que trois
  modèles indépendants s'accordaient sur des mots absents du texte ;
- une salutation trilingue perdue par le chemin fichier, conservée par le chemin live — le
  mécanisme (une décision de langue sur les 30 premières secondes) identifié par un test de 40 s ;
- l'absence de borne sur la longueur d'un énoncé live (149 s observés), qui distingue le RTF du
  délai de sous-titrage ;
- une limite importante : des blocs entiers d'exigences du proposal non démontrés, désormais
  écrits comme tels plutôt que passés sous silence.

## La limite de la méthode

Elle ne remplace pas l'écoute humaine, la disponibilité de locuteurs, ni l'accès aux données de
l'entreprise. Elle dit précisément **où** se trouvent les trous ; elle ne les comble pas.

Trois choses sont restées hors de portée et le resteront sans intervention humaine : les références
allemandes, une réunion avec de vrais locuteurs annotés, et une intégration Teams.
