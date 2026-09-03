# Installer et continuer le mémoire sur Mac

Guide pour reprendre le projet **ThesisMasterTest** (plateforme d'accessibilité multimodale — STT / OCR / RAG) sur un Mac, après le départ de la machine actuelle.

---

## Vue d'ensemble

Le code et le mémoire sont déjà sur GitHub : `https://github.com/LEVI226/ThesisMasterTest.git`.
Sur le Mac, il suffit de **cloner** puis de **reconstruire l'environnement**. Trois fichiers ne sont PAS dans Git et doivent être copiés depuis l'ancienne machine (voir étape 6) :

- `.env` (configuration + token Hugging Face)
- `storage/uploads/` (fichiers importés)
- `storage/chroma_db/` (base vectorielle RAG, ~232 Mo)

> Ces trois éléments sont dans l'archive de sauvegarde `thesis_backup.zip` que j'ai préparée.

---

## 1. Outils de base (une seule fois)

Installer **Homebrew** (gestionnaire de paquets Mac) si absent :

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Installer Git, Python, et les dépendances système (OCR + audio + PDF) :

```bash
brew install git python@3.12 tesseract tesseract-lang poppler ffmpeg
```

- `tesseract` + `tesseract-lang` → OCR (langues fra/eng/deu)
- `poppler` → conversion PDF→image (`pdf2image`)
- `ffmpeg` → décodage audio pour Whisper

Installer **uv** (le gestionnaire d'environnement du projet) :

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Fermez puis rouvrez le terminal après cette commande.

---

## 2. Cloner le projet

```bash
cd ~/Documents
git clone https://github.com/LEVI226/ThesisMasterTest.git
cd ThesisMasterTest
```

GitHub vous demandera de vous connecter. Le plus simple : installer **GitHub CLI** et s'authentifier une fois.

```bash
brew install gh
gh auth login
```

---

## 3. Recréer l'environnement Python

Le projet utilise `uv` avec un `uv.lock` versionné → environnement reproductible à l'identique :

```bash
uv sync
```

Cela crée `.venv/` et installe toutes les dépendances (FastAPI, Whisper, etc.).

---

## 4. Configurer le `.env`

Si vous avez restauré l'ancien `.env` (étape 6), corrigez juste la ligne Tesseract pour Mac.
Sinon, partez du modèle :

```bash
cp .env.example .env
```

Puis ouvrez `.env` et :

- mettez votre **HF_TOKEN** Hugging Face,
- laissez **TESSERACT_PATH vide** (sur Mac, Tesseract est dans le PATH — pas de chemin `C:\...`).

---

## 5. Installer Ollama (LLM local)

Le projet utilise Ollama en local pour le LLM.

```bash
brew install ollama
ollama serve        # à laisser tourner dans un terminal
ollama pull llama3.2
```

---

## 6. Restaurer les données locales (depuis l'ancienne machine)

Décompressez `thesis_backup.zip` à la racine du projet pour replacer `.env`, `storage/uploads/` et `storage/chroma_db/` :

```bash
cd ~/Documents/ThesisMasterTest
unzip ~/Downloads/thesis_backup.zip -d .
```

> Si vous ne restaurez pas `chroma_db`, la base vectorielle RAG sera vide : il faudra ré-importer les documents pour la reconstruire.

---

## 7. Lancer le serveur

```bash
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

L'API tourne ensuite sur `http://localhost:8000`.

---

## 8. Voir le code « sous les yeux »

Pour éditer le code et le mémoire confortablement :

```bash
brew install --cask visual-studio-code
code ~/Documents/ThesisMasterTest
```

VS Code ouvre tout le projet (backend, frontend, mémoire) dans une seule fenêtre.
Le mémoire est dans `Topic2_Thesis_Rewrite.md` et `Topic2_Thesis_Final.docx`.

---

## Vérification rapide (tout fonctionne ?)

```bash
uv run pytest -q          # lance les tests
ollama list               # llama3.2 présent ?
tesseract --version       # OCR OK ?
ffmpeg -version | head -1 # audio OK ?
```

---

## Workflow quotidien après installation

```bash
cd ~/Documents/ThesisMasterTest
git pull                  # récupérer les derniers changements
# ... travailler ...
git add -A && git commit -m "mon message"
git push                  # sauvegarder sur GitHub
```

Pensez à **committer + pousser** à chaque fin de session : c'est votre sauvegarde permanente.
