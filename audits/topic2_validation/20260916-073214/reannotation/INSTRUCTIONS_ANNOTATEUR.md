# Instructions pour l'annotateur — transcription à l'aveugle de 24 extraits audio

Ce travail demande **des oreilles humaines**. Il ne doit pas être fait avec un logiciel de
transcription automatique, ni avec un assistant IA : le but est justement de vérifier ce que
ces logiciels produisent. Si vous n'êtes pas une personne qui écoute, ne faites pas cette tâche.

Durée estimée : 24 extraits de 4 à 24 secondes, environ **30 à 45 minutes** au total.

---

## 1. Ce que vous allez faire

Écouter 24 courts enregistrements téléphoniques (anglais, français, allemand) et écrire
**exactement ce que vous entendez**, mot pour mot, dans un tableau. C'est tout.

## 2. Ce que vous ne devez PAS faire

- Ne cherchez **aucun** texte existant pour ces fichiers (ni dans le dossier `references/`,
  ni dans les résultats, ni ailleurs). Vous devez écrire à l'aveugle.
- N'utilisez **aucun** outil de transcription automatique, de dictée, ni d'IA.
- Ne modifiez, ne renommez, ne déplacez **aucun** autre fichier que le tableau indiqué.
- Ne « corrigez » pas ce que dit la personne : si elle hésite, se répète ou fait une faute,
  écrivez-le tel quel.

## 3. Les fichiers

**Les enregistrements** (24 fichiers `.wav`, à ouvrir avec n'importe quel lecteur audio) :

    C:\Users\ulric\Documents\ThesisMasterTest\datasets\stt_eval\audio\

Seuls les fichiers dont le nom contient `_clean_` vous concernent (par exemple
`minds14_en_clean_01.wav`). Ignorez ceux qui contiennent `_noisy_`.

**Le tableau à remplir** (un seul fichier, à ouvrir avec Excel ou LibreOffice Calc) :

    C:\Users\ulric\Documents\ThesisMasterTest\audits\topic2_validation\20260916-073214\reannotation\07b_transcription_sheet_BLIND.csv

À l'ouverture, si le logiciel demande l'encodage, choisissez **UTF-8** et le séparateur **virgule**.

## 4. Les colonnes du tableau

| Colonne | Vous devez… |
|---|---|
| `order` | rien — c'est l'ordre dans lequel travailler (1 en premier) |
| `file` | rien — c'est le chemin du fichier audio à écouter |
| `language` | rien — `en` anglais, `fr` français, `de` allemand |
| `duration_s` | rien — durée en secondes |
| `priority` | rien — les 5 lignes marquées `PRIORITY` sont les plus importantes |
| `needs_other_person` | rien — si la case dit `YES (German)`, voir le point 6 |
| **`transcription_verbatim`** | **écrire ici** ce que vous entendez, mot pour mot |
| **`uncertain_passages`** | **écrire ici** les mots dont vous n'êtes pas sûr, chacun suivi d'un `?` |
| **`annotator`** | **votre prénom et nom** |
| **`date`** | **la date du jour**, format `2026-09-17` |
| `notes` | facultatif : bruit, coupure, deux voix, tout ce qui vous semble utile |

## 5. Comment procéder, ligne par ligne

1. Prenez la ligne `order` = 1. Ouvrez le fichier audio indiqué dans `file`.
2. Écoutez-le **en entier une première fois** sans rien écrire.
3. Réécoutez-le autant de fois que nécessaire et écrivez dans `transcription_verbatim` tout ce
   qui est dit, du premier au dernier mot, y compris :
   - les hésitations (« euh », « um », « hm ») ;
   - les répétitions et les faux départs (« je je voudrais ») ;
   - les formules de politesse en fin d'appel (« merci », « thank you ») ;
   - les chiffres **tels qu'ils sont prononcés** (« vingt-trois », pas « 23 »).
4. Si un mot ou un passage reste incertain après plusieurs écoutes, écrivez-le quand même dans
   la transcription, puis recopiez-le dans `uncertain_passages` avec un `?` (ex. : `compte joint?`).
   Si un passage est vraiment inaudible, écrivez `[inaudible]` dans la transcription.
5. Remplissez `annotator` et `date`.
6. Passez à la ligne suivante. Faites les lignes 1 à 5 (`PRIORITY`) en premier, puis toutes
   les autres dans l'ordre.

Majuscules, accents et ponctuation n'ont pas d'importance pour l'exploitation, mais écrivez
naturellement. Une seule ligne de texte par extrait, pas de retour à la ligne dans la cellule.

## 6. Les 8 extraits en allemand

Les lignes avec `needs_other_person` = `YES (German)` ne doivent être remplies que par une
personne qui **comprend l'allemand**. Si ce n'est pas votre cas, laissez ces 8 lignes vides et
signalez-le. Il vaut mieux une case vide qu'une transcription devinée.

## 7. Enregistrer et rendre

- Enregistrez le tableau **au même endroit, sous le même nom**, au format CSV, encodage UTF-8.
  (Excel : « Enregistrer sous » → type « CSV UTF-8 (délimité par des virgules) ».)
- Rendez ce seul fichier. Rien d'autre n'est attendu.
- Si vous avez un doute sur une consigne, notez-le dans `notes` plutôt que de deviner.

## 8. Facultatif mais précieux

Si une seconde personne peut réécouter les 5 lignes `PRIORITY` indépendamment (sans voir votre
version), ajoutez sa transcription dans `notes` quand elle diffère de la vôtre.
