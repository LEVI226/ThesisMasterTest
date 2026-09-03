# Guide debutant A-Z pour comprendre et defendre le memoire STT

Auteur : OUEDRAOGO Yannick Ulrich Levi  
Memoire : *Advanced Speech-to-Text Models for Noisy, Multilingual Corporate Meetings*

Ce guide est fait pour toi si tu ne veux pas juste memoriser des phrases, mais vraiment comprendre ce que tu as fait. Il part de zero. Aucune notion n'est consideree comme deja acquise.

L'objectif final est simple : si un membre du jury te demande "pourquoi ?", "comment ?", "avec quoi ?", "qu'est-ce que ca veut dire ?", tu dois pouvoir reconstruire la reponse calmement.

---

## 1. Le probleme de depart

Dans une entreprise internationale comme Nestle, les reunions peuvent etre difficiles a suivre :

- plusieurs langues peuvent etre parlees : francais, anglais, allemand ;
- les personnes ont des accents differents ;
- il peut y avoir du bruit : ventilation, clavier, micro de mauvaise qualite, appel Teams ;
- certaines personnes parlent vite ;
- il y a parfois du vocabulaire interne : noms de marques, projets, personnes ;
- pour un employe malentendant, entendre la reunion peut etre tres difficile.

La solution naturelle est de transformer la parole en texte. C'est ce qu'on appelle :

- STT : Speech-to-Text ;
- ASR : Automatic Speech Recognition ;
- transcription automatique.

Ton memoire etudie donc cette question :

> Est-ce qu'un systeme de transcription automatique open-source peut produire des transcriptions utiles dans des conditions difficiles : bruit, multilinguisme, vocabulaire metier et besoin de temps reel ?

Important : ton memoire ne dit pas "j'ai resolu tout le probleme". Il dit :

> J'ai construit un pipeline, je l'ai teste proprement, j'ai mesure ce qui marche et ce qui ne marche pas.

---

## 2. Ce qu'est l'intelligence artificielle dans ton memoire

L'intelligence artificielle, ici, ce n'est pas un robot qui pense. C'est un ensemble de modeles statistiques entraines sur beaucoup de donnees pour reconnaitre des formes.

Dans ton cas, le modele recoit un signal audio et doit produire du texte.

Exemple :

```text
Audio : une personne dit "bonjour je voudrais changer d'adresse"
Modele ASR -> Texte : "bonjour je voudrais changer d'adresse"
```

Mais l'audio n'est pas directement du texte. C'est une onde sonore. Le modele doit apprendre des correspondances :

```text
forme sonore -> sons -> syllabes -> mots -> phrase
```

Quand l'audio est propre, c'est plus facile.  
Quand il y a du bruit, des accents ou plusieurs langues, c'est plus difficile.

---

## 3. Ce qu'est un modele ASR

Un modele ASR est un modele qui transforme la parole en texte.

Il existe plusieurs familles :

### 3.1 Les anciens systemes

Avant, les systemes etaient composes de plusieurs blocs separes :

```text
audio -> extraction de caracteristiques -> modele acoustique -> dictionnaire -> modele de langue -> texte
```

Ces systemes utilisaient souvent :

- GMM-HMM ;
- DNN-HMM.

Tu n'as pas besoin d'entrer dans les equations. Il faut juste savoir dire :

> Les anciens systemes decomposaient la reconnaissance en plusieurs etapes separees. Les modeles modernes apprennent davantage de bout en bout.

### 3.2 Les modeles modernes

Aujourd'hui, les modeles apprennent directement avec des reseaux de neurones.

Dans ton memoire, les familles importantes sont :

| Famille | Idee simple | Exemple dans ton travail |
|---|---|---|
| Encoder-decoder | lit l'audio puis genere du texte progressivement | Whisper |
| CTC | aligne rapidement audio et caracteres/mots | MMS, Conformer |
| Self-supervised | apprend d'abord sur beaucoup d'audio non annote | wav2vec 2.0 / MMS |

---

## 4. Ce qu'est Whisper

Whisper est un modele d'OpenAI pour reconnaitre la parole.

Il a ete entraine sur enormement d'audio multilingue. Il sait faire plusieurs choses :

- transcrire ;
- traduire ;
- detecter la langue ;
- produire des segments temporels.

Dans ton memoire, tu utilises Whisper via `faster-whisper`.

### 4.1 Pourquoi Whisper est interessant

Whisper est interessant parce qu'il est :

- multilingue ;
- robuste a plusieurs accents ;
- disponible publiquement ;
- capable de gerer francais, anglais, allemand ;
- pratique pour faire un prototype local.

### 4.2 Pourquoi Whisper n'est pas magique

Whisper peut echouer :

- sur du bruit fort ;
- sur des clips tres courts ;
- sur des termes rares ;
- sur du changement de langue ;
- sur des audios ambigus ;
- en produisant des hallucinations.

Une hallucination, dans ce contexte, signifie :

> Le modele produit un texte plausible, mais qui n'a pas ete prononce.

Exemple dans ton travail : le prompt contenait "Nestle Ghana", et le modele a insere "Nestle Ghana" dans une transcription alors que ce n'etait pas dans l'audio.

---

## 5. Ce qu'est faster-whisper

Whisper original peut etre lourd a executer. `faster-whisper` est une implementation optimisee qui utilise CTranslate2.

Pourquoi c'est utile :

- ca va plus vite ;
- ca consomme moins de memoire ;
- ca permet d'utiliser INT8 sur CPU ;
- c'est pratique pour un pipeline local.

Dans ton code :

```text
backend/stt/engine.py
  -> load_model()
  -> WhisperModel(...)
```

La fonction `load_model()` charge le modele Whisper une seule fois et le garde en memoire. C'est important car charger un modele a chaque requete serait lent.

---

## 6. CPU, GPU, INT8, float16 : explication simple

### CPU

Le CPU est le processeur classique de l'ordinateur. Il peut tout faire, mais il n'est pas specialise pour les gros calculs de reseaux de neurones.

### GPU

Le GPU est la carte graphique. Il est tres fort pour faire beaucoup de calculs en parallele. Les modeles IA tournent souvent beaucoup plus vite dessus.

### INT8

INT8 signifie que les nombres du modele sont stockes sur 8 bits.

Avantage :

- moins de memoire ;
- plus rapide sur CPU.

Inconvenient :

- petite perte possible de precision.

### float16

float16 signifie nombres flottants sur 16 bits.

Avantage :

- tres efficace sur GPU ;
- plus leger que float32.

Dans ta these :

- CPU : souvent INT8 ;
- GPU : souvent float16.

Piege important :

> Il ne faut pas comparer n'importe comment des resultats CPU INT8 et GPU float16, car le backend et la precision changent.

---

## 7. Le pipeline complet en mots simples

Un pipeline, c'est une chaine d'etapes.

Ton pipeline STT fait ceci :

```text
audio
  -> preprocessing optionnel
  -> modele Whisper
  -> texte
  -> metriques d'evaluation
  -> stockage des resultats
```

Dans l'application :

```text
utilisateur envoie audio
  -> FastAPI recoit le fichier
  -> le fichier est sauvegarde
  -> transcribe_file() lance Whisper
  -> le texte est produit
  -> le texte est stocke dans ChromaDB pour pouvoir poser des questions dessus
```

---

## 8. Le code principal explique simplement

### 8.1 `backend/stt/engine.py`

C'est le coeur du moteur STT.

Il contient :

- le prompt metier Nestle ;
- la configuration de transcription ;
- le chargement du modele ;
- le preprocessing audio ;
- la transcription ;
- la diarization si disponible.

#### `TranscribeConfig`

C'est une fiche de configuration.

Elle dit au systeme :

```text
Quel modele utiliser ?
Quelle langue ?
Faut-il reduire le bruit ?
Faut-il utiliser le prompt Nestle ?
Faut-il utiliser VAD ?
Faut-il produire les timestamps ?
```

En gros :

> Au lieu de mettre des options partout dans le code, tu les regroupes dans un seul objet.

#### `load_model()`

Cette fonction charge le modele.

Elle choisit :

- `cuda` si GPU disponible ;
- sinon `cpu` ;
- `float16` sur GPU ;
- `int8` sur CPU.

Elle garde le modele en cache.

Phrase a dire :

> `load_model()` evite de recharger Whisper a chaque requete et choisit automatiquement le bon backend selon le materiel.

#### `preprocess_audio()`

Cette fonction :

1. lit l'audio ;
2. le convertit en mono 16 kHz ;
3. applique une reduction de bruit avec `noisereduce` ;
4. sauvegarde un fichier nettoye temporaire.

Pourquoi 16 kHz ?

> Beaucoup de modeles de parole, dont Whisper, attendent un audio standardise a 16 kHz.

#### `transcribe_file()`

C'est la fonction la plus importante.

Elle fait :

```text
1. recevoir le chemin audio
2. charger la configuration
3. charger le modele
4. appliquer ou non le preprocessing
5. preparer les options Whisper
6. lancer model.transcribe()
7. recuperer les segments
8. concatener le texte complet
9. mesurer le temps de traitement
10. calculer la duree audio
11. appliquer la diarization si possible
12. retourner un dictionnaire de resultats
```

Phrase a dire :

> Toutes mes conditions experimentales correspondent a des variations controlees des options donnees a `transcribe_file()`.

### 8.2 `backend/main.py`

C'est le serveur web.

Il utilise FastAPI.

FastAPI permet de creer des endpoints, c'est-a-dire des routes que le frontend ou un client peut appeler.

Endpoints importants :

| Endpoint | Ce qu'il fait |
|---|---|
| `/transcribe` | transcrit un fichier audio |
| `/ws/transcribe` | transcrit en mode live avec WebSocket |
| `/ocr` | extrait du texte depuis image/PDF |
| `/ask` | pose une question sur les documents/transcripts |
| `/health` | verifie l'etat du systeme |

Ton sujet est surtout `/transcribe` et `/ws/transcribe`.

#### `/transcribe`

Etapes :

```text
1. recoit un fichier
2. verifie son extension
3. sauvegarde le fichier
4. appelle transcribe_file()
5. stocke le texte dans ChromaDB
6. renvoie le resultat
```

Pourquoi `run_in_executor` ?

FastAPI fonctionne en asynchrone. Mais Whisper est une operation lourde et bloquante.

Si on lance Whisper directement, le serveur peut se bloquer.

`run_in_executor` permet de dire :

> Lance cette grosse operation dans un autre thread pour ne pas bloquer le serveur.

#### `/ws/transcribe`

WebSocket = connexion continue entre navigateur et serveur.

Au lieu d'envoyer un fichier complet, le navigateur envoie des petits morceaux audio.

Le serveur :

```text
1. recoit des chunks audio
2. utilise VAD pour detecter la parole
3. accumule l'audio tant que la personne parle
4. attend 0.6 seconde de silence
5. transcrit le bloc audio
6. renvoie le texte au navigateur
```

Important :

> Ce n'est pas du vrai streaming ASR frame par frame. C'est un compromis : VAD segmente, puis Whisper transcrit chaque segment.

### 8.3 `backend/evaluation/metrics.py`

C'est le fichier qui calcule les metriques.

#### WER

WER = Word Error Rate.

Il mesure l'erreur au niveau des mots.

Formule :

```text
WER = (substitutions + suppressions + insertions) / nombre de mots dans la reference
```

Exemple :

Reference :

```text
the meeting starts at nine
```

Hypothese :

```text
the meeting start at nine a m
```

Erreurs :

- `starts` devient `start` : substitution ;
- `a` et `m` sont ajoutes : insertions.

Donc le WER augmente.

Important :

> Le WER peut depasser 100 % si le modele ajoute beaucoup de mots.

#### CER

CER = Character Error Rate.

Meme logique que WER, mais au niveau des caracteres.

Pourquoi c'est utile ?

> En francais ou allemand, un mot peut etre legerement mal orthographie mais rester proche. Le CER montre une erreur plus fine que le WER.

#### RTF

RTF = Real-Time Factor.

Formule :

```text
RTF = temps de traitement / duree de l'audio
```

Exemples :

- audio de 10 secondes, traitement en 5 secondes : RTF = 0.5, plus rapide que le temps reel ;
- audio de 10 secondes, traitement en 20 secondes : RTF = 2.0, plus lent que le temps reel.

Phrase a dire :

> RTF inferieur a 1 signifie que le systeme transcrit plus vite que la duree de l'audio.

### 8.4 `backend/evaluation/runner.py`

C'est le fichier qui transforme ton pipeline en experience scientifique.

Il fait :

```text
pour chaque audio
  pour chaque condition experimentale
    transcrire
    comparer a la reference
    calculer WER/CER/RTF
    ecrire dans CSV
```

Pourquoi c'est important ?

> Sans ce runner, tu as juste une application. Avec ce runner, tu as une evaluation reproductible.

---

## 9. Les donnees : comprendre le dataset

Tu n'avais pas acces a de vraies reunions Nestle, pour des raisons evidentes :

- confidentialite ;
- RGPD / protection des donnees ;
- donnees internes ;
- temps limite du master.

Tu as donc utilise un dataset public : MInDS-14.

MInDS-14 contient :

- vraie parole ;
- plusieurs langues ;
- domaine bancaire ;
- audio telephonique ;
- transcriptions de reference.

Ton dataset canonique :

```text
36 clips
  = 24 propres
  + 12 bruites

3 langues
  = anglais
  + francais
  + allemand
```

Les clips bruites sont crees en ajoutant du bruit blanc a 8 dB SNR.

### C'est quoi SNR ?

SNR = Signal-to-Noise Ratio.

Ca veut dire :

> rapport entre le signal utile, la voix, et le bruit.

Si le SNR est eleve, la voix domine le bruit.  
Si le SNR est faible, le bruit gene beaucoup.

8 dB est une condition difficile.

---

## 10. Les conditions experimentales

Une condition experimentale est une configuration du pipeline.

Exemple :

```text
modele tiny
pas de preprocessing
pas de prompt
langue automatique
```

Puis tu changes une seule chose a la fois.

### Conditions principales

| Condition | Idee | Ce qu'on teste |
|---|---|---|
| A | baseline | point de depart |
| B | + noise reduction | effet du nettoyage audio |
| C | + VAD | effet de la detection parole/silence |
| D | + prompt Nestle | effet du vocabulaire metier |
| E | + langue forcee | effet de ne pas laisser Whisper deviner la langue |
| F-I | model-size ladder | effet de la taille du modele |
| J | LoRA | effet d'un fine-tuning leger |
| K | MMS | comparaison wav2vec 2.0 / CTC |
| L | Conformer | comparaison autre architecture CTC |

Pourquoi cette structure est bonne ?

> Parce qu'elle permet d'attribuer les differences a des causes precises.

Exemple :

Si A et B different seulement par `noisereduce`, alors la difference de WER entre A et B vient du preprocessing.

---

## 11. Les resultats expliques en langage simple

### 11.1 Le bruit casse fortement la transcription

Baseline :

```text
audio propre : 47.0 % WER
audio bruite : 96.4 % WER
```

Interpretation :

> Le bruit double presque l'erreur. C'est le facteur le plus violent.

### 11.2 Nettoyer le bruit aide, mais pas toujours

Sur audio bruite :

```text
96.4 % -> 88.1 %
```

Donc ca aide.

Sur audio propre :

```text
47.0 % -> 49.2 %
```

Donc ca degrade legerement.

Conclusion :

> La reduction de bruit est utile dans une salle bruyante, mais peut abimer un audio deja propre.

### 11.3 Forcer la langue aide beaucoup en pratique

Whisper peut deviner la langue.

Mais sur des clips courts ou bruites, il peut se tromper.

Dans ton cas, le francais est fragile :

```text
42 % des clips francais different entre auto-detection et langue forcee
```

Parfois, Whisper sort du texte dans un mauvais alphabet.

Conclusion :

> Si l'organisation sait que la reunion est en francais, anglais ou allemand, forcer la langue est une amelioration simple et gratuite.

### 11.4 Les grands modeles reconnaissent mieux

La taille du modele a le plus gros effet sur la precision.

```text
tiny    : 63.4 % WER
base    : 48.3 %
small   : 33.3 %
medium  : 25.9 %
large-v3: 24.6 %
```

Interpretation :

> Plus le modele est grand, mieux il transcrit, mais le gain devient plus petit apres medium.

### 11.5 Prompting et LoRA ne changent presque pas le resultat ici

Prompting :

> On donne a Whisper une liste de mots attendus : Nestle, Nespresso, Maggi, etc.

Probleme :

> Le dataset ne contient pas vraiment ces mots. Donc on ne peut pas mesurer si le prompt aide sur les mots Nestle.

Ce que tu as mesure :

- effet moyen tres faible ;
- risque de hallucination du prompt.

LoRA :

> On fine-tune legerement le modele en modifiant seulement une petite partie des poids.

Resultat :

- environ 1 point de WER ;
- non significatif ;
- pas une preuve que LoRA ne marche pas ;
- plutot une preuve que ce dataset ne cree pas assez d'ecart de domaine.

---

## 12. Comprendre LoRA simplement

Un grand modele contient beaucoup de parametres. Fine-tuner tout le modele coute cher.

LoRA dit :

> Au lieu de modifier tout le modele, on ajoute de petites matrices entrainables et on garde le modele principal presque fixe.

Image mentale :

```text
Modele Whisper gelé
  + petit adaptateur LoRA
  = modele adapte legerement
```

Dans ton travail :

- modele : whisper-small ;
- 300 clips d'entrainement ;
- 100 par langue ;
- verification anti-contamination ;
- LoRA rank 16 ;
- environ 1.77M parametres entraines ;
- seulement 0.73 % du modele ;
- evaluation appariee.

Evaluation appariee signifie :

> On compare le modele vanilla et le modele LoRA sur exactement les memes clips, avec le meme scoreur, pour que la comparaison soit juste.

---

## 13. Comprendre MMS et Conformer

### MMS

MMS vient de Meta et appartient a la famille wav2vec 2.0.

Il est base sur CTC.

Il est rapide.

Mais dans ton evaluation :

> La langue est donnee par construction.

Donc il ne faut pas dire :

> MMS bat ou ne bat pas Whisper de maniere absolue.

Il faut dire :

> MMS est une alternative rapide si la langue est connue.

### Conformer

Conformer combine :

- attention : comprendre les relations globales ;
- convolution : capter les motifs locaux du signal audio.

Dans ton travail, Conformer est tres rapide et performant, mais :

- checkpoints monolingues ;
- langue donnee ;
- comparaison avec Whisper-auto confondee.

Phrase a dire :

> Conformer est tres fort dans un cadre langue connue, mais Whisper reste plus pratique pour un contexte multilingue general avec detection native, ponctuation et timestamps.

---

## 14. Comprendre la diarization

Diarization veut dire :

> savoir qui parle quand.

Exemple :

```text
SPEAKER_1: Bonjour
SPEAKER_2: Oui, je suis d'accord
```

Ton systeme utilise pyannote.

Probleme :

> Ton dataset principal est mono-locuteur, donc il ne permet pas de bien evaluer la diarization.

Tu as donc cree des reunions simulees en concatenant des clips.

Le DER moyen est 0.585.

DER = Diarization Error Rate.

Mais attention :

> Ce chiffre est difficile a interpreter parce que le testbed est artificiel.

Pourquoi ?

- les pauses internes peuvent etre comptees comme parole dans la reference ;
- les clips viennent de vrais locuteurs differents ;
- l'etiquette simulee peut simplifier une realite plus complexe ;
- les reunions bruitees semblent parfois avoir un meilleur DER, ce qui montre que la mesure est instable.

Conclusion :

> La diarization fonctionne mecaniquement, mais une vraie evaluation demanderait de vraies reunions multi-locuteurs annotees.

---

## 15. Comprendre RAG, OCR et pourquoi ce n'est pas ton coeur

La plateforme globale a trois topics :

1. OCR : lire les documents scannes ;
2. STT : transcrire la parole ;
3. RAG/personnalisation : poser des questions sur les contenus.

Ton sujet est Topic 2 : STT.

Mais ton STT alimente le RAG :

```text
transcription
  -> decoupage en chunks
  -> embeddings
  -> ChromaDB
  -> question utilisateur
  -> reponse avec LLM local
```

ChromaDB :

> retrouve les passages pertinents.

Ollama / LLM :

> genere une reponse a partir des passages retrouves.

Piege :

> Le RAG n'a pas ete evalue pour precision/relevance dans ton memoire. Il existe comme integration plateforme, mais l'evaluation centrale est STT.

---

## 16. Comprendre les limites

Une limite n'est pas une honte. En recherche, une limite bien formulee montre que tu sais exactement ce que tes resultats veulent dire.

### Limite 1 : pas de vraies donnees Nestle

Pourquoi ?

- confidentialite ;
- donnees personnelles ;
- acces impossible pendant le master.

Consequence :

> Tu ne peux pas prouver que le systeme marche sur toutes les reunions Nestle.

Mais tu peux dire :

> J'ai mesure des facteurs pertinents avec un proxy public : bruit, multilinguisme, parole spontanee.

### Limite 2 : bruit synthetique

Tu as ajoute du bruit blanc.

Ce n'est pas pareil que :

- brouhaha ;
- reverberation ;
- micro Teams ;
- plusieurs personnes qui parlent.

Mais avantage :

> C'est controle et reproductible.

### Limite 3 : dataset petit

36 clips, c'est petit.

Mais :

- toutes les conditions utilisent les memes clips ;
- les resultats sont traceables ;
- les gros effets sont robustes ;
- les petits effets sont presentes comme non significatifs.

### Limite 4 : systeme pas production-ready

Il manque :

- authentification ;
- controle d'acces par utilisateur ;
- securite ;
- gouvernance ;
- vraie integration Teams/Azure ;
- evaluation sur vraies reunions.

Phrase :

> C'est un pilote experimental local, pas un produit final deployable.

---

## 17. Comment apprendre le memoire de A a Z

### Etape 1 : comprendre le besoin

Question :

> Pourquoi fait-on ce travail ?

Reponse :

> Pour aider l'accessibilite en reunion, surtout pour les personnes malentendantes.

### Etape 2 : comprendre la difficulte

Question :

> Pourquoi ce n'est pas trivial ?

Reponse :

> Parce que l'audio reel est bruite, multilingue, avec accents et vocabulaire metier.

### Etape 3 : comprendre l'outil

Question :

> Quel modele utilise-t-on ?

Reponse :

> Whisper via faster-whisper, parce qu'il est multilingue, open-source utilisable localement, et efficace avec CTranslate2.

### Etape 4 : comprendre l'experience

Question :

> Comment sait-on si ca marche ?

Reponse :

> On compare la transcription produite avec une reference humaine, puis on calcule WER, CER et RTF.

### Etape 5 : comprendre les resultats

Question :

> Qu'a-t-on appris ?

Reponse :

> Le bruit degrade fortement, la taille du modele aide beaucoup, forcer la langue aide qualitativement, prompting/LoRA ont peu d'effet sur ce dataset.

### Etape 6 : comprendre les limites

Question :

> Qu'est-ce qu'on ne peut pas conclure ?

Reponse :

> On ne peut pas affirmer une performance finale sur vraies reunions Nestle, ni le benefice du prompt sur vocabulaire Nestle reel.

---

## 18. Methode de memorisation ultra simple

Chaque jour, recite cette chaine :

```text
Besoin -> Difficultes -> Pipeline -> Dataset -> Conditions -> Metriques -> Resultats -> Limites -> Perspectives
```

Developpe ensuite chaque mot :

### Besoin

Accessibilite pour employes malentendants.

### Difficultes

Bruit, langues, accents, vocabulaire, multi-speakers.

### Pipeline

FastAPI + faster-whisper + preprocessing + RAG.

### Dataset

MInDS-14, 36 clips, EN/FR/DE, propre/bruite.

### Conditions

Baseline, noisereduce, VAD, prompt, langue forcee, tailles, LoRA, MMS, Conformer.

### Metriques

WER, CER, RTF, DER pour diarization.

### Resultats

Bruit domine, taille domine, langue forcee utile, adaptation faible ici.

### Limites

Pas de vraie reunion Nestle, bruit synthetique, petit dataset, pas production.

### Perspectives

Vraies donnees, fine-tuning domaine, integration securisee, Teams/Azure.

---

## 19. Les reponses "niveau debutant mais intelligent"

### Si on demande : "Expliquez WER simplement"

> Le WER mesure combien de mots il faut corriger pour transformer la transcription produite par le modele en reference correcte. On compte les mots remplaces, supprimes ou ajoutes, puis on divise par le nombre de mots de la reference.

### Si on demande : "Expliquez Whisper simplement"

> Whisper est un modele de reconnaissance vocale. Il prend un signal audio, l'encode sous forme de representations internes, puis genere progressivement le texte correspondant. Comme il genere du texte, il peut aussi halluciner si l'audio est ambigu.

### Si on demande : "Expliquez le role du preprocessing"

> Le preprocessing essaie d'ameliorer l'audio avant transcription. Dans mon cas, `noisereduce` attenue certaines frequences associees au bruit. Mais cela peut aussi supprimer des indices utiles dans un audio propre.

### Si on demande : "Expliquez le role du prompt"

> Le prompt donne au decodeur une liste de mots attendus. L'idee est d'augmenter la probabilite de termes rares comme des marques. Mais si l'audio est ambigu ou si le dataset ne contient pas ces mots, le prompt peut aussi pousser le modele a halluciner.

### Si on demande : "Expliquez LoRA simplement"

> LoRA est une methode de fine-tuning leger. Au lieu de re-entrainer tout le modele, on ajoute de petites matrices entrainables. Cela permet d'adapter un grand modele avec beaucoup moins de parametres et moins de calcul.

### Si on demande : "Expliquez pourquoi vous avez fait MMS et Conformer"

> Pour comparer Whisper a d'autres familles d'architectures ASR. MMS represente wav2vec 2.0/CTC, et Conformer represente une architecture attention-convolution performante. Mais la comparaison est caveatee car ces modeles recoivent la langue par construction.

---

## 20. Ton script oral complet en francais

> Mon memoire porte sur la transcription automatique de reunions multilingues et bruitees dans un contexte d'accessibilite. Le point de depart est humain : pour un employe malentendant, une transcription fiable peut etre le principal moyen d'acceder au contenu d'une reunion.
>
> Techniquement, ce probleme est difficile parce que les reunions d'entreprise combinent plusieurs facteurs : bruit, accents, alternance de langues, vocabulaire specifique et parfois plusieurs locuteurs. Les benchmarks classiques d'ASR ne representent pas toujours ces conditions.
>
> J'ai donc construit et evalue un pipeline local base sur faster-whisper. Le pipeline permet d'activer ou non la reduction de bruit, le prompt de vocabulaire metier, la langue forcee et le VAD. J'ai ensuite mesure les performances avec WER, CER et RTF sur un dataset public trilingue, MInDS-14, compose de 36 clips propres et bruites.
>
> Les resultats montrent d'abord que le bruit est le facteur dominant : le WER passe de 47.0 % sur audio propre a 96.4 % sur audio bruite en baseline. La reduction de bruit aide sur le bruite mais degrade legerement le propre. La langue forcee est le resultat le plus directement actionnable, car elle corrige des erreurs de detection automatique, notamment en francais. La taille du modele est le plus grand levier de precision : le WER descend de 63.4 % avec tiny a 24.6 % avec large-v3. En revanche, le prompting et LoRA ne deplacent le WER que d'environ un point sur ce dataset.
>
> La limite principale est que MInDS-14 n'est pas une vraie reunion Nestle. C'est un proxy public, choisi pour des raisons de confidentialite et de reproductibilite. Donc mon travail ne pretend pas prouver un deploiement final chez Nestle ; il fournit une evaluation controlee, traceable, et une hierarchie claire des leviers a tester ensuite sur de vraies donnees autorisees.

---

## 21. La carte finale a apprendre par coeur

```text
Pourquoi ?
  Accessibilite des employes malentendants.

Probleme ?
  Bruit + langues + accents + vocabulaire metier.

Solution testee ?
  Pipeline local faster-whisper.

Comment mesurer ?
  MInDS-14, 36 clips, WER/CER/RTF, 468 runs.

Qu'est-ce qu'on apprend ?
  Bruit domine.
  Taille modele domine la precision.
  Langue forcee est tres actionnable.
  Prompting/LoRA faibles ici.

Quelles limites ?
  Pas de vraie reunion Nestle.
  Bruit synthetique.
  Petit dataset.
  Pas production-ready.

Et apres ?
  Donnees Nestle autorisees.
  Fine-tuning domaine.
  Vraies reunions multi-speakers.
  Securite et integration.
```

---

## 22. Dernier conseil de defense

Tu n'as pas besoin de paraitre comme quelqu'un qui sait tout en IA. Tu dois paraitre comme quelqu'un qui comprend son propre travail.

La phrase qui te sauve toujours :

> Dans le cadre de mon memoire, je n'ai pas mesure cela directement. Ce que mes resultats permettent de dire, c'est ceci ; pour aller plus loin, il faudrait telle experience.

C'est une reponse scientifique. Et c'est exactement ce qu'un jury respecte.
