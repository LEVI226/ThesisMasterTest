# Mon projet STT « pour les nuls » — du zéro à la maîtrise

> Manuel pédagogique progressif du projet **Nestlé AI Accessibility Platform — Topic 2 (Speech-to-Text)**.
> Objectif : comprendre **chaque** brique, de l'électron dans le CPU jusqu'à la phrase transcrite, pour pouvoir défendre ton mémoire du bout des doigts.
> Chaque notion est expliquée d'abord en langage simple (analogie), puis reliée à **ton** code et **tes** résultats.

---

## Table des matières

1. [Vue d'ensemble : que fait ton projet, en une page](#1)
2. [Les fondations informatiques : CPU, GPU, RAM, bits](#2)
3. [Quantification : int8 vs float16 (le cœur de ton choix CPU/GPU)](#3)
4. [Programmation : Python, synchrone vs asynchrone](#4)
5. [Les maths utiles : vecteurs, distance d'édition, probabilités, décibels](#5)
6. [IA, Machine Learning, Deep Learning : la hiérarchie](#6)
7. [Le Transformer et le décodage autorégressif](#7)
8. [Speech-to-Text en profondeur : Whisper et ta pipeline](#8)
9. [Les métriques : WER, CER, RTF](#9)
10. [RAG et LLM : ChromaDB cherche, Ollama génère](#10)
11. [API et systèmes : REST, WebSocket, FastAPI](#11)
12. [Administration : uv, venv, CUDA, Ollama, git](#12)
13. [Le parcours complet d'une requête, bout à bout](#13)
14. [Glossaire express](#14)

---

<a name="1"></a>
## 1. Vue d'ensemble : que fait ton projet, en une page

**Le problème.** Dans une réunion d'entreprise multinationale comme Nestlé, les gens parlent plusieurs langues (français, anglais, allemand), avec du bruit de fond, des accents, et du vocabulaire propre à l'entreprise (Nescafé, Maggi…). Pour un employé **malentendant**, un sous-titrage écrit et fiable est souvent le **seul** moyen de suivre. Les systèmes de reconnaissance vocale grand public se dégradent précisément dans ces conditions.

**Ta réponse.** Tu construis et tu **évalues honnêtement** une chaîne de transcription automatique (ASR = *Automatic Speech Recognition*) basée sur un modèle ouvert (**Whisper** d'OpenAI, via l'implémentation optimisée **faster-whisper**). Tu ne te contentes pas de dire « ça marche » : tu **mesures** la précision (WER/CER) et la vitesse (RTF) dans 5 conditions différentes, sur 180 transcriptions, et tu rapportes ce que tu trouves — y compris quand ça contredit tes attentes.

**Les trois sujets de la plateforme globale :**

- **Topic 1 — OCR** (lire du texte dans des images/PDF) — autre étudiant.
- **Topic 2 — STT** (transformer la parole en texte) — **toi**.
- **Topic 3 — Accessibilité / RAG** (poser des questions sur le contenu transcrit) — commun.

**Ta pipeline en une phrase :**

```
Audio → [Réduction de bruit] → [Whisper STT] → texte → [ChromaDB] → [Llama 3.2] → Questions/Réponses
```

**Les 4 questions de recherche que tu poses :**
1. La réduction de bruit aide-t-elle vraiment, et à quel prix ?
2. Injecter le vocabulaire Nestlé dans le modèle réduit-il les erreurs ?
3. La détection automatique de langue est-elle fiable ?
4. Quel est le compromis vitesse/précision selon la taille du modèle ?

Garde cette page en tête : tout le reste du manuel sert à comprendre **comment** chacune de ces briques fonctionne.

---

<a name="2"></a>
## 2. Les fondations informatiques : CPU, GPU, RAM, bits

### Le bit, l'octet
Un **bit** est la plus petite unité d'information : 0 ou 1. Huit bits = un **octet** (*byte*). Tout, dans ton projet — un son, un mot, un poids de modèle — finit en suites de bits.

### Le CPU (processeur central)
Le **CPU** (*Central Processing Unit*) est le « cerveau généraliste » de l'ordinateur. Il exécute les instructions une (ou quelques-unes) à la fois, mais très vite, et il est excellent pour les tâches **séquentielles** et la logique (gérer un serveur, lire un fichier, faire tourner ton FastAPI).

Analogie : un **chef cuisinier expert** qui fait chaque plat parfaitement, l'un après l'autre.

### Le GPU (processeur graphique)
Le **GPU** (*Graphics Processing Unit*) a des milliers de petits cœurs qui font la **même** opération sur des **milliers** de données **en parallèle**. C'est nul pour la logique compliquée, mais parfait pour les **maths matricielles massives** — exactement ce qu'un réseau de neurones fait à chaque inférence.

Analogie : une **armée de 5000 commis** qui épluchent chacun une patate en même temps. Pour éplucher 5000 patates, l'armée écrase le chef solitaire.

**Dans ton projet :** Whisper est un réseau de neurones = beaucoup de multiplications de matrices. Sur **GPU** il tourne bien plus vite. C'est exactement ce que tu as mesuré : ton RTF passe de 0.323 (CPU) à 0.143 (GPU) sur le modèle `tiny`, et 0.635 → 0.188 sur `base` (×3.4). Le log de démarrage le confirme : `Loading faster-whisper model: small on CUDA (float16)`.

### La RAM et la VRAM
La **RAM** est la mémoire de travail rapide du CPU (les données « en cours d'usage »). La **VRAM** est la mémoire dédiée du GPU. Un modèle doit **tenir** en mémoire pour tourner : c'est pour ça que la taille du modèle compte (`tiny` ≈ 75 M paramètres, `small` ≈ 244 M, etc.).

### CUDA
**CUDA** est la technologie de NVIDIA qui permet à du code (comme PyTorch) d'utiliser le GPU. Si CUDA n'est pas détecté (driver manquant, mauvaise version de PyTorch), ton code **retombe sur le CPU**. Ton `engine.py` gère ça automatiquement :

```python
device = "cuda" if torch.cuda.is_available() else "cpu"
```

C'est la ligne exacte qui décide si tu tournes sur l'armée de commis ou sur le chef solitaire.

---

<a name="3"></a>
## 3. Quantification : int8 vs float16 (le cœur de ton choix CPU/GPU)

C'est **la** notion technique la plus susceptible de te valoir une question de jury. Maîtrise-la.

### Le problème
Un réseau de neurones, c'est des millions de **poids** : des nombres. Par défaut, ils sont stockés en **float32** (nombres à virgule, 32 bits chacun). C'est précis mais lourd et lent.

### La quantification
**Quantifier**, c'est représenter ces nombres sur **moins de bits** pour gagner en mémoire et en vitesse, au prix d'une petite perte de précision.

- **float16** (16 bits) : moitié moins lourd que float32, quasi sans perte. Les **GPU** ont des « Tensor Cores » qui calculent le float16 nativement à pleine vitesse. → C'est ce que tu utilises sur **GPU**.
- **int8** (entiers 8 bits) : ÷4 en mémoire vs float32. Les **CPU** modernes ont des instructions (AVX2/AVX-512) optimisées pour l'arithmétique entière, donc int8 est **plus rapide que le float sur CPU**. → C'est ce que tu utilises sur **CPU**.

Ton code choisit automatiquement :

```python
compute_type = "float16" if device == "cuda" else "int8"
```

### La conséquence subtile (à connaître absolument)
int8 et float16 sont **deux approximations différentes** des mêmes poids. Elles produisent des nombres légèrement différents à chaque étape de calcul. Comme Whisper génère son texte token par token en se basant sur l'étape précédente (décodage autorégressif, §7), une minuscule différence peut faire **diverger** toute la phrase.

C'est pourquoi, quand tu as rejoué l'évaluation sur GPU, **52 transcriptions sur 180 ont changé** légèrement vs CPU. Ce n'est **pas un bug** : « déterministe » veut dire reproductible **pour un même couple (matériel, type de calcul)**, pas entre CPU/int8 et GPU/float16. C'est exactement la raison pour laquelle tu as gardé le run CPU comme référence canonique de ta thèse et le run GPU à part.

---

<a name="4"></a>
## 4. Programmation : Python, synchrone vs asynchrone

### Pourquoi Python
Python est lisible et possède l'écosystème IA le plus riche (PyTorch, faster-whisper, FastAPI…). Ton projet est presque entièrement en Python.

### Synchrone vs asynchrone (notion clé pour ton API)
- **Synchrone** : on fait une chose, on attend qu'elle finisse, puis la suivante. Si une tâche prend 5 secondes, tout est bloqué 5 secondes.
- **Asynchrone** : pendant qu'une tâche « attend » (réseau, disque), le programme fait autre chose. C'est géré par une **boucle d'événements** (`asyncio`).

**FastAPI** (ton serveur) est asynchrone : un seul thread alterne entre toutes les requêtes. Problème : transcrire avec Whisper est une tâche **bloquante** (calcul pur de plusieurs secondes, qui ne « rend pas la main »). Si tu l'appelais directement, **tout le serveur gèlerait** pendant la transcription.

La solution dans ton `main.py` :

```python
result = await loop.run_in_executor(None, lambda: transcribe_file(...))
```

`run_in_executor` envoie le calcul lourd dans un **pool de threads séparé**, pour que la boucle asyncio reste libre de traiter `/health`, `/ask`, etc. C'est une réponse de jury fréquente : *« pourquoi `run_in_executor` ? Pour ne jamais bloquer la boucle d'événements. »*

### Dataclass
Ton `TranscribeConfig` est une **dataclass** : une classe Python qui regroupe proprement des options de configuration (taille du modèle, langue, preprocessing…) au lieu de les éparpiller en arguments. Ça centralise et documente les réglages.

---

<a name="5"></a>
## 5. Les maths utiles : vecteurs, distance d'édition, probabilités, décibels

Pas besoin d'être mathématicien. Tu as besoin de **quatre** idées.

### A. Le vecteur et la similarité (pour le RAG)
Un **vecteur** est une liste de nombres, par exemple `[0.12, -0.88, 0.43, …]`. En IA, on transforme un texte en vecteur appelé **embedding** : deux textes au sens proche donnent deux vecteurs **proches dans l'espace**. La « proximité » se mesure souvent par la **similarité cosinus** (l'angle entre deux vecteurs).

Pourquoi tu en as besoin : ChromaDB (ta base RAG) retrouve les passages pertinents en comparant l'embedding de la question à ceux des passages stockés. Ton modèle d'embedding est `intfloat/multilingual-e5-small` (visible dans tes logs de démarrage).

### B. La distance d'édition de Levenshtein (pour le WER/CER)
C'est le **cœur mathématique de ton évaluation**. La distance de Levenshtein entre deux séquences = le **nombre minimum d'opérations** (substitution, suppression, insertion) pour transformer l'une en l'autre.

On la calcule avec une **matrice de programmation dynamique** (algorithme de **Wagner-Fischer**). Ton `metrics.py` la code à la main :

- On remplit une matrice `dp` où `dp[i][j]` = coût pour transformer les `i` premiers éléments de la référence en les `j` premiers de l'hypothèse.
- Cas de base : `dp[i][0] = i` (il faut `i` **suppressions** pour vider la référence) et `dp[0][j] = j` (il faut `j` **insertions** pour partir de rien).
- Puis on **remonte** la matrice (*backtracking*) pour compter séparément S (substitutions), D (suppressions), I (insertions).

Exemple concret : référence `"the meeting starts at nine"` (5 mots), hypothèse `"the meeting start at nine a m"` (7 mots) → 1 substitution (starts→start) + 2 insertions (a, m) → **WER = 3/5 = 0.60**.

### C. Logits et probabilités (pour comprendre les hallucinations)
À chaque étape, un modèle de langage produit des **logits** : un score brut pour chaque mot/token possible. On les transforme en **probabilités** (fonction *softmax*), et on choisit le token le plus probable.

Quand l'audio est de **mauvaise qualité**, ces scores sont « plats » (le modèle est peu sûr). Il se rabat alors sur ce qu'il « connaît » d'autre — par exemple le **prompt** que tu lui as injecté. C'est le mécanisme de l'hallucination « Nestlé Ghana » que tu as documentée.

### D. Le décibel et le SNR (pour la condition bruitée)
Le **SNR** (*Signal-to-Noise Ratio*, rapport signal/bruit) mesure, en **décibels (dB)**, combien le signal utile (la voix) domine le bruit. Plus le SNR est **bas**, plus c'est bruité. Tu as généré tes clips « noisy » en ajoutant du bruit blanc à **8 dB de SNR** — un niveau délibérément difficile. Le décibel est une échelle **logarithmique** : chaque +10 dB ≈ ×10 en puissance.

---

<a name="6"></a>
## 6. IA, Machine Learning, Deep Learning : la hiérarchie

Ces mots sont souvent confondus. Range-les comme des poupées russes :

- **Intelligence Artificielle (IA)** : le grand domaine — faire faire à une machine des tâches « intelligentes ».
- **Machine Learning (ML)** : un sous-ensemble — au lieu de programmer des règles à la main, on **apprend** des règles à partir de **données** et d'exemples.
- **Deep Learning (DL)** : un sous-ensemble du ML qui utilise des **réseaux de neurones** profonds (beaucoup de couches). Whisper en fait partie.

### Le réseau de neurones, simplement
C'est une fonction mathématique géante avec des millions de **paramètres** (les poids). On lui montre des exemples (audio → texte correct), et un algorithme (la *descente de gradient*) **ajuste les poids** pour réduire l'erreur. Après l'entraînement, les poids sont figés.

### Entraînement vs inférence (distinction cruciale)
- **Entraînement (*training*)** : la phase coûteuse (GPU, des jours/semaines) où le modèle apprend ses poids. **Tu ne fais PAS ça** — tu utilises un Whisper déjà entraîné.
- **Inférence (*inference*)** : utiliser le modèle entraîné pour faire une prédiction (transcrire un fichier). **C'est ce que ton projet fait.**

À dire au jury : *« Je ne ré-entraîne pas Whisper ; j'évalue et j'optimise son inférence avec des techniques ouvertes (preprocessing, prompting, forçage de langue). »*

### Supervision faible (*weak supervision*)
Whisper a été entraîné sur **680 000 heures** d'audio collecté sur le web avec des transcriptions imparfaites. Cette « supervision faible » lui donne une large couverture multilingue et une robustesse aux accents — mais son entraînement ne couvre pas spécifiquement les réunions d'entreprise ni le vocabulaire Nestlé. C'est **la** justification de fond de ton sujet.

---

<a name="7"></a>
## 7. Le Transformer et le décodage autorégressif

### L'architecture Transformer
Le **Transformer** (2017) est l'architecture derrière presque toute l'IA moderne (Whisper, GPT, Llama…). Son idée clé est l'**attention** : pour traiter un élément, le modèle « regarde » et pondère tous les autres éléments du contexte pour décider lesquels sont pertinents.

### Encoder-Decoder (le schéma de Whisper)
Whisper est un modèle **encoder-decoder** :
- L'**encodeur** lit l'audio (transformé en spectrogramme, une image du son) et le résume en représentations internes.
- Le **décodeur** génère le texte, **un token à la fois**, en regardant à la fois l'audio encodé et les tokens déjà produits.

Un **token** est un morceau de mot (parfois un mot entier, parfois une syllabe). Le modèle ne pense pas en lettres mais en tokens.

### Le décodage autorégressif (à maîtriser absolument)
« Autorégressif » = chaque token généré **dépend des précédents**. Le décodeur produit le token 1, puis utilise [audio + token 1] pour produire le token 2, puis [audio + tokens 1-2] pour le token 3, etc.

Deux conséquences capitales pour ta thèse :

1. **L'effet boule de neige (hallucination).** Si le modèle se trompe sur un token (surtout sur audio bruité), cette erreur devient le contexte du token suivant, qui peut dériver davantage. Sur tes clips français bruités, ça produit des sorties absurdes (cyrillique, turc…) ou des répétitions en boucle. L'option `condition_on_previous_text=True` de ton code **alimente** ce mécanisme : elle améliore la cohérence sur audio propre mais aggrave la dérive sur audio difficile.

2. **Pourquoi int8 ≠ float16.** Comme le token N dépend du N-1, une différence numérique minuscule (due à la quantification) au token 3 peut faire bifurquer toute la suite. D'où tes 52 transcriptions divergentes entre CPU et GPU.

---

<a name="8"></a>
## 8. Speech-to-Text en profondeur : Whisper et ta pipeline

### Qu'est-ce que l'ASR / STT
**ASR** (*Automatic Speech Recognition*) = **STT** (*Speech-to-Text*) : transformer un signal audio de parole en texte écrit. C'est le cœur de ton Topic 2.

### De l'audio au spectrogramme
Le son est une onde. On le découpe en petites fenêtres temporelles et, pour chacune, on calcule quelles **fréquences** sont présentes (transformée de Fourier). On obtient un **spectrogramme** : une image 2D (temps × fréquence) que l'encodeur de Whisper sait lire. L'audio est rééchantillonné à **16 kHz mono** (16 000 mesures/seconde, un seul canal) — un standard pour l'ASR.

### Whisper et faster-whisper
- **Whisper** est le modèle d'OpenAI (encoder-decoder Transformer).
- **faster-whisper** est une ré-implémentation optimisée via **CTranslate2** : même modèle, mais plus rapide et plus léger en mémoire, avec support natif de la quantification int8/float16. C'est **ce que tu utilises**.
- Les **tailles** de modèle vont de `tiny` (rapide, moins précis) à `large` (lent, très précis). Tu compares `tiny` et `base` : passer de l'un à l'autre est ton plus gros gain de précision (Condition F, WER 48.4 % vs 62.2 %).

### Les briques de ta pipeline (fichier `backend/stt/engine.py`)

**1. Réduction de bruit — `preprocess_audio()`**
Utilise la bibliothèque `noisereduce` : c'est du **spectral gating**. Le principe : estimer le profil de bruit (les fréquences présentes même quand personne ne parle), puis **atténuer** les fréquences qui ne dépassent pas ce profil d'un certain seuil (`prop_decrease=0.75` dans ton code).
- Effet mesuré : sur audio **bruité**, WER 96.4 % → 88.1 % (ça aide). Sur audio **propre**, 47.0 % → 49.2 % (léger coût, car le filtre rabote aussi des consonnes faibles comme s, f, ch). → C'est un **compromis**, pas un gain gratuit (ta conclusion H1).

**2. Le prompt de domaine — `DEFAULT_DOMAIN_PROMPT`**
On injecte une phrase de vocabulaire Nestlé (`"Nestlé, Nespresso, Maggi, Purina, KitKat, Nescafé, supply chain, plant-based portfolio, Nestlé Ghana"`) dans le décodeur via `initial_prompt`. L'idée : biaiser le modèle vers ces termes. Mais comme ton dataset (MInDS-14) **ne contient pas** ce vocabulaire, tu n'as pu mesurer que son **coût** (légère dégradation + une hallucination « Nestlé Ghana »), pas son bénéfice. → H2 non testable.

**3. La détection / le forçage de langue**
Whisper peut **deviner** la langue (auto) ou on peut la **forcer** (`language="fr"`). Ton résultat phare (H4) : la détection auto échoue souvent sur audio court/bruité non-anglais (42 % des clips FR !), produisant parfois du mauvais script (cyrillique…). Forcer la langue récupère un texte lisible, à coût zéro. **C'est ton finding le plus solide.**

**4. Le VAD — `load_vad_model()` (Silero)**
Le **VAD** (*Voice Activity Detection*) détecte **où** il y a de la parole vs du silence/bruit, pour ne transcrire que les segments utiles (économie de calcul + moins d'hallucinations sur le silence). **Point d'honnêteté de ta thèse** : le VAD est chargé mais **jamais appelé** dans le chemin batch `transcribe_file()` ; il n'est utilisé que dans le chemin temps réel (WebSocket). Tu le documentes comme un *gap*, ce qui est de la rigueur scientifique, pas un échec.

**5. La diarisation — pyannote**
La **diarisation** répond à « **qui** parle quand » (Speaker 1, Speaker 2…). Tu utilises `pyannote`. Elle n'a pas été évaluée dans le pilote car ton dataset est mono-locuteur (téléphone bancaire) et aucun token HuggingFace n'était configuré.

### Le dataset : MInDS-14
Faute de corpus Nestlé (confidentiel, pas encore reçu) et après l'échec d'autres corpus dans ton environnement, tu as utilisé **PolyAI/MInDS-14** : de la parole téléphonique bancaire spontanée, sous licence CC-BY-4.0, en EN/FR/DE. **36 échantillons** : 24 propres + 12 bruités. Limite assumée : ce n'est ni du Nestlé, ni de la réunion multi-locuteurs.

---

<a name="9"></a>
## 9. Les métriques : WER, CER, RTF

Tu mesures trois choses. Connais leur formule et leur sens.

### WER — Word Error Rate (taux d'erreur sur les mots)
$$ \text{WER} = \frac{S + D + I}{N} $$
où S = substitutions, D = suppressions, I = insertions, N = nombre de mots de la **référence**.
- 0 = parfait. Plus c'est bas, mieux c'est.
- **Peut dépasser 100 %** : le dénominateur N est fixé par la référence, mais si le modèle **insère** beaucoup de mots faux, le numérateur peut être plus grand que N. Exemple : référence `"merci"` (N=1), hypothèse `"je vous remercie beaucoup"` → 1 substitution + 3 insertions = 4 → WER = 4/1 = **400 %**.

### CER — Character Error Rate (taux d'erreur sur les caractères)
Même formule, mais au niveau des **caractères** au lieu des mots (les espaces sont retirés).
- Plus **indulgent** sur les mots longs : `"Nescafébohnen"` vs `"Nescafébohn"` → WER = 100 % (le mot entier est faux) mais CER ≈ 15 % (seulement 2 caractères faux sur 13).
- Pertinent pour toi : les noms de marque/termes techniques sont des mots longs où une seule erreur de lettre fait exploser le WER. → Tu rapportes les **deux**.

### RTF — Real-Time Factor (facteur temps réel)
$$ \text{RTF} = \frac{\text{temps de traitement}}{\text{durée de l'audio}} $$
- RTF **< 1** = plus rapide que le temps réel (bon pour la production). RTF = 0.3 veut dire : transcrire 10 s d'audio prend 3 s.
- Toutes tes conditions sont < 1 (de 0.26 à 0.64 en CPU), ce qui valide H3. Sur GPU, c'est encore mieux (0.14–0.19).

### La normalisation (équité de la mesure)
Avant de comparer, `metrics.py` **normalise** : minuscules, suppression de la ponctuation, espaces uniformisés. Sinon `"Bonjour."` et `"bonjour"` compteraient comme une erreur, ce qui serait injuste.

---

<a name="10"></a>
## 10. RAG et LLM : ChromaDB cherche, Ollama génère

C'est le Topic 3, mais ton STT l'alimente, donc tu dois le comprendre.

### Le LLM (Large Language Model)
Un **LLM** est un gros modèle de langage (comme **Llama 3.2**, que tu fais tourner localement via **Ollama**). Il sait **une seule chose** : recevoir du texte et générer la suite la plus plausible. Il ne sait pas chercher dans une base, ni calculer.

### Le problème que le RAG résout
Un LLM seul « hallucine » s'il ne connaît pas le contenu de TES réunions. On ne va pas le ré-entraîner à chaque réunion. → On lui **fournit le contexte** au moment de la question.

### RAG = Retrieval-Augmented Generation, en deux temps
1. **Retrieval (recherche)** : on transforme la question en embedding (vecteur) et on cherche dans **ChromaDB** les passages les plus proches (similarité vectorielle). Dans ton code : `chunks = query(question, n_results=5)`. **Ollama n'intervient pas ici.**
2. **Augmented Generation (génération augmentée)** : on construit un prompt = [question + les 5 passages trouvés] et on l'envoie à **Llama 3.2**, qui rédige une réponse fondée sur ces passages. Dans ton code : `answer(question, chunks, language)`.

**Phrase de jury :** *« ChromaDB cherche, Ollama génère. Jamais l'inverse. Llama ne touche jamais la base. »*

### ChromaDB et les embeddings
**ChromaDB** est une **base de données vectorielle** : elle stocke des textes avec leur embedding et sait retrouver les plus similaires très vite. Tes transcriptions (STT) et tes OCR y sont **ingérées** par `ingest()`, découpées en **chunks** (morceaux de ~500 mots avec chevauchement) avant stockage. Le modèle d'embedding est `multilingual-e5-small`.

---

<a name="11"></a>
## 11. API et systèmes : REST, WebSocket, FastAPI

### Qu'est-ce qu'une API
Une **API** (*Application Programming Interface*) est un « contrat » qui permet à des programmes de se parler. Ton backend expose une API web : d'autres programmes (ou ton frontend) lui envoient des requêtes, il répond.

### HTTP et REST
**HTTP** est le protocole du web (requête → réponse). Une API **REST** organise ça autour de **verbes** :
- `GET` : lire (ex. `GET /health` → état du système).
- `POST` : envoyer/créer (ex. `POST /transcribe` → on envoie un fichier audio).

La réponse est en général du **JSON** (format texte structuré clé/valeur).

### Tes endpoints (fichier `backend/main.py`)
- `POST /transcribe` : upload audio → Whisper → ingestion ChromaDB → JSON (texte, segments, langue, `duration_seconds`, `processing_time_seconds`…).
- `POST /ocr` : upload PDF/image → Tesseract → ingestion.
- `POST /ask` : question → RAG → réponse Llama.
- `GET /health` : liveness check.
- `WS /ws/transcribe` : transcription **temps réel**.

### WebSocket (le temps réel)
Là où HTTP est « une question, une réponse », le **WebSocket** ouvre un **canal permanent** bidirectionnel : le navigateur envoie des morceaux d'audio en continu, le serveur renvoie le texte au fur et à mesure. C'est ton chemin « live ». Il diffère du batch : il utilise le **VAD**, **pas** de noise reduction, et hardcode `language="fr"`.

### Lifespan et le préchargement
Charger Whisper prend du temps. Ton `lifespan` précharge les modèles **au démarrage** du serveur pour éviter une latence à la première requête. Nuance honnête de ta thèse : `/health` peut répondre `"ok"` **avant** que Whisper ait fini de charger — c'est un *liveness check* (le process est vivant), pas un *readiness check* (prêt à servir).

### Swagger / OpenAPI
FastAPI génère automatiquement une page de documentation interactive à `/docs` (Swagger). Tu peux y tester `POST /transcribe` en uploadant un `.wav` et voir le JSON renvoyé — pratique pour les démos de soutenance.

---

<a name="12"></a>
## 12. Administration : uv, venv, CUDA, Ollama, git

### Environnement virtuel et `uv`
Un **environnement virtuel** (`.venv`) isole les bibliothèques de ton projet pour ne pas polluer le système. **`uv`** est l'outil moderne qui gère ça : `uv sync` installe les dépendances listées dans `pyproject.toml`, `uv run …` exécute une commande dans l'environnement. `uv.lock` fige les versions **exactes** pour la reproductibilité.

### `pyproject.toml`
Le fichier qui déclare **ce dont ton app a besoin** : fastapi, uvicorn, faster-whisper, noisereduce, chromadb, etc. Garde-le honnête (n'y laisse pas de libs temporaires) — un jury peut le regarder.

### Variables d'environnement et `.env`
Les réglages sensibles ou variables (modèle Whisper, URL d'Ollama, `HF_TOKEN`…) vivent dans `.env`, **non versionné** (dans `.gitignore`) pour ne pas exposer de secret. Ton code les lit via `os.getenv(...)`.

### Ollama
**Ollama** fait tourner des LLM **localement** (sans cloud). `ollama run llama3.2` lance le modèle ; ton backend lui parle en HTTP sur `localhost:11434`. Avantage : **privé**, gratuit, hors-ligne — important pour des données de réunion confidentielles.

### CUDA / drivers
Pour utiliser le GPU, il faut : un GPU NVIDIA + ses **drivers** + une version de **PyTorch compilée pour CUDA** (la tienne : `2.6.0+cu124`, soit CUDA 12.4). Si un maillon manque, `torch.cuda.is_available()` renvoie `False` et tu retombes sur CPU. (Le warning `torchcodec` que tu as vu est bénin : pyannote utilise un autre décodeur audio.)

### Git : ton journal de recherche
**Git** versionne ton code : chaque **commit** est une photo datée avec un message. Un historique de commits atomiques et bien nommés **est** ton journal de bord de recherche — la preuve, pour un directeur de mémoire, que le travail s'est construit dans le temps. Tes 5 commits (`fix(stt)…`, `docs(these)…`, etc.) en sont l'exemple.

---

<a name="13"></a>
## 13. Le parcours complet d'une requête, bout à bout

Suis une transcription, de l'upload au texte ingéré. Si tu sais raconter ça, tu maîtrises ton projet.

1. **Upload.** Un client envoie un `.wav` à `POST /transcribe`. FastAPI vérifie l'extension contre une liste blanche, génère un identifiant unique (`uuid4`), et sauve le fichier dans `storage/uploads/`.
2. **Délégation.** Comme transcrire est bloquant, l'appel part dans un thread via `run_in_executor` pour ne pas geler le serveur.
3. **Preprocessing (optionnel).** `preprocess_audio()` rééchantillonne en 16 kHz mono et applique le spectral gating `noisereduce`.
4. **Inférence Whisper.** Le modèle (chargé en cache, en float16 sur ton GPU) lit le spectrogramme via l'encodeur, puis le décodeur génère le texte token par token (autorégressif). Selon la config : langue forcée ou auto, prompt de domaine ou non.
5. **Assemblage.** On concatène le texte, on calcule la vraie durée audio (`get_audio_duration`) et le temps de traitement, on liste les segments horodatés.
6. **Diarisation (si activée).** pyannote attribue un locuteur à chaque segment par chevauchement temporel.
7. **Ingestion RAG.** `ingest()` découpe le texte en chunks et les stocke dans ChromaDB avec leurs embeddings.
8. **Réponse JSON.** Le client reçoit : texte complet, segments, langue, `duration_seconds`, `processing_time_seconds`, modèle utilisé, nombre de chunks ingérés.

Plus tard, une question via `POST /ask` déclenche : recherche ChromaDB (retrieval) → génération Llama (augmented generation) → réponse sourcée.

---

<a name="14"></a>
## 14. Glossaire express

- **ASR / STT** : reconnaissance vocale (parole → texte).
- **Token** : morceau de mot, l'unité que manipule le modèle.
- **Embedding** : vecteur de nombres représentant le sens d'un texte.
- **Inférence** : utiliser un modèle entraîné (≠ entraînement).
- **Quantification** : réduire la précision des poids (float32 → float16/int8) pour gagner vitesse/mémoire.
- **int8 / float16** : formats quantifiés ; int8 pour CPU, float16 pour GPU.
- **Autorégressif** : chaque token dépend des précédents.
- **Transformer / attention** : l'architecture des modèles modernes.
- **Encoder-decoder** : encodeur lit l'audio, décodeur écrit le texte (Whisper).
- **VAD** : détection d'activité vocale (parole vs silence).
- **Diarisation** : qui parle quand.
- **Spectral gating** : réduction de bruit dans le domaine fréquentiel.
- **SNR (dB)** : rapport signal/bruit ; bas = bruité.
- **WER / CER / RTF** : erreur sur les mots / sur les caractères / facteur temps réel.
- **Levenshtein / Wagner-Fischer** : distance d'édition et son algorithme.
- **Logits / softmax** : scores bruts des tokens / leur conversion en probabilités.
- **RAG** : Retrieval (ChromaDB) + Augmented Generation (LLM).
- **LLM** : grand modèle de langage (Llama 3.2).
- **Embedding model** : modèle qui produit les vecteurs (multilingual-e5-small).
- **ChromaDB** : base de données vectorielle.
- **Ollama** : exécuteur de LLM en local.
- **API / REST / HTTP / JSON** : interfaces et protocoles web.
- **WebSocket** : canal temps réel bidirectionnel.
- **FastAPI / uvicorn** : framework web Python / le serveur qui le fait tourner.
- **asyncio / run_in_executor** : asynchrone / déléguer un calcul bloquant à un thread.
- **uv / venv / pyproject.toml / uv.lock** : gestion de l'environnement et des dépendances.
- **CUDA** : couche NVIDIA pour calculer sur GPU.
- **Git / commit** : versionnement / photo datée du code.

---

> **Méthode de révision conseillée.** Lis une section, ferme le manuel, et explique-la à voix haute comme si tu l'enseignais à un ami. Si tu bloques, relis ; sinon, passe à la suivante. Couple ce manuel avec `Fiche_Revision_Soutenance.md` (les chiffres) et la simulation de jury Antigravity (l'entraînement). C'est la combinaison qui te rend solide du bout des doigts.

