# Guide complet de defense du memoire Topic 2 STT

Auteur : OUEDRAOGO Yannick Ulrich Levi  
Memoire : *Advanced Speech-to-Text Models for Noisy, Multilingual Corporate Meetings: Evaluation of a Whisper-Based Pipeline for Workplace Accessibility*

Ce document est ton manuel d'appropriation. Son objectif n'est pas seulement de te faire memoriser des phrases, mais de faire entrer la logique du memoire dans ta tete : pourquoi le sujet existe, ce que tu as construit, comment tu as mesure, ce que les resultats prouvent, ce qu'ils ne prouvent pas, et comment repondre au jury sans paniquer.

---

## 1. La these en une phrase

J'ai evalue, de facon controlee et reproductible, un pipeline local de transcription automatique base sur Whisper/faster-whisper pour des conditions difficiles proches de reunions d'entreprise multilingues : bruit, changement de langue, vocabulaire metier, contrainte de temps reel et accessibilite pour employes malentendants.

Phrase encore plus courte a dire a l'oral :

> Mon travail ne pretend pas construire un produit final magique ; il mesure honnetement ce qu'un pipeline STT open-source peut faire, ce qui le degrade, et quels leviers sont vraiment utiles.

---

## 2. Le fil rouge a garder dans ton cerveau

Tu dois toujours ramener la soutenance a cette chaine :

1. Probleme humain : pour une personne malentendante, le transcript est l'acces a la reunion.
2. Probleme technique : les reunions d'entreprise sont difficiles pour l'ASR car il y a bruit, multilinguisme, accents, vocabulaire metier et parfois plusieurs locuteurs.
3. Probleme scientifique : les benchmarks publics propres et monolingues ne disent pas ce qui se passe dans ce contexte.
4. Ta contribution : tu as construit un pipeline local, un protocole controle, puis mesure WER, CER et RTF.
5. Resultat principal : le bruit domine, la taille du modele aide le plus, forcer la langue est le gain le plus actionnable, le prompting et LoRA donnent environ 1 point seulement sur ce dataset.
6. Limite principale : le dataset est un proxy public, pas de vraies reunions Nestle, donc certaines conclusions sont directionnelles et non definitives.
7. Position mature : tu assumes les limites au lieu de les cacher.

Si tu perds le fil pendant une question, reviens a cette phrase :

> La logique du memoire est de remplacer les hypotheses generales sur l'ASR par des mesures traceables sur un pipeline fixe.

---

## 3. Les cinq chiffres que tu dois connaitre par coeur

Ces chiffres sont tes ancres. Tu dois pouvoir les sortir sans chercher.

| Idee | Chiffre a retenir | Interpretation |
|---|---:|---|
| Taille du dataset canonique | 36 clips | 24 propres + 12 bruites, EN/FR/DE |
| Campagne totale | 468 transcriptions | 180 CPU + 288 GPU/extensions |
| Effet du bruit baseline | 61.1 % -> 96.4 % WER, sur 12 paires | +35.3 points ; IC 95 % [7.0, 60.0] |
| Echelle Whisper | 63.4 % -> 24.6 % WER | de tiny a large-v3 |
| LoRA / prompting | environ 1 point | effet faible, non comparable a la taille du modele |

Ajoute aussi ces trois chiffres de defense :

| Idee | Chiffre |
|---|---:|
| Detection automatique FR en echec | 42 % des clips francais |
| RTF CPU sous 1 | 93.9 % des 180 runs CPU |
| Latence live historique, 20 observations hors premiers enonces | mediane 0.56 s, p95 0.84 s, maximum 1.18 s |

Attention : le journal contient maintenant 38 observations. Les 35 hors premiers enonces donnent une mediane de 0.575 s, un p95 de 1.614 s et un maximum de 11.021 s. Les configurations des sessions ne sont pas consignees. Voir `results/topic2_readiness_audit.md` et `COMPLEMENTS_TOPIC2.md` ; ne pas presenter le resultat historique comme une garantie actuelle.

---

## 4. Les resultats en mode defense

### 4.1 Resultat 1 : le bruit domine

Ce que tu dis :

> Sur les 12 memes enonces avant et apres ajout de bruit, le WER passe de 61.1 % a 96.4 %, soit +35.3 points. C'est un effet important, avec une incertitude large. Le contraste 47.0 % contre 96.4 % utilise des ensembles differents et ne mesure pas a lui seul l'effet du bruit.

Ce que ca veut dire :

- Le modele n'est pas "casse".
- Le dataset MInDS-14 est deja difficile : parole telephonique 8 kHz, spontanee.
- Le bruit blanc a 8 dB rend la transcription tres dure.
- C'est exactement pourquoi il faut mesurer au lieu de citer seulement les benchmarks Whisper.

Piege :

> "Mais 96 % de WER, c'est inutilisable non ?"

Reponse :

> Oui, sur les clips bruites avec tiny, la qualite absolue est mauvaise. C'est un resultat important, pas un echec cache. Il montre que le petit modele en conditions bruitees ne suffit pas, et il justifie les tests de taille de modele, langue forcee et preprocessing.

### 4.2 Resultat 2 : la reduction de bruit est un compromis

Ce que tu dis :

> La reduction de bruit aide sur l'audio bruite, mais elle coute un peu sur l'audio propre. Elle recupere environ 8.3 points de WER sur les clips bruites, mais degrade legerement les clips propres.

Interpretation :

- `noisereduce` fait du spectral gating.
- Il attenue certaines frequences supposees etre du bruit.
- Sur du bruit, ca peut aider.
- Sur du propre, ca peut aussi supprimer de petites informations utiles a la reconnaissance.

Phrase de defense :

> Aucun interrupteur de preprocessing ne doit etre active aveuglement ; il faut l'adapter a la qualite acoustique de la salle.

### 4.3 Resultat 3 : forcer la langue est le gain le plus actionnable

Ce que tu dis :

> La detection automatique de langue echoue fortement sur les clips francais courts et bruites. Elle produit parfois des sorties dans le mauvais alphabet. Forcer `language="fr"` recupere un texte francais lisible a cout computationnel nul.

Important :

- Le WER global ne bouge pas toujours enormement.
- Mais le gain qualitatif est majeur : pour un humain, un francais imparfait est plus exploitable qu'un texte en cyrillique ou en hebreu.

Piege :

> "Si c'est si utile, pourquoi le WER ne chute pas massivement ?"

Reponse :

> Parce que le WER est une distance mot a mot. Un texte en mauvais alphabet et un texte francais encore imparfait restent tous les deux loin de la reference. Le WER capte mal la lisibilite humaine dans ce cas ; c'est pourquoi le memoire rapporte aussi des exemples qualitatifs.

### 4.4 Resultat 4 : la taille du modele est le plus gros levier de precision

Table a connaitre :

| Modele | WER moyen | WER bruite |
|---|---:|---:|
| tiny | 62.2 % | 88.1 % |
| base | 48.3 % | 79.2 % |
| small | 33.3 % | 56.7 % |
| medium | 25.9 % | 43.3 % |
| large-v3 | 24.6 % | 40.7 % |

Ce que tu dis :

> La courbe est monotone : plus le modele est grand, plus le WER baisse. Mais les rendements diminuent apres medium, donc small ou medium sont probablement les meilleurs compromis selon le materiel disponible.

Piege :

> "Pourquoi small est presque aussi rapide que tiny sur GPU ?"

Reponse :

> Le RTF ne depend pas seulement du nombre de parametres. Il depend aussi de la longueur de sortie et du comportement du decodeur. Un petit modele peut halluciner ou prolonger des hypotheses sur audio difficile, ce qui augmente le temps de decodage.

### 4.5 Resultat 5 : prompting et LoRA ont un effet faible ici

Ce que tu dis :

> Les deux strategies d'adaptation a bas cout, prompting et LoRA, donnent environ 1 point de WER. C'est un ordre de grandeur sous l'effet taille du modele.

Pourquoi :

- Le dataset MInDS-14 est de la parole bancaire, pas du vocabulaire Nestle.
- Le prompt Nestle n'avait pas de termes reels a reconnaitre dans les references.
- Le LoRA a ete entraine sur MInDS-14, donc sur un domaine probablement deja bien couvert par Whisper.

Phrase cle :

> Ce n'est pas la preuve que l'adaptation ne sert a rien ; c'est la preuve que, sur ce dataset, il n'y avait pas assez d'ecart de domaine a combler.

Piege :

> "Donc votre adaptation ne marche pas ?"

Reponse :

> La machinerie fonctionne : le LoRA s'entraine, la contamination est controlee, l'evaluation est appariee. Mais le gain est faible et non significatif sur ce corpus. La vraie valeur de l'adaptation doit etre testee sur du vocabulaire vraiment divergent, par exemple des termes internes Nestle, indisponibles pour raisons de confidentialite.

---

## 5. La structure du memoire, chapitre par chapitre

### Introduction generale

But : poser le probleme humain et scientifique.

A comprendre :

- Les reunions multinationales melangent langues, accents, bruit et vocabulaire metier.
- Les employes malentendants dependent fortement de la transcription.
- Les benchmarks publics ne suffisent pas.
- Ton objectif est de mesurer un pipeline STT local.

Phrase mentale :

> On part d'un besoin d'accessibilite, pas d'une fascination pour Whisper.

### Chapitre I : etat de l'art

But : montrer que tu connais le paysage.

Familles a connaitre :

- ASR classique : GMM-HMM, DNN-HMM.
- ASR moderne : CTC, encoder-decoder, Transformers.
- Whisper : robuste et multilingue, mais batch, autoregressif, peut halluciner.
- wav2vec 2.0 / MMS : CTC, rapide, interessant si langue connue.
- Conformer : attention + convolution, rapide et performant en CTC.
- Noise robustness : spectral gating, augmentation, beamforming, VAD.
- Domain adaptation : prompting, fine-tuning, LoRA.
- Diarization : identifier qui parle.

Phrase mentale :

> La litterature traite souvent chaque probleme separement ; mon travail mesure plusieurs difficultes ensemble sur un pipeline fixe.

### Chapitre II : methodologie et implementation

But : expliquer ce que tu as construit et comment tu as mesure.

A connaitre :

- FastAPI expose `/transcribe`, `/ws/transcribe`, `/ocr`, `/ask`, `/health`.
- Ton sujet est Topic 2 STT ; OCR et RAG existent dans la plateforme mais ne sont pas l'objet central du memoire.
- `TranscribeConfig` centralise les options : modele, langue, preprocessing, prompt, timestamps, VAD.
- Dataset : MInDS-14, 36 clips, EN/FR/DE, clean/noisy.
- Conditions : baseline, noisereduce, VAD, prompt, langue forcee, tailles de modele.
- Metriques : WER, CER, RTF.

Phrase mentale :

> Je tiens le pipeline fixe et je change une variable a la fois.

### Chapitre III : resultats et discussion

But : defendre les constats mesures.

A connaitre :

- Bruit = facteur dominant.
- Noise reduction = compromis.
- VAD = autre compromis, pas bouton magique.
- Langue forcee = resultat le plus actionnable.
- Taille modele = levier de precision dominant.
- Prompt/LoRA = faible effet ici.
- MMS/Conformer = comparaisons utiles mais attention au confound "langue donnee".
- FLEURS = validite externe : large-v3 fait 7.4 % WER sur parole propre lue.
- Diarization = fonctionne mecaniquement, mais DER difficile a interpreter sur reunions simulees.

Phrase mentale :

> Le chapitre resultats n'est pas une vitrine ; c'est un audit experimental.

### Conclusion

But : fermer proprement.

A dire :

- Objectifs atteints : dataset, pipeline, evaluation.
- Principaux leviers : modele, langue, bruit.
- Limites : dataset proxy, bruit synthetique, pas de vraies reunions Nestle.
- Perspectives : donnees Nestle, fine-tuning texte ou LoRA cible, vraies reunions multi-locuteurs, securite/authentification, integration Teams/Azure.

---

## 6. Le code a comprendre pour te l'approprier

Tu n'as pas besoin de connaitre chaque ligne. Tu dois savoir tracer le chemin d'une requete et le chemin d'une experience.

### 6.1 Fichier central : `backend/stt/engine.py`

Role :

> C'est le moteur STT. Il charge Whisper, applique eventuellement le preprocessing, transcrit, calcule la duree, et ajoute la diarization si disponible.

Elements a connaitre :

- `DEFAULT_DOMAIN_PROMPT` : liste de termes Nestle injectes dans Whisper quand le prompt est active.
- `TranscribeConfig` : objet de configuration unique.
- `load_model()` : charge et met en cache le modele Whisper.
- `preprocess_audio()` : resample en 16 kHz mono et applique `noisereduce`.
- `transcribe_file()` : fonction principale de transcription.
- `get_audio_duration()` : calcule la duree audio pour le RTF.

Trace mentale de `transcribe_file()` :

1. Recoit un fichier audio.
2. Construit ou recoit un `TranscribeConfig`.
3. Charge le modele via `load_model()`.
4. Si `preprocessing=True`, applique `preprocess_audio()`.
5. Prepare les options Whisper : langue, prompt, timestamps, VAD.
6. Lance `model.transcribe()`.
7. Regroupe les segments en texte complet.
8. Calcule temps de traitement et duree audio.
9. Si pyannote est disponible, aligne les speakers.
10. Retourne texte, segments, langue detectee, duree, temps, modele.

Phrase orale :

> Le coeur du code est `transcribe_file()`. Toutes les conditions experimentales ne sont que des configurations differentes de cette fonction.

### 6.2 Fichier API : `backend/main.py`

Role :

> C'est la porte d'entree FastAPI de la plateforme.

Endpoints a connaitre :

| Endpoint | Role | Sujet |
|---|---|---|
| `POST /transcribe` | upload audio puis transcription | Topic 2 |
| `WS /ws/transcribe` | transcription live par WebSocket | Topic 2 |
| `POST /ocr` | OCR document/image | Topic 1 |
| `POST /ask` | question sur contenu ingere | Topic 3 |
| `GET /health` | etat du systeme | plateforme |
| `GET /research` | dashboard evidence | support soutenance |

Trace mentale de `/transcribe` :

1. Verifie extension audio/video.
2. Sauvegarde le fichier dans `storage/uploads`.
3. Appelle `transcribe_file()` dans `run_in_executor`.
4. Ingest le texte dans ChromaDB via `backend.rag.vectorstore.ingest`.
5. Retourne JSON : transcript, segments, duree, temps, modele, chunks RAG.

Pourquoi `run_in_executor` ?

> Whisper est un appel lourd et bloquant. `run_in_executor` evite de bloquer la boucle async FastAPI.

Trace mentale de `/ws/transcribe` :

1. Le navigateur envoie des chunks PCM 16 kHz.
2. Silero VAD calcule si le chunk contient de la parole.
3. Le handler bufferise jusqu'a 0.6 s de silence.
4. Il transcrit l'utterance.
5. Il filtre les repetitions/hallucinations evidentes.
6. Il mesure la latence dans `results/live_latency.csv`.
7. Il renvoie speaker, texte, start, end.

Phrase orale :

> Le live n'est pas du streaming frame-synchrone natif ; c'est un compromis : VAD pour segmenter, puis Whisper batch sur chaque utterance.

### 6.3 Fichier metriques : `backend/evaluation/metrics.py`

Role :

> C'est le scoreur canonique WER/CER/RTF.

Fonctions :

- `normalize_text()` : minuscules, suppression ponctuation, espaces normalises.
- `_levenshtein()` : distance d'edition par programmation dynamique.
- `wer()` : edit distance au niveau mots.
- `cer()` : edit distance au niveau caracteres.
- `rtf()` : temps de traitement / duree audio.

Formule :

```text
WER = (substitutions + deletions + insertions) / nombre de mots reference
RTF = processing_time / audio_duration
```

Important :

- WER peut depasser 100 % si l'hypothese est beaucoup plus longue que la reference.
- C'est normal avec hallucinations ou repetitions.
- Le meme scoreur est utilise partout : Whisper, MMS, Conformer, LoRA.

Phrase orale :

> L'interet du scoreur maison est la transparence : les regles de normalisation sont connues et identiques pour tous les modeles.

### 6.4 Fichier runner : `backend/evaluation/runner.py`

Role :

> C'est le harnais experimental. Il applique les conditions aux samples, appelle le moteur STT, calcule WER/CER/RTF et ecrit les CSV.

Trace mentale de `run_single()` :

1. Recoit un sample.
2. Cree une config.
3. Lance `transcribe_file()`.
4. Lit la reference.
5. Calcule WER, CER, RTF.
6. Sauvegarde le transcript.
7. Retourne un `EvalResult`.

Trace mentale de `run_evaluation()` :

1. Boucle sur tous les samples.
2. Boucle sur toutes les conditions.
3. Appelle `run_single()`.
4. Ecrit le CSV final.

Phrase orale :

> Le runner transforme le pipeline en experience reproductible.

### 6.5 Fichiers training / extensions

| Fichier | Role |
|---|---|
| `backend/training/build_train_split.py` | construit le train split LoRA sans contamination |
| `backend/training/train_lora.py` | entraine l'adaptateur LoRA |
| `backend/training/eval_lora.py` | compare Whisper-small vanilla vs LoRA |
| `backend/training/eval_wav2vec.py` | benchmark MMS/wav2vec 2.0 |
| `backend/training/eval_conformer.py` | benchmark Conformer NeMo |
| `backend/training/build_meetings.py` | cree reunions simulees |
| `backend/training/eval_meetings.py` | evalue diarization avec DER |

Phrase mentale :

> Le code est organise en deux mondes : le pipeline applicatif, et les scripts experimentaux qui produisent les resultats du memoire.

---

## 7. Comment memoriser sans apprendre betement

### Methode generale : 3 couches

Tu dois memoriser en couches :

1. Couche histoire : pourquoi ce sujet existe.
2. Couche experience : comment tu as mesure.
3. Couche code : ou chaque idee vit dans le depot.

Si tu connais seulement les chiffres, tu paniqueras quand on demandera "pourquoi".  
Si tu connais seulement le code, tu paniqueras quand on demandera "so what".  
Il faut les deux.

### Jour 1 : carte mentale

Objectif : savoir raconter le memoire en 3 minutes.

Exercice :

1. Ferme le document.
2. Reponds a voix haute :
   - Quel probleme humain ?
   - Quel probleme technique ?
   - Quel pipeline ?
   - Quel dataset ?
   - Quels resultats ?
   - Quelles limites ?
3. Recommence jusqu'a pouvoir le faire sans hesiter.

Phrase cible :

> J'ai construit et evalue un pipeline local STT pour l'accessibilite en reunion multilingue. J'ai mesure 468 transcriptions sur un dataset trilingue public avec bruit controle. Les resultats montrent que le bruit domine, que la taille du modele est le plus gros levier de precision, que forcer la langue est immediatement utile, et que prompting/LoRA donnent peu sur ce dataset. Les limites viennent surtout de l'absence de donnees Nestle reelles.

### Jour 2 : chiffres

Objectif : connaitre les chiffres sans regarder.

A memoriser :

- 36 clips.
- 468 runs.
- Bruit apparie : 61.1 -> 96.4, soit +35.3 points.
- Taille : 63.4 -> 24.6.
- Prompt/LoRA : environ 1 point.
- FR auto-detect : 42 % d'echecs.
- Live historique : 0.56 s mediane, 0.84 s p95, 1.18 s maximum ; consulter aussi l'audit des 38 observations.

Technique :

Associe chaque chiffre a une image mentale :

- 36 = petit dataset pilote.
- 468 = grosse campagne tracee.
- 61 -> 96 = environ 35 points de degradation sur les memes enonces.
- 63 -> 25 = modele plus grand.
- 1 point = adaptation faible ici.
- 42 = francais auto-detect fragile.
- 0.56 = live rapide.

### Jour 3 : code

Objectif : pouvoir tracer une requete.

Exercice 1 : trace `/transcribe`

Dis a voix haute :

> FastAPI recoit le fichier, verifie l'extension, sauvegarde, appelle `transcribe_file`, puis ingere le texte dans ChromaDB.

Exercice 2 : trace une evaluation

Dis :

> `run_evaluation` parcourt samples et conditions, `run_single` configure le pipeline, appelle `transcribe_file`, lit la reference, calcule WER/CER/RTF et ecrit le CSV.

Exercice 3 : explique WER

Dis :

> WER est la distance de Levenshtein au niveau mots : substitutions, deletions et insertions divisees par le nombre de mots reference.

### Jour 4 : pieges du jury

Objectif : transformer les faiblesses en preuves de maturite.

Repete ces cinq reponses :

1. Dataset pas Nestle :
   > Oui, c'est la limite principale. Les donnees Nestle sont confidentielles. J'ai donc utilise MInDS-14, public, licencie et multilingue, comme proxy controle, en declarant clairement que ce n'est pas une preuve finale sur reunions Nestle.

2. WER eleve :
   > Justement, le memoire quantifie la degradation dans un contexte difficile. Les chiffres eleves ne sont pas caches ; ils montrent les limites du petit modele et l'interet des leviers testes.

3. Prompt inefficace :
   > Le dataset ne contient pas de vocabulaire Nestle, donc je ne pouvais pas mesurer le benefice du prompt. J'ai mesure son cout et un risque : prompt leakage.

4. LoRA faible :
   > L'experience est propre et appariee, mais le domaine d'entrainement est proche de ce que Whisper connait deja. Le gain faible est donc interpretable, pas honteux.

5. DER mauvais :
   > Le DER mesure surtout l'artificialite du testbed simule. La diarization tourne, mais une evaluation valide demande de vraies reunions multi-locuteurs.

### Jour 5 : simulation soutenance

Objectif : etre fluide.

Programme :

1. Pitch 3 minutes.
2. Explication code 5 minutes.
3. Resultats 5 minutes.
4. Limites 3 minutes.
5. Questions pieges 10 minutes.

Regle :

> Ne cherche pas a parler vite. Cherche a parler proprement.

---

## 8. Les 20 questions probables du jury

### 1. Quelle est votre contribution principale ?

> Ma contribution est une evaluation controlee et reproductible d'un pipeline STT local pour conditions multilingues et bruitees, avec un protocole qui isole l'effet marginal de plusieurs leviers : preprocessing, prompting, langue forcee, taille du modele, LoRA et architectures alternatives.

### 2. Pourquoi ce sujet est important ?

> Parce que pour les employes malentendants, la transcription n'est pas un confort mais un canal d'acces au contenu de la reunion. Or les conditions reelles d'entreprise sont plus difficiles que les benchmarks classiques.

### 3. Pourquoi Whisper ?

> Whisper est multilingue, robuste aux accents, disponible publiquement, et faster-whisper permet une inference optimisee en local. C'etait donc un bon choix pour un pilote auditable sans service proprietaire.

### 4. Pourquoi faster-whisper ?

> Parce qu'il utilise CTranslate2 et permet notamment l'INT8 sur CPU, ce qui reduit les besoins materiels tout en gardant une inference efficace.

### 5. Pourquoi ne pas utiliser Azure Speech ou Google Speech ?

> Ces services sont pertinents comme comparaison future, mais ce travail vise un pipeline local, auditable et mesurable. Une API SaaS est une boite noire : je ne controle ni les poids, ni le decoding, ni l'adaptation, et l'audio quitte l'environnement local.

### 6. Pourquoi MInDS-14 ?

> Parce qu'il est public, licencie CC-BY-4.0, multilingue et contient de la vraie parole spontanee. Ce n'est pas une reunion Nestle, et cette limite est declaree clairement.

### 7. Pourquoi seulement 36 clips ?

> C'est une evaluation pilote sous contraintes de temps, confidentialite et ressources. Pour compenser, toutes les comparaisons utilisent le meme dataset, le meme scoreur, et les resultats importants sont analyses avec intervalles bootstrap.

### 8. Est-ce statistiquement fragile ?

> Les petits effets le sont, et je ne les survends pas. Les gros effets comme bruit et taille du modele ont des intervalles qui excluent zero ; LoRA traverse zero, donc je le presente comme non significatif.

### 9. Pourquoi le WER peut depasser 100 % ?

> Parce que le WER inclut les insertions. Si le modele hallucine une sortie beaucoup plus longue que la reference, le nombre d'erreurs peut depasser le nombre de mots reference.

### 10. Pourquoi le bruit blanc ?

> Le bruit blanc a SNR controle est reproductible et permet d'isoler l'effet du bruit. Il ne remplace pas le brouhaha reel ou la reverberation, et cette limite est declaree.

### 11. Que fait `noisereduce` ?

> Il applique une forme de spectral gating : il estime un profil de bruit et attenue certaines frequences. C'est utile en bruit, mais peut abimer des signaux propres.

### 12. Que fait le VAD ?

> Il detecte les zones de parole et evite de transcrire silence ou bruit. Mais s'il classe mal de la parole bruitee comme silence, il peut supprimer de l'information utile.

### 13. Pourquoi la langue forcee aide ?

> Parce que Whisper fait une decision de langue par segment. Sur clips courts ou bruites, cette decision peut etre fausse. Forcer la langue evite des sorties en mauvais alphabet.

### 14. Pourquoi le prompt Nestle peut halluciner ?

> L'initial prompt donne un contexte au decodeur autoregressif. Sur audio faible ou ambigu, le decodeur peut se raccrocher au prompt et injecter des mots qui n'ont pas ete prononces.

### 15. Que prouve le LoRA ?

> Il prouve que la chaine de fine-tuning est fonctionnelle et controlee, mais pas que l'adaptation resout le probleme Nestle. Sur ce dataset proche du pretraining de Whisper, le gain est faible.

### 16. Pourquoi MMS et Conformer sont-ils plus rapides ?

> Ce sont des modeles CTC, qui decodent souvent plus simplement et plus vite que le decodeur autoregressif de Whisper.

### 17. Peut-on dire que Conformer bat Whisper ?

> Pas directement. Conformer recoit la langue par construction avec des checkpoints monolingues, alors que Whisper peut faire de l'auto-detection. La comparaison juste est caveatee.

### 18. Votre WebSocket est-il du vrai streaming ASR ?

> Non. C'est un compromis live : le VAD detecte une utterance, puis Whisper transcrit le buffer. Ce n'est pas un RNN-T frame-synchrone.

### 19. Le systeme est-il deployable en production ?

> Pas tel quel. Il manque authentification, scoping par utilisateur/reunion, gouvernance de donnees et evaluation sur vraies reunions. C'est un pilote local mesure, pas un produit final.

### 20. Quelle est la prochaine etape la plus importante ?

> Obtenir un petit dataset autorise avec vocabulaire Nestle reel. C'est la cle pour tester vraiment le benefice du prompt et du fine-tuning.

---

## 9. Les phrases interdites

Ne dis jamais :

- "J'ai prouve que ca marche pour les reunions Nestle."
- "Le prompt ameliore le vocabulaire Nestle."
- "LoRA ne sert a rien."
- "Conformer est meilleur que Whisper" sans caveat.
- "Le DER prouve que pyannote est mauvais."
- "Le systeme est production-ready."
- "Le WER live est bon" si tu n'as pas de ground truth.
- "Le dataset est representatif des reunions d'entreprise."

Dis plutot :

- "J'ai mesure un proxy public controle."
- "Le benefice du prompt n'est pas mesurable sur ce dataset."
- "LoRA a un effet faible ici, probablement faute d'ecart de domaine."
- "Conformer est tres fort en langue donnee, mais la comparaison avec Whisper-auto est confondee."
- "Le DER est borne par l'artificialite du testbed."
- "Le systeme est un pilote local, pas un deploiement production."

---

## 10. Ton pitch de 90 secondes

> My thesis addresses automatic speech recognition for workplace accessibility, especially for hearing-impaired employees in multilingual corporate meetings. The problem is that real meetings combine background noise, language switching and domain-specific vocabulary, while most published ASR benchmarks are cleaner and more controlled.
>
> I implemented a local STT pipeline based on faster-whisper and evaluated it under controlled conditions using a trilingual MInDS-14 dataset with clean and noise-augmented audio. The experimental campaign includes 468 transcription runs: a CPU pilot, GPU model-size extensions, VAD, LoRA fine-tuning, and comparisons with MMS and Conformer.
>
> Matched noise augmentation raises baseline WER from 61.1 to 96.4 percent on twelve paired utterances. Model size is the strongest accuracy lever, reducing mean WER from 63.4 percent with tiny to 24.6 percent with large-v3. Providing the expected language repairs several wrong-script outputs, but direct language-identification accuracy was not logged in the CPU pilot. Prompting and LoRA only changed WER by about one point on this dataset; a reliable LoRA benefit is not established.
>
> The work is deliberately honest about its limits: the dataset is not real Nestle meeting audio, the noise is synthetic, and the system is a pilot rather than a production deployment. The contribution is therefore not a universal ASR solution, but a reproducible measurement of what works, what fails, and what should be tested next.

---

## 11. Ton pitch de 30 secondes

> I measured a local faster-whisper STT pipeline for noisy multilingual speech in an accessibility context. On 468 traceable runs, noise was the main degradation factor, model size was the strongest accuracy lever, forced language was the most practical zero-cost fix, and prompting/LoRA had only marginal effect on this proxy dataset. The thesis is honest about the main limitation: without real Nestle audio, it is a controlled pilot, not a final production proof.

---

## 12. Comment repondre quand tu ne sais pas

Tu n'as pas besoin d'avoir reponse a tout. Tu dois repondre avec maturite.

Formule universelle :

> That is a valid limitation. In this work, I did not measure that directly. What I can say from my data is X. To answer your question properly, the next experiment would be Y.

Exemples :

Question :

> "How would it perform on real Teams meetings?"

Reponse :

> I did not measure real Teams meetings because no confidential Nestle meeting data was available. My data suggests the main risks would be noise, language identification and speaker overlap. The correct next step is a small authorised internal dataset with ground-truth transcripts.

Question :

> "Would Azure be better?"

Reponse :

> It might be. I did not run Azure in this thesis. A fair comparison would require running Azure Speech on the same 36 clips with the same scorer. My contribution is the local, auditable baseline and the measurement framework.

Question :

> "Why are your results worse than Whisper papers?"

Reponse :

> The Whisper paper reports larger models on cleaner public benchmarks. My experiment uses difficult 8 kHz telephone speech, added noise, three languages and small checkpoints. The gap is exactly why this study was needed.

---

## 13. Les cartes mentales du code

### Carte 1 : requete batch

```text
Client
  -> POST /transcribe
  -> sauvegarde upload
  -> transcribe_file()
       -> load_model()
       -> preprocess_audio() si active
       -> model.transcribe()
       -> diarization si disponible
  -> ingest ChromaDB
  -> reponse JSON
```

### Carte 2 : evaluation

```text
metadata.csv
  -> load_metadata()
  -> samples
  -> run_evaluation()
       -> run_single()
            -> TranscribeConfig
            -> transcribe_file()
            -> wer/cer/rtf
            -> save transcript
  -> CSV resultats
  -> tableaux memoire
```

### Carte 3 : RAG

```text
Transcript ou OCR
  -> chunk_text
  -> embeddings multilingual-e5
  -> ChromaDB
  -> /ask
       -> query top 5 chunks
       -> prompt LLM local
       -> answer avec sources
```

Phrase de defense :

> ChromaDB retrouve les passages ; Ollama genere la reponse. Il ne faut pas inverser les roles.

---

## 14. Le tableau mental des fichiers

| Fichier | A quoi il sert | Ce que tu dois savoir dire |
|---|---|---|
| `Memoire_LaTeX/main.tex` | version officielle du memoire | structure, resultats, limites |
| `backend/stt/engine.py` | moteur transcription | config, preprocessing, Whisper, diarization |
| `backend/main.py` | API FastAPI | endpoints, batch, live, RAG |
| `backend/evaluation/metrics.py` | WER/CER/RTF | Levenshtein, normalisation |
| `backend/evaluation/runner.py` | evaluations | applique conditions, ecrit CSV |
| `backend/evaluation/statistics.py` | bootstrap/latence | incertitude et CIs |
| `backend/training/train_lora.py` | fine-tuning | LoRA r=16, q/v projections |
| `backend/training/eval_wav2vec.py` | MMS | CTC, langue donnee |
| `backend/training/eval_conformer.py` | Conformer | NeMo CTC, rapide |
| `results/*.csv` | sources de verite | chaque chiffre doit etre tracable |
| `results/bootstrap_ci.md` | intervalles confiance | gros effets robustes, LoRA non significatif |
| `Fiche_Revision_Soutenance.md` | revision rapide | chiffres et pieges |
| `Reponses_Jury.md` | reponses courtes | entrainement Q&A |

---

## 15. Les zones de danger maximum

### Danger 1 : contradiction 432 vs 468

Les supports corriges utilisent 468 runs. Les anciennes versions pouvaient mentionner 432. Si on te demande :

> La version finale integre les extensions qui portent la campagne totale a 468 transcriptions. Certaines notes de preparation plus anciennes mentionnaient 432, mais le chiffre canonique du memoire final est 468.

Action avant envoi : verifier que les exports PDF et les diapositives utilisent eux aussi 468.

### Danger 2 : dataset proxy

Le jury peut dire :

> "Votre titre parle de reunions corporate, mais vos donnees sont telephone banking."

Ta reponse :

> Oui, et c'est la limite principale. Le dataset est un proxy public et licencie, choisi parce que les vraies donnees Nestle etaient indisponibles. Le memoire ne pretend pas que MInDS-14 represente parfaitement les reunions ; il mesure des facteurs proches et isoles : bruit, multilinguisme, parole spontanee et contraintes de pipeline.

### Danger 3 : adaptation de domaine

Le jury peut dire :

> "Vous n'avez pas vraiment teste le vocabulaire Nestle."

Ta reponse :

> Exact. Je n'ai pas pu tester le benefice sur vocabulaire Nestle reel, faute de donnees autorisees. J'ai teste le cout et les risques du prompt sur un dataset domain-mismatched, notamment le prompt leakage. C'est pourquoi la perspective prioritaire est un petit corpus autorise avec termes Nestle.

### Danger 4 : production readiness

Le jury peut dire :

> "Peut-on deployer chez Nestle demain ?"

Ta reponse :

> Non, pas tel quel. Le pilote montre que le pipeline fonctionne et permet de mesurer les bons leviers. Pour production, il faut authentification, controle d'acces, gouvernance, tests sur vraies reunions, et integration IT.

### Danger 5 : comparaison architectures

Le jury peut dire :

> "Conformer est meilleur, donc pourquoi Whisper ?"

Ta reponse :

> Conformer est tres rapide et performant en langue donnee, mais il utilise des checkpoints monolingues. Whisper offre detection multilingue native, ponctuation, timestamps, et un pipeline plus adapte quand la langue n'est pas connue a l'avance. Je presente Conformer comme baseline serieuse, pas comme remplacement automatique.

---

## 16. Check-list avant soutenance

### A corriger dans les fichiers

- Supprimer ou completer les `\todo{ ...}` dans `Memoire_LaTeX/main.tex`.
- Verifier que les exports des supports conservent le total corrige de 468.
- Verifier que le PDF compile proprement.
- Verifier que les tableaux du deck reprennent les chiffres finaux.
- Ne pas utiliser `Topic2_Thesis_Rewrite.md` comme source finale si `main.tex` est plus a jour.

### A imprimer ou garder sous les yeux

- `Fiche_Revision_Soutenance.md`
- `Reponses_Jury.md`
- `results/bootstrap_ci.md`
- Ce guide

### A repeter

- Pitch 90 secondes.
- Explication du pipeline batch.
- Explication WER/CER/RTF.
- Les 5 pieges principaux.
- Les limites sans te justifier trop longtemps.

---

## 17. Attitude de soutenance

Tu dois avoir trois postures :

### 1. Calme

Quand une question attaque une limite, ne te crispe pas. Souvent, la bonne reponse commence par :

> Yes, that is a real limitation.

Ca montre que tu maitrises.

### 2. Precis

Ne donne pas de chiffre invente. Si tu n'as pas mesure, dis :

> I did not measure that directly.

### 3. Scientifique

Ramene toujours a :

- ce qui est mesure ;
- avec quelle methode ;
- sur quelles donnees ;
- avec quelle limite ;
- quelle experience future permettrait de conclure mieux.

---

## 18. Mini-glossaire a maitriser

| Terme | Definition simple |
|---|---|
| ASR/STT | transformer la parole en texte |
| WER | taux d'erreur mot, distance reference/hypothese |
| CER | taux d'erreur caractere |
| RTF | temps traitement / duree audio |
| Whisper | modele encoder-decoder autoregressif multilingue |
| faster-whisper | implementation optimisee avec CTranslate2 |
| INT8 | quantification 8 bits, utile CPU |
| float16 | precision GPU plus rapide que float32 |
| VAD | detection des zones de parole |
| Diarization | identifier qui parle quand |
| Prompting | injecter du vocabulaire au decoding |
| LoRA | fine-tuning parameter-efficient |
| CTC | famille de decodage rapide, non autoregressive |
| MMS | modele wav2vec 2.0 multilingual de Meta |
| Conformer | architecture attention + convolution |
| ChromaDB | base vectorielle pour retrieval |
| RAG | retrieval + generation |

---

## 19. La reponse finale si on te demande "qu'avez-vous appris ?"

> J'ai appris que dans ce probleme, la difficulte principale n'est pas d'appeler un modele Whisper, mais de mesurer proprement son comportement dans des conditions realistes et de ne pas confondre prototype, benchmark et produit. Les resultats montrent que les leviers n'ont pas le meme ordre de grandeur : la taille du modele et la qualite audio dominent, la langue forcee est un gain pratique tres fort, et l'adaptation de domaine ne peut etre jugee honnetement qu'avec de vraies donnees de domaine. C'est cette hierarchie des leviers que mon memoire apporte.

---

## 20. Plan d'entrainement express sur 48 heures

### H-48 a H-36

- Lire l'introduction et la conclusion.
- Apprendre le pitch 90 secondes.
- Reciter les 5 chiffres.
- Relire les limites.

### H-36 a H-24

- Lire les sections resultats.
- Faire 20 questions jury a voix haute.
- Refaire le tableau des modeles de memoire.
- Tracer `/transcribe` sur papier.

### H-24 a H-12

- Repetition complete avec slides.
- Chronometrer.
- Revoir uniquement les zones faibles.
- Dormir suffisamment.

### H-12 a H-1

- Ne plus apprendre de nouvelles choses.
- Relire pitch, chiffres, pieges.
- Respirer.
- Te rappeler : tu as construit, mesure, corrige et compris.

---

## 21. Ta boussole finale

Si le jury cherche a te coincer, ta defense tient en cinq mots :

> mesure, trace, limite, caveat, perspective.

Tu as mesure.  
Tu peux tracer les chiffres jusqu'aux CSV.  
Tu connais les limites.  
Tu sais mettre les caveats.  
Tu proposes les perspectives naturelles.

C'est exactement ce qu'on attend d'un bon memoire de master.
