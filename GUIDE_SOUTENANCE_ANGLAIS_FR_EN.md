# Comprendre et defendre mon memoire en anglais

Guide bilingue pour OUEDRAOGO Yannick Ulrich Levi. Sujet : Topic 2, Speech-to-Text.

## 1. Ton objectif

Tu dois comprendre ton travail, reconnaitre ce que le jury demande et repondre avec des mots que tu maitrises. Tu n'as pas besoin d'un accent parfait. Une phrase courte et exacte vaut mieux qu'une phrase savante dont tu ne comprends pas les limites.

Ce guide complete `GUIDE_DEFENSE_MEMOIRE_DEBUTANT_A_Z.md` pour les notions et `COMPLEMENTS_TOPIC2.md` pour les preuves et limites. Il suit la revision anglaise `Memoire_LaTeX/main_revised.tex`. C'est un parcours d'apprentissage, pas une traduction integrale ligne par ligne du memoire.

Les reponses anglaises ci-dessous sont des modeles a reformuler. Verifie que toute phrase au passe decrit bien un travail realise et que toute phrase avec "would" decrit une proposition. Les experiences complementaires sur reunions reelles ne sont pas encore executees.

## 2. La carte mentale bilingue du travail

| Etape | Ce que cela veut dire | Ce que tu peux dire en anglais |
|---|---|---|
| Probleme | La parole peut etre mal transcrite avec du bruit et plusieurs langues | Background noise and multiple languages make speech recognition challenging. |
| Objectif | Comparer des solutions et comprendre leurs limites | My goal was to evaluate transcription accuracy and processing speed. |
| Donnees | Audio et texte attendu pour verifier le resultat | I used audio recordings and reference transcripts. |
| Systeme | Transformer le son en texte avec un modele existant | I implemented a configurable pipeline based on pretrained models. |
| Experience | Changer un element et comparer les sorties | I compared configurations on the same evaluation files. |
| Mesure | Compter les erreurs et chronometrer le traitement | I measured word error rate and processing time. |
| Resultat | Dire ce que montrent effectivement les calculs | Larger Whisper models achieved lower average word error rates on this dataset. |
| Limite | Dire ce que les donnees ne permettent pas de prouver | The main dataset does not represent real corporate meetings. |
| Suite | Expliquer quelle experience manque | The next step would be a controlled evaluation on real meeting audio. |

Exercice : cache la colonne anglaise. Explique chaque etape en une phrase anglaise differente. Ensuite, explique en francais le sens de ta propre phrase. Si tu ne peux pas revenir au francais, tu as peut-etre memorise le son sans comprendre.

## 3. Vocabulaire technique depuis zero

| Anglais | Francais et sens simple | Phrase utile |
|---|---|---|
| speech | parole | The input is speech. |
| speech-to-text / STT | transformation de la parole en texte | STT produces a transcript from audio. |
| automatic speech recognition / ASR | reconnaissance automatique de la parole | ASR is the core task of my thesis. |
| utterance | un enonce, une portion de parole | Each utterance has a reference transcript. |
| transcript | texte de ce qui est dit | The transcript contains recognition errors. |
| transcription | action ou resultat de transcrire | I evaluated transcription accuracy. |
| reference / ground truth | annotation servant de comparaison, a verifier | The reference is the expected text. |
| hypothesis | ici, texte produit par le modele ; ailleurs, hypothese de recherche | I compared the hypothesis with the reference. |
| dataset / corpus | ensemble de donnees | The dataset contains three languages. |
| sample | un exemple du jeu | This sample is a noisy recording. |
| baseline | point de comparaison de depart | I compared the adapted model with its baseline. |
| pretrained model | modele deja entraine avant ton travail | I used pretrained models. |
| training | apprentissage des parametres a partir de donnees | Training updates model parameters. |
| inference | utilisation du modele pour produire un resultat | Inference produces the transcript. |
| fine-tuning | adaptation d'un modele deja entraine | Fine-tuning uses additional training data. |
| weights / parameters | valeurs numeriques apprises par le modele | LoRA updates a small set of additional parameters. |
| prompt | indices textuels donnes au modele | The prompt contains domain vocabulary. |
| domain | type de contenu, par exemple banque ou industrie | Banking speech differs from meeting speech. |
| noise reduction | traitement cherchant a attenuer le bruit | Noise reduction also affected clean speech. |
| clean / noisy | propre / bruite, selon les categories de l'etude | I compared clean and noisy versions. |
| paired comparison | comparaison des memes exemples sous deux conditions | A paired comparison controls for the spoken content. |
| word error rate / WER | taux d'erreur sur les mots | Lower WER is better. |
| character error rate / CER | taux d'erreur sur les caracteres | CER measures character-level errors. |
| substitution / deletion / insertion | mot remplace / retire / ajoute | Insertions can make WER exceed one hundred percent. |
| real-time factor / RTF | temps de calcul divise par duree audio | An RTF below one indicates faster-than-real-time processing for that measurement. |
| latency / delay | delai avant un evenement defini | This latency does not include browser rendering. |
| endpointing | decision que l'enonce est termine | Endpointing introduces an additional waiting period. |
| voice activity detection / VAD | detection des portions contenant de la parole | VAD detects speech activity. |
| speaker diarization | attribution des portions de parole a des locuteurs | Diarization addresses who spoke when. |
| overlap | paroles simultanees | Real meetings may contain overlapping speech. |
| code-switching | changement de langue dans une conversation ou un enonce | Separate language tests do not validate code-switching. |
| confidence interval | intervalle exprimant l'incertitude de l'estimation selon une methode | The interval includes zero. |
| statistical significance | resultat d'une evaluation statistique de l'evidence, pas importance pratique | A reliable LoRA improvement was not established. |
| generalization | comportement sur des donnees nouvelles | Generalization to real meetings remains untested. |
| limitation | frontiere de ce que tu peux conclure | This is a limitation of the evaluation. |
| trade-off | compromis entre deux objectifs | There is an accuracy-latency trade-off. |
| reproducible | calcul que l'on peut reproduire avec les informations necessaires | The statistical audit is reproducible from the CSV files. |

Ne confonds pas "speaker" (personne qui parle) et "speech" (parole). "Accuracy" veut souvent dire exactitude au sens general ; ton indicateur principal est le WER. Ne transforme pas automatiquement WER en "accuracy = 100 - WER".

## 4. Lire les phrases scientifiques anglaises

### Reperer qui fait quoi

Phrase : "The model generates a transcript from the audio signal."

The model = le modele, sujet. Generates = produit, action. A transcript = une transcription, resultat. From the audio signal = a partir du signal audio, entree.

Reformulation simple : "Audio goes in. Text comes out." Tu dois ensuite pouvoir expliquer les etapes intermediaires en francais.

### Comprendre le passif

"The model was evaluated on 36 files" signifie "Le modele a ete evalue sur 36 fichiers". Le passif decrit ce qui a ete fait au modele. Tu peux reformuler : "I evaluated the model on 36 files."

"The model was trained on..." parle d'apprentissage. "The model was evaluated on..." parle de mesure. Confondre ces verbes peut faire croire que tu as entraine sur le test.

### Comprendre le niveau de certitude

| Expression | Sens | Usage dans ton travail |
|---|---|---|
| shows | montre | The table shows the measured WER. |
| suggests | suggere, sans tout etablir | This suggests that model size matters on this dataset. |
| may / might | peut, pourrait | Noise reduction may remove useful speech information. |
| does not establish | ne permet pas d'etablir | This result does not establish a domain-specific benefit. |
| remains untested | reste non teste | Meeting-level generalization remains untested. |
| would require | necessiterait | A stronger conclusion would require more data. |
| within this study | dans les limites de cette etude | The conclusion holds within this study. |

"Not statistically significant" ne veut pas dire "useless". "Not evaluated" ne veut pas dire "does not work". "No recorded runtime errors" ne veut pas dire "no transcription errors".

### Lire les articulations logiques

Because = parce que, donne une raison. However = cependant, introduit une limite ou un contraste. Therefore = donc, annonce une consequence. Whereas = tandis que, compare. Although = bien que, nuance. In addition = de plus, ajoute.

Exercice : dans chaque paragraphe du memoire, entoure ces mots. Ecris une phrase pour le constat et une autre pour sa limite.

## 5. Lire ton memoire chapitre par chapitre

| Section reelle de la revision | Question a laquelle elle repond | Reformulation anglaise simple |
|---|---|---|
| Abstract | De quoi parle l'ensemble ? | This is a short overview of the problem, method, findings and limitations. |
| General Introduction | Pourquoi ce travail ? | This section explains the research problem and objectives. |
| State of the Art | Que sait-on deja ? | This chapter reviews existing approaches and identifies gaps. |
| Fundamental Concepts | Quelles notions faut-il comprendre ? | This section defines ASR and the evaluation metrics. |
| Critical Review of Related Work | Quels avantages et limites des approches ? | I discuss the strengths and limitations of previous methods. |
| Methodological Approach | Comment organiser une comparaison credibile ? | This chapter explains the dataset and experimental design. |
| Dataset Construction | D'ou viennent les fichiers ? | The evaluation set contains clean recordings and noise-augmented copies. |
| Statistical Analysis Plan | Comment prendre en compte l'incertitude ? | Related files are kept together when estimating uncertainty. |
| Implementation, Experiments and Results | Qu'est-ce qui a ete execute et obtenu ? | This chapter describes the implementation and reports the results. |
| Discussion | Que signifient les resultats et jusqu'ou ? | I interpret the findings and explain their limits. |
| General Conclusion and Perspectives | Quelle contribution et quelle suite ? | The work provides a controlled pilot and identifies the remaining validation steps. |
| Topic 2 Completion Audit and Validation Protocol | Quelles preuves restent incompletes ? | This supplement separates corrected analysis from future experiments. |

Pour CHAQUE paragraphe, remplis cette fiche dans tes notes :

1. Original anglais : une ou deux phrases que tu etudies.
2. Sens francais : explication avec tes mots, sans traduction automatique mot a mot.
3. Anglais simple : une phrase qui garde le sens.
4. Preuve : fichier, experience, reference bibliographique ou simple proposition ?
5. Question du jury : quelle question pourrait remettre cette phrase en cause ?
6. Limite : qu'est-ce que cette phrase ne permet pas de conclure ?

Exemple sur les resultats : "The interval includes zero." Sens : l'estimation reste compatible avec une absence de gain selon cette analyse. Anglais simple : "I cannot claim a reliable improvement." Preuve : audit statistique LoRA. Question : "Was the improvement significant?"

Ordre conseille : introduction, donnees, resultats, limites, puis notions et litterature en allant chercher les definitions necessaires. Relis ensuite l'abstract : chaque affirmation doit te sembler explicable.

## 6. Expliquer le code en anglais

| Fichier | Role a comprendre | Explication orale |
|---|---|---|
| `backend/stt/engine.py` | configuration, chargement et utilisation des modeles | This module configures the model and transcribes audio. |
| `backend/evaluation/dataset.py` | charge les exemples et leurs references | This module loads the evaluation samples and reference paths. |
| `backend/evaluation/runner.py` | execute des conditions et enregistre les mesures | The runner processes each sample and records the results. |
| `backend/evaluation/metrics.py` | calcule les erreurs textuelles | This module compares the predicted text with the reference. |
| `backend/evaluation/statistics.py` | calcule incertitude et resumes | This module estimates uncertainty and summarizes latency. |
| `backend/evaluation/run_statistical_audit.py` | recalcule les contrastes existants | This script reproduces the statistical comparisons from existing CSV files. |
| `backend/evaluation/topic2_readiness.py` | audite les sessions du journal live | This script separates inferred sessions and keeps slow observations visible. |
| `backend/training/build_meetings.py` | assemble des clips avec etiquettes artificielles | This script builds simulated sequences, but its speaker identities are not verified. |
| `backend/training/eval_meetings.py` | execute et evalue la diarisation | This script compares diarization output with the supplied annotations. |
| `backend/main.py` | expose notamment le chemin WebSocket live | The live path receives audio and sends transcription results through a WebSocket. |

Methode pour presenter une fonction : input, operation, output, limitation. Exemple : "The input is an audio file. The function runs the configured model. The output is a transcript. The transcript may contain errors."

Ne dis pas "I created Whisper". Dis "I used Whisper" ou "I implemented and evaluated a Whisper-based pipeline". Pour ta contribution personnelle, sois exact sur ce que tu as ecrit, adapte, verifie et sur l'aide recue. Comprendre un code assiste ne signifie pas que tu as invente son algorithme.

## 7. Dire les nombres sans te perdre

| Nombre | Lecture anglaise | Ce qu'il designe |
|---|---|---|
| 468 | four hundred and sixty-eight | transcriptions canoniques, pas participants |
| 36 | thirty-six | fichiers d'evaluation |
| 24 | twenty-four | enonces sources distincts |
| 12 pairs | twelve pairs | comparaisons propres/bruitees |
| 8 dB | eight decibels | SNR du bruit canonique |
| 61.1% | sixty-one point one percent | WER propre des 12 paires |
| 96.4% | ninety-six point four percent | WER de leurs copies bruitees |
| 35.3 percentage points | thirty-five point three percentage points | difference absolue de WER |
| 24.6% | twenty-four point six percent | WER moyen large-v3 canonique |
| [-2.4, 5.3] | from minus two point four to five point three | intervalle du gain LoRA, en points |
| 0.844 seconds | zero point eight four four seconds | p95 historique, hors premiers enonces |
| 1.614 seconds | one point six one four seconds | p95 du journal etendu, hors premiers enonces |
| 11.021 seconds | eleven point zero two one seconds | maximum du journal etendu |

En anglais, la decimale se dit "point", pas "comma". Pour les valeurs comme 0.844, lis les chiffres apres le point un par un. Tu peux arrondir a l'oral : "about zero point eight four seconds", en gardant la valeur exacte sur la diapositive.

De 61.1 % a 96.4 %, dis "an increase of 35.3 percentage points". Dire "an increase of 35.3 percent" annoncerait une variation relative differente.

Apprends aussi les directions : increased from A to B = a augmente de A a B ; decreased by X = a diminue de X ; decreased to X = a diminue jusqu'a X.

## 8. Presenter ton travail avec des phrases simples

### Introduction courte

"Good morning. My name is Yannick Ulrich Levi Ouedraogo. My research focuses on speech-to-text systems for noisy and multilingual meetings. I will present the problem, the evaluation method, the main results, and the limitations of the study."

Sens : tu annonces qui tu es, ton sujet et ton parcours. Adapte l'ordre de ton nom a celui que tu utilises officiellement.

### Trame de presentation a adapter au temps impose

Les huit blocs suivants constituent un texte de travail. Leur duree depend de ton debit et de tes explications des figures ; chronometre une repetition avant de promettre une duree.

**1. Motivation**

"In multinational workplaces, meetings may involve background noise, several speakers and different languages. These conditions make automatic transcription difficult. Reliable transcripts can support access to spoken information. My contribution concerns the speech-to-text component of the broader accessibility project."

Sens : tu relies le probleme technique a l'usage. Tu ne pretends pas avoir mesure le benefice pour les utilisateurs.

**2. Research questions**

"I investigated three questions. First, how do different speech recognition models perform under noisy and multilingual conditions? Second, what is the effect of adaptation strategies? Third, what can we measure about processing speed and live transcription delay? The current study answers these questions partially."

Sens : les trois questions donnent la structure du memoire. La derniere phrase prepare une discussion honnete des limites.

**3. Data**

"The main evaluation uses MInDS-14, a telephone-banking speech dataset. I selected twenty-four clean recordings in English, French and German. Twelve recordings also have a noise-augmented version. This gives thirty-six evaluation files, but only twenty-four distinct source utterances. These are not real corporate meetings."

Sens : explique a la fois d'ou viennent les donnees et pourquoi le nombre de fichiers ne suffit pas a decrire la taille effective du test.

**4. Method**

"The canonical campaign contains four hundred and sixty-eight transcription runs. I evaluated Whisper configurations, a LoRA adaptation, MMS and Conformer baselines. The same text-scoring procedure was used across models. I also considered preprocessing and language settings. Some comparisons have additional differences, such as whether the language is supplied to the model."

Sens : tu compares des systemes, mais le meme scorer n'efface pas tous les facteurs de confusion.

**5. Main findings**

"On twelve matched pairs, adding noise increased mean word error rate from sixty-one point one to ninety-six point four percent. Larger Whisper models achieved lower average error rates on the canonical set. The mean WER decreased from sixty-three point four percent with tiny to twenty-four point six percent with large-v3. These findings are specific to the evaluated conditions."

Sens : les premiers chiffres concernent les memes phrases avant/apres bruit. L'echelle de modeles est une comparaison de configurations dont les details doivent etre expliques depuis les tableaux ; ne la presente pas comme une ablation purement materielle.

**6. Adaptation**

"The paired LoRA comparison showed an average improvement of about one WER point. However, the confidence interval includes zero. I therefore cannot claim a reliable improvement. The evaluation also does not establish a benefit for Nestle-specific vocabulary, because the main corpus contains banking speech."

Sens : un petit gain observe n'est pas automatiquement une conclusion solide sur ton domaine cible.

**7. Live prototype**

"The prototype includes a live WebSocket path. The historical latency study reported a p95 of about zero point eight four seconds after excluding first utterances. The extended log contains slower observations, with a p95 of about one point six one seconds and a maximum of about eleven seconds. These are server-side measurements, not browser display latency. A controlled accuracy-latency study is still required."

Sens : tu conserves les observations defavorables et tu definis exactement ce que mesure le chronometre.

**8. Contribution and conclusion**

"The contribution is a configurable prototype and a traceable pilot evaluation. The main limitations are the small telephone-speech corpus, unverified speaker identities in the simulated meeting test, and the absence of a controlled end-to-end latency evaluation. The next steps are real meeting data, a vocabulary-focused test and a joint accuracy-latency study. Thank you for your attention. I am ready for your questions."

Sens : tu termines avec la contribution reelle et des suites concretes, sans annoncer que les limites ont disparu.

### Transitions a connaitre

"Let me start with the problem." / Je commence par le probleme.

"I will now explain the dataset." / Je passe aux donnees.

"This table compares the evaluated configurations." / Ce tableau compare les configurations.

"The key point here is..." / L'element a retenir est...

"This result needs one qualification." / Ce resultat demande une nuance.

"This brings me to the limitations." / Cela m'amene aux limites.

"To answer the research question..." / Pour repondre a la question de recherche...

### Commenter une figure

Dans cet ordre : ce qui est compare, unite, direction utile, resultat, limite.

"This figure compares word error rates across model configurations. The values are percentages, and lower is better. Large-v3 has a lower average error rate in this evaluation. However, these results come from a small telephone-speech dataset."

Ne lis pas chaque cellule. Montre un contraste utile et explique pourquoi il compte.

## 9. Comprendre une question du jury a l'oreille

Tu ne dois pas traduire toute la phrase avant de comprendre son intention. Cherche le type de demande, le sujet et les mots qui changent le sens.

| Debut ou mot entendu | Ce que le jury attend |
|---|---|
| What do you mean by...? / Could you define...? | definition |
| Why did you choose...? / What motivated...? | justification |
| How did you evaluate...? / Could you walk us through...? | methode, etapes |
| How many...? / How much...? | nombre ou quantite avec unite |
| Compared with what...? / What was your baseline? | point de comparaison |
| What evidence supports...? / How do you know...? | preuve et mesure |
| Does this imply...? / Can you conclude...? | portee de la conclusion |
| To what extent...? / Under what conditions...? | jusqu'ou et dans quelles conditions |
| What if...? / Suppose that...? | scenario hypothetique |
| What are the limitations...? / What remains untested? | limites |
| What would you change...? / How would you extend...? | suite proposee, pas resultat passe |

Attention aux negations : "Why did you NOT use real meetings?" demande pourquoi tu ne les as pas utilisees. "Did you train on the test set?" concerne la contamination, pas les performances du modele.

La meme question peut prendre plusieurs formes :

- "Why did you choose MInDS-14?"
- "What motivated your dataset selection?"
- "Could you justify the use of telephone speech for a meeting-related topic?"

Les mots changent, l'intention reste : justifier les donnees et reconnaitre leur limite. Reponse centrale : "It provided a controlled trilingual evaluation set, but it does not validate real meetings."

Autre famille : "Was the LoRA gain significant?", "Is that one-point improvement reliable?", "Does the confidence interval exclude zero?" Les trois demandent la solidite du gain, avec des formulations differentes.

### Procedure en cinq gestes

1. Ecoute jusqu'au bout sans commencer mentalement une longue reponse.
2. Note deux ou trois mots : "dataset - meetings - why", par exemple.
3. Si necessaire, confirme ton interpretation en une phrase.
4. Reponds directement, puis donne une preuve et une limite.
5. Arrete-toi quand la question est traitee ; le jury pourra approfondir.

## 10. Demander une clarification sans perdre le fil

| Situation | Phrase anglaise |
|---|---|
| Pas entendu | Could you repeat the question, please? |
| Debit trop rapide | Could you say that a little more slowly, please? |
| Un terme incompris | Could you clarify what you mean by "robustness" here? |
| Deux interpretations | Are you asking about processing time or end-to-end latency? |
| Question longue | If I understood correctly, you are asking why I used this dataset. Is that right? |
| Plusieurs sous-questions | I heard two questions: one about the data and one about the evaluation. I will start with the data. |
| Besoin d'un instant | Let me think for a moment. |
| Besoin de la figure | May I refer to the results table? |

Tu peux demander une reformulation meme si tu connais tous les mots. Ne dis pas automatiquement "Yes" quand tu n'as pas compris : tu pourrais approuver une conclusion fausse.

## 11. Construire une reponse en anglais

Structure utile : reponse directe -> raison ou preuve -> limite. C'est un appui, pas une formule obligatoire pour toutes les questions.

Question : "Does your evaluation validate real meetings?"

"No, not fully. The main corpus contains single-speaker telephone speech. It supports a controlled component evaluation, but meeting-level validation remains to be done."

Question : "Why did you use paired comparisons?"

"To compare the same spoken content across conditions. Each noisy recording is matched with its clean version. This reduces the influence of differences between sentences."

### Dire que tu ne sais pas

"I did not evaluate that aspect, so I cannot give a measured answer."

"I do not recall the exact value. The result table contains it, and I would prefer to check it."

"My hypothesis is that..., but I would need an experiment to verify it."

Ne transforme pas une hypothese en resultat pour paraitre a l'aise. La phrase "I would test this by..." permet de montrer ton raisonnement apres avoir reconnu ce qui manque.

### Accepter une objection juste

"You are right. That comparison has a limitation."

"I should distinguish the historical study from the extended log."

"That wording is too strong. A more accurate statement would be..."

### Corriger une interpretation incorrecte calmement

"The four hundred and sixty-eight figure refers to transcription runs, not independent recordings."

"The gain is expressed in percentage points, not relative percent."

"Those speaker labels were assigned during construction; they are not verified identities."

## 12. Banque de questions et reponses courtes

Les fichiers audio reprennent les douze premieres questions dans `training/english_defense/questions.json`. Ecoute d'abord sans regarder les reponses.

| Question anglaise | Ce qu'elle demande en francais | Noyau de reponse anglaise |
|---|---|---|
| What is the main contribution of your thesis? | ta contribution | A configurable speech-to-text prototype and a traceable pilot evaluation. |
| Why did you choose MInDS-14 for a topic about meetings? | justification et limite des donnees | It supports a controlled trilingual evaluation, but it does not represent real meetings. |
| How many independent recordings are in your evaluation set? | independance, pas nombre de runs | There are twenty-four source utterances and twelve additional noisy copies. |
| Could you explain how word error rate is calculated? | formule | Add substitutions, deletions and insertions, then divide by the number of reference words. |
| Why did you compare matched clean and noisy recordings? | appariement | To compare the same content before and after noise augmentation. |
| Was the improvement from LoRA statistically significant? | solidite du gain | A reliable improvement was not established; the interval includes zero. |
| How do you know that the system handles multiple speakers correctly? | preuve de diarisation | The simulated labels do not verify real speaker identities, so accuracy is not established. |
| Does your latency measurement include the delay until the text appears in the browser? | delai vraiment mesure | No. It is measured on the server before WebSocket transmission. |
| How do you explain the slow observation in the extended latency log? | cause du ralentissement | The log lacks the information needed to identify the cause. I retained the observation. |
| Did you evaluate changes of language within the same sentence? | code-switching | No. Separate language evaluations do not establish that capability. |
| How would you test the effect of company-specific vocabulary? | protocole futur | Compare the same recordings with and without a fixed glossary and measure term recognition and hallucinations. |
| What would you improve first if you had more time? | priorite | Real meeting data, followed by domain vocabulary and controlled end-to-end latency evaluation. |
| Did you train Whisper from scratch? | origine du modele | No. I used pretrained models and evaluated a LoRA adaptation. |
| Does an RTF below one guarantee live captions without delay? | difference vitesse/delai | No. It measures processing relative to audio duration, not endpoint waiting or browser rendering. |
| Is Conformer universally better than Whisper? | generalisation excessive | No. These results compare particular checkpoints and configurations on a small dataset. |
| Were all models given the same language information? | equite de comparaison | No. MMS and Conformer received the language by construction, which limits interpretation. |
| Can word error rate exceed one hundred percent? | insertions | Yes. Excessive insertions can produce more errors than reference words. |
| Does a one-point gain mean LoRA is useless? | absence de preuve | No. This study does not establish a reliable gain, but it does not establish equivalence or universal failure. |
| Have you demonstrated improved accessibility for hearing-impaired users? | benefice utilisateur | No user study was conducted within this Topic 2 evaluation. |
| What do you mean by reproducible? | preuves et execution | The data, configurations and scoring procedure should allow the reported calculation to be repeated. |

Pour allonger une reponse, ajoute UN exemple ou UN resultat, pas toute l'histoire du memoire. Pour la raccourcir, garde la conclusion et sa limite essentielle.

## 13. Prononciation et aisance

Lis les sigles lettre par lettre en anglais : A-S-R, S-T-T, W-E-R, C-E-R, G-P-U, C-P-U. Tu peux aussi dire "word error rate" au lieu de WER. "P ninety-five" se comprend, mais "the ninety-fifth percentile" explicite le sens.

Pratique ces groupes de mots comme des ensembles : "reference transcript", "background noise", "paired comparison", "confidence interval", "real meeting audio", "end-to-end latency". Evite une transcription phonetique francaise apprise par coeur : elle risque de fixer une prononciation difficile a comprendre. Ecoute la voix, repete et compare ton enregistrement.

Pour presenter, place de petites pauses entre les idees. Exemple : "I used twenty-four source utterances. / Twelve have a noisy copy. / This gives thirty-six files." Les barres sont des pauses de travail, pas du texte a lire.

Si tu bloques sur un mot, simplifie : "the expected text" pour "reference transcript", "who spoke when" pour "diarization", "the time before the result is available" pour "latency", en precisant ensuite l'evenement mesure.

## 14. Exercices d'ecoute avec les audios

Les fichiers WAV sont generes localement avec Microsoft Zira, voix synthetique anglaise americaine. Ils servent a l'entrainement : une voix unique ne prepare pas a tous les accents, aux interruptions ou a l'acoustique d'une salle.

- `training/english_defense/questions_slow.wav` : 2 min 42, questions a debit ralenti, quatre secondes entre elles pour noter l'intention.
- `training/english_defense/questions_normal.wav` : 1 min 48, memes questions a debit normal, deux secondes entre elles.
- `training/english_defense/answers_normal.wav` : 5 min 47, questions puis exemples de reponses.

Les pauses ne suffisent pas a une reponse complete : mets la lecture en pause apres chaque question.

Premier passage : note seulement le sujet en francais, sans transcript.

Deuxieme passage : note les mots anglais reconnus et l'intention : definition, choix, preuve, limite ou suite.

Troisieme passage : dis une reponse anglaise en deux ou trois phrases, puis compare avec le texte.

Quatrieme passage : ecoute la reponse, mets en pause et reformule-la sans copier exactement les mots.

Ensuite, fais lire les variantes de la section 9 par une autre personne ou demande une simulation orale. Il faut changer l'ordre et les formulations : connaitre la piste audio par coeur n'est pas comprendre une nouvelle question.

Exercice de clarification : demande volontairement "Are you asking about... ?" sur une question ambigue, puis reponds seulement apres confirmation.

## 15. Programme propose sur quatorze jours

Hypothese de travail : 40 a 50 minutes par jour. Ce programme structure la pratique ; il ne garantit pas un niveau en quatorze jours. Si tu as moins de temps, reduis le nombre de notions par jour et conserve les repetitions.

| Jour | Comprendre | Ecouter et parler | Trace a conserver |
|---|---|---|---|
| 1 | probleme et Topic 2 | introduction courte | enregistrement initial d'une minute |
| 2 | audio, modele, transcript | definir cinq termes | cinq cartes bilingues |
| 3 | dataset, 24/12/36/468 | questions 2 et 3 | explication des nombres sans notes |
| 4 | WER, CER, RTF | questions 4 et 14 | exemple de WER calcule puis explique |
| 5 | bruit apparie | question 5, plusieurs formulations | reponse avec chiffre et limite |
| 6 | prompting et LoRA | questions 6, 11 et 18 | expliquer le gain incertain |
| 7 | limites et diarisation | questions 7, 10 et 19 | presentation de trois minutes |
| 8 | latence historique et etendue | questions 8 et 9 | distinguer timer serveur et navigateur |
| 9 | code et donnees | commenter trois fonctions | input, operation, output, limitation |
| 10 | lire introduction et methode | questions au hasard | fiche de six paragraphes difficiles |
| 11 | lire resultats et discussion | commenter deux tableaux | valeurs et unites prononcees correctement |
| 12 | contribution et suites | presentation complete chronometree | duree et trois corrections prioritaires |
| 13 | points faibles identifies | simulation avec reformulations | journal des questions mal comprises |
| 14 | revision legere des erreurs | derniere repetition avec interruptions | fiche d'une page, sans nouveau jargon |

Routine quotidienne : 10 minutes de comprehension FR/EN, 10 minutes d'ecoute, 15 minutes de reponses orales, 5 minutes de retour sur les erreurs. Revois les questions difficiles le lendemain, trois jours apres et une semaine apres.

## 16. Mesurer tes progres sans te tromper

Pour une question choisie au hasard, attribue de 0 a 2 points a chaque critere : intention comprise, exactitude scientifique, anglais comprehensible, limite pertinente, capacite a reformuler. C'est un outil personnel de progression, pas une note officielle.

Si tu comprends mais reponds difficilement : raccourcis tes phrases et repete la structure reponse/preuve/limite.

Si tu recites bien mais comprends mal : travaille des formulations nouvelles, sans regarder les reponses.

Si ton anglais est fluide mais scientifiquement faux : retourne au fichier et au calcul. La fluidite ne remplace pas la comprehension.

Critere pratique de preparation : expliquer chaque diapositive sans texte appris, identifier la demande dans une question reformulee, donner une reponse courte exacte et retrouver la preuve lorsqu'on approfondit. Demander une clarification reste parfaitement compatible avec une bonne preparation.

## 17. Fiche de secours pour le jour de la soutenance

"Could you repeat the question, please?"

"If I understood correctly, you are asking about..."

"The main point is..."

"The evidence comes from..."

"This result is limited to..."

"I did not evaluate that aspect."

"I would test it by..."

"Let me correct that statement."

Retiens les idees centrales : Topic 2 ; 24 sources, 36 fichiers, 468 transcriptions ; bruit apparie +35.3 points ; LoRA incertain ; locuteurs non valides ; latence serveur avec observations lentes ; reunions reelles encore a evaluer.
