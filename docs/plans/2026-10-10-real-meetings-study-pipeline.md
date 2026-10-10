# Real-Meetings Validation Study: Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and run the pre-registered real-meetings validation study (data → transcription → scoring → statistics → LaTeX tables) that answers H1–H5 and D1 of the spec. This covers weeks 1–2.

**Architecture:** A small Python package, `study_real_meetings/`, sits next to `backend/`. It reuses the audited scorer (`backend/evaluation/metrics.py`). Every audio source becomes JSONL manifests of 16 kHz segments. One runner applies a condition (noise, language forcing, prompt, denoising) and a transcriber to each segment, then appends one provenance-rich row per (segment × system × condition) to a single resumable CSV. Analysis reads only that CSV.

**Tech Stack:** Python 3.11 (`.venv`), faster-whisper 1.2.1 / CTranslate2 4.6.0, transformers 5.3 + peft, NeMo 3.0, pyannote.audio 4.0.4 + pyannote.metrics, pyarrow, soundfile, librosa, noisereduce, num2words, matplotlib, ffmpeg, pytest.

**Spec:** `docs/specs/2026-10-10-real-meetings-study-design.md` (read it first).

## Global Constraints

- **Branch:** `study/real-meetings`. Never commit to `main`. Tag `defense-baseline` must stay untouched.
- **Python:** always run as `.venv\Scripts\python.exe` from the repo root `C:\Users\ulric\Documents\ThesisMasterTest`. **Never** run `uv sync` or `uv run`: they would re-resolve the pinned CUDA stack (torch 2.6.0+cu124, CTranslate2 4.6.0, lightning 2.4.0).
- **Scorer:** WER/CER must go through `normalize_text` and `_levenshtein` from `backend/evaluation/metrics.py`. Do not modify `metrics.py` or `statistics.py`.
- **Private audio:** `audioReunionréel/` (private meetings, no consent) is never read, copied, transcribed or committed by any task.
- **Large data:** everything under `datasets/real_meetings/` is git-ignored. Only code, `PROTOCOL.md`, `manifests.sha256` and results CSVs are committed.
- **Seed:** `20261010` everywhere.
- **Decoding:** deterministic. Whisper: `beam_size=5`, `temperature=[0.0]`, `condition_on_previous_text=False`, `vad_filter=False`. CTC: greedy argmax.
- **Splits:** the first 180 s of each source cluster is `dev`; the rest is `test`. Tuning uses `dev` only. All reported results use `test`.
- **Commit messages** end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. On Windows PowerShell 5.1, write the message to a file with the Write tool (UTF-8, no BOM) and use `git commit -F <file>`.

### Deviations from the spec decided while planning (record them in PROTOCOL.md in Task 9)

1. **D1 (diarization) runs on SUMM-RE, not AMI.** The Hugging Face AMI release has only cut-up utterances, with no full-meeting audio. SUMM-RE has one channel per participant plus word timings, so we can sum the channels into a meeting mix and derive exact speaker turns.
2. **H5 (streaming) runs on AGM only, in 3 languages.** It needs long continuous audio with a reference, and AMI-HF has none.
3. **Noise corpus: DEMAND** (meeting room OMEETING, office OOFFICE, cafeteria PCAFETER; Zenodo record 1227121, CC BY 4.0) instead of MUSAN. DEMAND has an actual meeting-room recording, and it is about 280 MB instead of 11 GB.
4. **D1 is reported per meeting, without a confidence interval.** With 3 meetings a bootstrap interval is meaningless, so DER stays descriptive.
5. **Optional sources** (Senate hearing, investor call, YouTube auto-captions) are left out of this plan. They are added only if weeks 1–2 finish early, through a follow-up plan.

---

## File Structure

```
study_real_meetings/
├── __init__.py
├── PROTOCOL.md                 # Task 9: frozen before any test-set run
├── manifests.sha256            # Task 9: checksums of the frozen manifests
├── config.py                   # all fixed parameters (paths, seeds, meetings, terms, SNRs)
├── text.py                     # normalisation extras, error counts, term recall, repetition loops
├── srt.py                      # SRT parsing → Unit
├── manifest.py                 # Unit, Segment, merge_units, split_for, JSONL I/O
├── audio.py                    # ffmpeg conversion, segment loading, wav writing
├── noise.py                    # DEMAND bank, deterministic noise pick, SNR mixing
├── sources/
│   ├── __init__.py
│   ├── agm.py                  # AGM captions + audio → segments; caption checks
│   ├── ami.py                  # AMI parquet rows → segments + wav files
│   └── summre.py               # SUMM-RE token tiers → segments, speaker regions, mixes
├── transcribers.py             # FasterWhisper / HFWhisper(+LoRA) / MMS / NeMo adapters + factory
├── runner.py                   # Condition, prepare_audio, run(), provenance, CSV schema
├── plans.py                    # Job definitions for H1–H4d + NOISE
├── streaming.py                # H5 chunked streaming simulation
├── diarization.py              # D1: regions, RTTM, DER
├── stats.py                    # corpus WER, clustered paired/unpaired bootstrap, Holm
├── analysis.py                 # summary tables, primary tests, LaTeX, figure
└── scripts/
    ├── __init__.py
    ├── build_data.py           # downloads + conversion + manifests (all sources)
    ├── reference_checks.py     # spot-check sheet (FR/EN) + automatic DE caption checks
    ├── run_experiments.py      # --plan H1|H2|H3|H4a|H4b|H4c|H4d|NOISE|ALL
    ├── run_streaming.py        # H5
    ├── run_diarization.py      # D1
    └── analyse.py              # writes results/real_meetings/*.csv + LaTeX + figure
tests/
├── test_rm_text.py
├── test_rm_manifest.py
├── test_rm_audio_noise.py
├── test_rm_sources.py
├── test_rm_runner.py
├── test_rm_stats.py
├── test_rm_plans.py
├── test_rm_streaming.py
├── test_rm_diarization.py
└── test_rm_analysis.py
results/real_meetings/          # runs.csv, streaming.csv, diarization.csv, summary.csv, primary.csv
Memoire_LaTeX/generated/        # real_meetings_*.tex tables + figure (input by week-3 writing)
```

---

### Task 1: Day-1 setup (supervisor message, documentation entries, environment)

**Files:**
- Create: `docs/Message_Superviseur_real_meetings.md`
- Create: `study_real_meetings/__init__.py`, `study_real_meetings/sources/__init__.py`, `study_real_meetings/scripts/__init__.py` (empty)
- Modify: `.gitignore` (append)
- Modify: `pyproject.toml` (`[tool.pytest.ini_options]`; dependencies)
- Modify: `ETAT_ACTUEL.md` (append §5)
- Modify: `CHANGELOG.md` (append Phase 4)

**Interfaces:**
- Produces: importable package `study_real_meetings`; pytest can import it (`pythonpath = ["."]`); `num2words` installed.

- [ ] **Step 1: Write the supervisor message draft**

Create `docs/Message_Superviseur_real_meetings.md`:

```markdown
# Draft: message to Dr.-Ing. NIKIEMA (to adapt and send yourself)

Objet : Proposition d'une validation complémentaire sur réunions réelles (Topic 2)

Bonjour Docteur,

En relisant mon mémoire avant la soutenance, j'ai identifié une limite que le jury pourrait relever :
mon jeu canonique (MInDS-14) est de la parole téléphonique mono-locuteur, alors que le sujet porte
sur des réunions multilingues et bruitées.

Je propose d'ajouter, sans rien modifier aux résultats existants, une courte étude de validation
externe sur des données publiques de réunions réelles :
- AMI (réunions anglaises, micros proches et lointains),
- SUMM-RE (réunions françaises, transcriptions de référence humaines),
- l'AGM Nestlé 2026 en allemand, anglais et français (sous-titres publiés par Nestlé),
avec un bruit réaliste (salle de réunion, bureau, cafétéria) et un protocole fixé à l'avance.

La version actuelle est figée (tag git `defense-baseline`). L'étude serait ajoutée comme une
section séparée, prête dans environ trois semaines ; si elle n'est pas concluante à temps, elle
sera présentée comme travail en cours.

Êtes-vous d'accord avec cet ajout ?

Cordialement,
OUEDRAOGO Yannick Ulrich Levi
```

- [ ] **Step 2: Ignore the study's data folder**

Append to `.gitignore`:

```
# Real-meetings study: downloaded/converted audio (regenerable via study_real_meetings/scripts/build_data.py)
datasets/real_meetings/
```

- [ ] **Step 3: Make the package importable in tests**

In `pyproject.toml`, replace the `[tool.pytest.ini_options]` block with:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
cache_dir = "tmp/pytest_cache"
pythonpath = ["."]
markers = ["gpu: needs CUDA and downloaded models (run with -m gpu)"]
addopts = "-m 'not gpu'"
```

Create the three empty `__init__.py` files listed above.

- [ ] **Step 4: Install num2words without touching the pinned stack**

```powershell
uv add --no-sync "num2words>=0.5.13"
uv pip install --python .venv\Scripts\python.exe "num2words>=0.5.13"
.venv\Scripts\python.exe -c "from num2words import num2words; print(num2words(160, lang='fr'))"
```

Expected: `cent soixante`. Then confirm the pinned stack is unchanged:

```powershell
.venv\Scripts\python.exe -c "import torch, ctranslate2; print(torch.__version__, ctranslate2.__version__)"
```

Expected: `2.6.0+cu124 4.6.0`.

- [ ] **Step 5: Declare the study in the source-of-truth documents**

Append to `ETAT_ACTUEL.md`:

```markdown
---

## 5. Étude complémentaire « réunions réelles » (branche `study/real-meetings`, ouverte le 10/10/2026)

- **Statut :** en cours. Jeu de validation EXTERNE distinct, déclaré ici pour ne pas être confondu
  avec un pipeline parallèle égaré. Il ne remplace PAS le jeu canonique MInDS-14 (§2).
- **Spec :** `docs/specs/2026-10-10-real-meetings-study-design.md` ; **plan :** `docs/plans/2026-10-10-real-meetings-study-pipeline.md`.
- **Données :** AGM Nestlé 2026 (DE/EN/FR, sous-titres Nestlé), AMI (EN), SUMM-RE (FR), bruit DEMAND.
  Les enregistrements privés de `audioReunionréel/` sont EXCLUS (pas de consentement des participants).
- **Résultats :** `results/real_meetings/` (CSV = source de vérité, comme pour le reste du mémoire).
```

Append to `CHANGELOG.md`:

```markdown

## Phase 4 — Étude de validation sur réunions réelles (octobre 2026)

**2026-10-10** — Instantané de l'état soutenable : commit `9054422`, tag `defense-baseline`.
`.gitignore` exclut désormais l'audio privé, les sondes d'audit et `tmp/`. Ouverture de la branche
`study/real-meetings` ; spec (`53248d7`) et plan d'implémentation rédigés. Les réunions privées sont
exclues faute de consentement. → `docs/specs/`, `docs/plans/`.
```

- [ ] **Step 6: Run the existing suite to prove nothing broke**

Run: `.venv\Scripts\python.exe -m pytest -q`
Expected: all existing tests pass (the 16/09 suite reported 68 tests, 0 failures). If a pre-existing test fails, record its name and do not fix it in this task.

- [ ] **Step 7: Commit**

```powershell
git add .gitignore pyproject.toml uv.lock ETAT_ACTUEL.md CHANGELOG.md docs/Message_Superviseur_real_meetings.md study_real_meetings
git commit -F <msgfile>   # "chore(study): day-1 setup for the real-meetings study"
```

**Human action (author, day 1):** adapt and send the supervisor message. Record the answer in `CHANGELOG.md`.

---

### Task 2: Study configuration and text scoring

**Files:**
- Create: `study_real_meetings/config.py`
- Create: `study_real_meetings/text.py`
- Test: `tests/test_rm_text.py`

**Interfaces:**
- Consumes: `backend.evaluation.metrics.normalize_text(text) -> str`, `_levenshtein(ref: list, hyp: list) -> (s, d, i, n)`.
- Produces:
  - `config` constants (exact names below).
  - `normalize_tokens(text: str, language: str, *, numbers_to_words: bool = False) -> list[str]`
  - `Counts(sub: int, dele: int, ins: int, n_ref: int)` with `.errors` and `.wer`
  - `score_words(reference, hypothesis, language, *, numbers_to_words=False) -> Counts`
  - `score_chars(reference, hypothesis, language) -> Counts`
  - `term_hits(reference, hypothesis, language, terms=NESTLE_TERMS) -> tuple[int, int]` (hits, total)
  - `has_repetition_loop(hypothesis, language, n=4, min_repeats=3) -> bool`

- [ ] **Step 1: Create the configuration module**

`study_real_meetings/config.py`:

```python
"""Fixed parameters of the real-meetings study.

Every value here is part of the pre-registered protocol. Changing one after the
protocol freeze (Task 9) is a deviation and must be logged in PROTOCOL.md.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datasets" / "real_meetings"
RAW = DATA / "raw"
AUDIO = DATA / "audio"
MANIFESTS = DATA / "manifests"
RTTM = DATA / "rttm"
SPOTCHECK = DATA / "spotcheck"
RESULTS = ROOT / "results" / "real_meetings"
GENERATED_TEX = ROOT / "Memoire_LaTeX" / "generated"
LORA_ADAPTER = ROOT / "models" / "lora_small_minds14"

SAMPLE_RATE = 16_000
SEED = 20261010

DEV_SECONDS = 180.0
SEGMENT_TARGET_S = 15.0
SEGMENT_MAX_S = 20.0
SEGMENT_MAX_GAP_S = 2.0
SEGMENT_PAD_S = 0.15
IPU_MAX_GAP_S = 0.5
AGM_BLOCK_S = 120.0

AGM_LANGUAGES = ("de", "en", "fr")

AMI_REPO = "edinburghcstr/ami"
AMI_MEETINGS = ("EN2002a", "ES2004a", "IS1009a", "TS3003a")
AMI_MIN_S = 1.0
AMI_MAX_S = 30.0

SUMMRE_REPO = "datasets-CNRS/summ-re-asru"
SUMMRE_MEETINGS = ("018a_EARZ", "032b_EADH", "069c_EEPL")
SUMMRE_EXTERNAL_WHISPER = "WX_vad_noprompt"

DEMAND_URL = "https://zenodo.org/api/records/1227121/files/{env}_16k.zip/content"
DEMAND_ENVS = ("OMEETING", "OOFFICE", "PCAFETER")
SNRS_DB = (20.0, 10.0, 5.0)
NOISE_ONLY_CLIPS = 30
NOISE_ONLY_SECONDS = 10.0

STREAM_CHUNKS_S = (1.0, 2.0, 5.0, 10.0, 20.0)
STREAM_TOLERANCE_WER = 0.01

N_BOOTSTRAP = 10_000
ALPHA = 0.05

NESTLE_TERMS = (
    "nestlé", "nespresso", "nescafé", "maggi", "purina",
    "kitkat", "perrier", "vittel", "gerber", "nesquik",
)
# Identical to backend/stt/engine.py DEFAULT_DOMAIN_PROMPT (the thesis prompt), on purpose.
DOMAIN_PROMPT = (
    "Nestlé, Nespresso, Maggi, Purina, KitKat, Nescafé, "
    "supply chain, plant-based portfolio, Nestlé Ghana"
)

FILLERS = {
    "en": frozenset({"uh", "um", "hmm", "mm", "mmhmm", "mhm", "uhhuh", "er", "erm"}),
    "fr": frozenset({"euh", "heu", "hum", "hm", "mh", "mmh"}),
    "de": frozenset({"äh", "ähm", "öh", "hm", "mhm"}),
}
```

- [ ] **Step 2: Write the failing tests**

`tests/test_rm_text.py`:

```python
import pytest

from backend.evaluation.metrics import wer as thesis_wer
from study_real_meetings.text import (
    Counts,
    has_repetition_loop,
    normalize_tokens,
    score_chars,
    score_words,
    term_hits,
)


def test_worked_example_from_the_learning_notes():
    # "the meeting starts at nine" vs "the meeting start at nine today": 1 S + 1 I over 5 words.
    c = score_words("the meeting starts at nine", "the meeting start at nine today", "en")
    assert (c.sub, c.dele, c.ins, c.n_ref) == (1, 0, 1, 5)
    assert c.wer == pytest.approx(0.4)


def test_matches_thesis_scorer_when_no_fillers_or_numbers():
    ref = "Nous lançons, aujourd'hui, la nouvelle stratégie."
    hyp = "nous lançons aujourdhui la nouvelle stratégies"
    assert score_words(ref, hyp, "fr").wer == pytest.approx(thesis_wer(ref, hyp))


def test_fillers_are_removed_on_both_sides():
    assert score_words("um so we start", "so we start", "en").errors == 0
    assert score_words("euh on commence", "on commence", "fr").errors == 0


def test_number_rule_is_optional_and_symmetric():
    ref, hyp = "founded 160 years ago", "founded one hundred and sixty years ago"
    assert score_words(ref, hyp, "en").errors > 0
    assert score_words(ref, hyp, "en", numbers_to_words=True).errors == 0
    assert normalize_tokens("160", "fr", numbers_to_words=True) == ["cent", "soixante"]


def test_char_counts_ignore_spaces_like_the_thesis():
    c = score_chars("ab cd", "abcd", "en")
    assert c.errors == 0 and c.n_ref == 4


def test_empty_reference_counts_insertions():
    c = score_words("", "thank you", "en")
    assert (c.n_ref, c.ins) == (0, 2)
    assert c.wer != c.wer  # NaN: WER undefined without reference words


def test_term_hits_need_exact_normalised_match():
    hits, total = term_hits("Nestlé and KitKat and Nestlé", "nestle and kitkat and nestlé", "en")
    assert (hits, total) == (2, 3)


def test_repetition_loop_detection():
    loop = "nescafé purina kitkat " * 4
    assert has_repetition_loop(loop, "fr")
    assert not has_repetition_loop("the board approved the plan for next year", "en")


def test_counts_dataclass_errors():
    assert Counts(1, 2, 3, 10).errors == 6
```

- [ ] **Step 3: Run to verify failure**

Run: `.venv\Scripts\python.exe -m pytest tests/test_rm_text.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'study_real_meetings.text'`.

- [ ] **Step 4: Implement**

`study_real_meetings/text.py`:

```python
"""Scoring helpers for the real-meetings study.

Word and character alignment reuse the audited thesis scorer
(backend.evaluation.metrics) so that "WER" means the same thing in every chapter.
Two documented additions: filler-word removal (both sides) and an optional
digits-to-words rule (both sides), reported with and without.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from num2words import num2words

from backend.evaluation.metrics import _levenshtein, normalize_text
from study_real_meetings.config import FILLERS, NESTLE_TERMS

_DIGITS = re.compile(r"^\d+$")


@dataclass(frozen=True)
class Counts:
    sub: int
    dele: int
    ins: int
    n_ref: int

    @property
    def errors(self) -> int:
        return self.sub + self.dele + self.ins

    @property
    def wer(self) -> float:
        return self.errors / self.n_ref if self.n_ref else float("nan")


def normalize_tokens(text: str, language: str, *, numbers_to_words: bool = False) -> list[str]:
    fillers = FILLERS.get(language, frozenset())
    out: list[str] = []
    for token in normalize_text(text).split():
        if token in fillers:
            continue
        if numbers_to_words and _DIGITS.match(token):
            out.extend(normalize_text(num2words(int(token), lang=language)).split())
        else:
            out.append(token)
    return out


def _counts(ref: list, hyp: list) -> Counts:
    if not ref:
        return Counts(0, 0, len(hyp), 0)
    s, d, i, n = _levenshtein(ref, hyp)
    return Counts(s, d, i, n)


def score_words(reference: str, hypothesis: str, language: str, *, numbers_to_words: bool = False) -> Counts:
    return _counts(
        normalize_tokens(reference, language, numbers_to_words=numbers_to_words),
        normalize_tokens(hypothesis, language, numbers_to_words=numbers_to_words),
    )


def score_chars(reference: str, hypothesis: str, language: str) -> Counts:
    ref = list("".join(normalize_tokens(reference, language)))
    hyp = list("".join(normalize_tokens(hypothesis, language)))
    return _counts(ref, hyp)


def term_hits(reference: str, hypothesis: str, language: str, terms=NESTLE_TERMS) -> tuple[int, int]:
    ref = Counter(normalize_tokens(reference, language))
    hyp = Counter(normalize_tokens(hypothesis, language))
    total = sum(ref[t] for t in terms)
    hits = sum(min(ref[t], hyp[t]) for t in terms)
    return hits, total


def has_repetition_loop(hypothesis: str, language: str, n: int = 4, min_repeats: int = 3) -> bool:
    tokens = normalize_tokens(hypothesis, language)
    grams = Counter(tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1))
    return any(count >= min_repeats for count in grams.values())
```

- [ ] **Step 5: Run to verify pass**

Run: `.venv\Scripts\python.exe -m pytest tests/test_rm_text.py -q`
Expected: 9 passed.

- [ ] **Step 6: Commit**

```powershell
git add study_real_meetings/config.py study_real_meetings/text.py tests/test_rm_text.py
git commit -F <msgfile>   # "feat(study): study config and scoring helpers on top of the thesis scorer"
```

---

### Task 3: Segments, manifests and SRT parsing

**Files:**
- Create: `study_real_meetings/srt.py`, `study_real_meetings/manifest.py`
- Test: `tests/test_rm_manifest.py`

**Interfaces:**
- Produces:
  - `Unit(start: float, end: float, text: str)` (frozen dataclass, in `manifest.py`)
  - `Segment(segment_id, dataset, language, audio_path, start, end, reference, cluster, split, speaker="", pair_key="")` with `.duration`
  - `merge_units(units, *, target_s=SEGMENT_TARGET_S, max_s=SEGMENT_MAX_S, max_gap_s=SEGMENT_MAX_GAP_S) -> list[list[Unit]]`
  - `split_for(start_s: float, dev_seconds: float = DEV_SECONDS) -> str`
  - `write_manifest(path, segments)`, `read_manifest(path) -> list[Segment]`
  - `parse_srt(text: str) -> list[Unit]` (in `srt.py`)

- [ ] **Step 1: Write the failing tests**

`tests/test_rm_manifest.py`:

```python
from study_real_meetings.manifest import (
    Segment,
    Unit,
    merge_units,
    read_manifest,
    split_for,
    write_manifest,
)
from study_real_meetings.srt import parse_srt

SRT = """1
00:00:00,800 --> 00:00:02,520
Ladies and Gentlemen.

2
00:00:02,520 --> 00:00:05,440
Geehrte Damen
und Herren,
"""


def test_parse_srt_joins_lines_and_reads_times():
    units = parse_srt(SRT)
    assert units == [
        Unit(0.8, 2.52, "Ladies and Gentlemen."),
        Unit(2.52, 5.44, "Geehrte Damen und Herren,"),
    ]


def test_merge_stops_once_target_is_reached():
    units = [Unit(float(i), float(i + 5), f"u{i}") for i in range(0, 20, 5)]
    groups = merge_units(units, target_s=15, max_s=20, max_gap_s=2)
    assert [[u.text for u in g] for g in groups] == [["u0", "u5", "u10"], ["u15"]]


def test_merge_breaks_on_long_gap_and_on_max_span():
    assert len(merge_units([Unit(0, 2, "a"), Unit(10, 12, "b")], max_gap_s=2)) == 2
    assert len(merge_units([Unit(0, 12, "a"), Unit(12, 25, "b")], max_s=20)) == 2


def test_merge_skips_empty_text():
    assert merge_units([Unit(0, 1, "  "), Unit(1, 2, "x")]) == [[Unit(1, 2, "x")]]


def test_split_for_uses_dev_window():
    assert split_for(0.0) == "dev"
    assert split_for(179.9) == "dev"
    assert split_for(180.0) == "test"


def test_manifest_roundtrip_keeps_unicode(tmp_path):
    seg = Segment("agm-fr-0001", "agm", "fr", "audio/agm/fr.wav", 1.0, 16.0,
                  "Mesdames et messieurs, Nestlé", "agm-fr-b00", "dev")
    path = tmp_path / "m.jsonl"
    write_manifest(path, [seg])
    assert read_manifest(path) == [seg]
    assert seg.duration == 15.0
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv\Scripts\python.exe -m pytest tests/test_rm_manifest.py -q`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement**

`study_real_meetings/manifest.py`:

```python
"""Segment manifests: one JSON object per line, UTF-8."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from study_real_meetings.config import (
    DEV_SECONDS,
    SEGMENT_MAX_GAP_S,
    SEGMENT_MAX_S,
    SEGMENT_TARGET_S,
)


@dataclass(frozen=True)
class Unit:
    start: float
    end: float
    text: str


@dataclass(frozen=True)
class Segment:
    segment_id: str
    dataset: str        # agm | ami-ihm | ami-sdm | summre | noise
    language: str       # en | fr | de
    audio_path: str     # 16 kHz mono wav, relative to config.DATA, forward slashes
    start: float
    end: float
    reference: str
    cluster: str        # resampling unit for the bootstrap
    split: str          # dev | test
    speaker: str = ""
    pair_key: str = ""  # pairs AMI IHM and SDM copies of the same utterance

    @property
    def duration(self) -> float:
        return self.end - self.start


def merge_units(
    units: list[Unit],
    *,
    target_s: float = SEGMENT_TARGET_S,
    max_s: float = SEGMENT_MAX_S,
    max_gap_s: float = SEGMENT_MAX_GAP_S,
) -> list[list[Unit]]:
    groups: list[list[Unit]] = []
    current: list[Unit] = []
    for unit in sorted(units, key=lambda u: u.start):
        if not unit.text.strip():
            continue
        if current:
            too_long = unit.end - current[0].start > max_s
            too_far = unit.start - current[-1].end > max_gap_s
            full = current[-1].end - current[0].start >= target_s
            if too_long or too_far or full:
                groups.append(current)
                current = []
        current.append(unit)
    if current:
        groups.append(current)
    return groups


def split_for(start_s: float, dev_seconds: float = DEV_SECONDS) -> str:
    return "dev" if start_s < dev_seconds else "test"


def write_manifest(path: Path, segments: list[Segment]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        for segment in segments:
            handle.write(json.dumps(asdict(segment), ensure_ascii=False) + "\n")


def read_manifest(path: Path) -> list[Segment]:
    with open(path, encoding="utf-8") as handle:
        return [Segment(**json.loads(line)) for line in handle if line.strip()]
```

`study_real_meetings/srt.py`:

```python
"""Minimal SRT parser (cue index, time line, one or more text lines)."""
from __future__ import annotations

import re

from study_real_meetings.manifest import Unit

_TIME = re.compile(r"(\d+):(\d\d):(\d\d)[,.](\d{3})")


def _seconds(stamp: str) -> float:
    h, m, s, ms = map(int, _TIME.match(stamp.strip()).groups())
    return round(h * 3600 + m * 60 + s + ms / 1000, 3)


def parse_srt(text: str) -> list[Unit]:
    units: list[Unit] = []
    for block in re.split(r"\r?\n\s*\r?\n", text.strip().lstrip("\ufeff")):
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        timing = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if timing is None:
            continue
        start, end = (part.strip() for part in lines[timing].split("-->"))
        body = " ".join(lines[timing + 1 :])
        units.append(Unit(_seconds(start), _seconds(end), body))
    return units
```

- [ ] **Step 4: Run to verify pass**

Run: `.venv\Scripts\python.exe -m pytest tests/test_rm_manifest.py -q`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```powershell
git add study_real_meetings/manifest.py study_real_meetings/srt.py tests/test_rm_manifest.py
git commit -F <msgfile>   # "feat(study): segment manifests, unit merging and SRT parsing"
```

---

### Task 4: Audio I/O and realistic noise mixing

**Files:**
- Create: `study_real_meetings/audio.py`, `study_real_meetings/noise.py`
- Test: `tests/test_rm_audio_noise.py`

**Interfaces:**
- Produces:
  - `convert_to_wav16k(src: Path, dst: Path) -> None` (ffmpeg)
  - `load_segment(path: Path, start: float, end: float) -> np.ndarray` (float32, mono, 16 kHz)
  - `write_wav(path: Path, audio: np.ndarray) -> None`, `wav_duration(path: Path) -> float`
  - `stable_rng(*parts) -> np.random.Generator`
  - `mix_at_snr(speech, noise, snr_db) -> np.ndarray`
  - `pick_noise(bank: dict[str, np.ndarray], segment_id: str, snr_db: float, n_samples: int, seed: int) -> tuple[str, np.ndarray]`
  - `load_demand_bank(demand_dir: Path) -> dict[str, np.ndarray]`

- [ ] **Step 1: Write the failing tests**

`tests/test_rm_audio_noise.py`:

```python
import numpy as np
import pytest

from study_real_meetings.audio import load_segment, wav_duration, write_wav
from study_real_meetings.noise import mix_at_snr, pick_noise, stable_rng

SR = 16_000


def test_load_segment_returns_requested_span(tmp_path):
    audio = np.linspace(-0.5, 0.5, 3 * SR, dtype=np.float32)
    path = tmp_path / "a.wav"
    write_wav(path, audio)
    assert wav_duration(path) == pytest.approx(3.0)
    chunk = load_segment(path, 1.0, 2.5)
    assert chunk.dtype == np.float32 and len(chunk) == int(1.5 * SR)


@pytest.mark.parametrize("snr", [20.0, 10.0, 5.0, 0.0])
def test_mix_reaches_requested_snr(snr):
    rng = np.random.default_rng(0)
    speech = (0.1 * np.sin(np.arange(SR) / 7.0)).astype(np.float32)
    noise = (0.05 * rng.standard_normal(SR // 3)).astype(np.float32)  # shorter: must be tiled
    mix = mix_at_snr(speech, noise, snr)
    added = mix.astype(np.float64) - speech
    measured = 10 * np.log10(np.mean(speech.astype(np.float64) ** 2) / np.mean(added ** 2))
    assert measured == pytest.approx(snr, abs=0.05)


def test_mix_never_clips():
    speech = np.full(SR, 0.9, dtype=np.float32)
    noise = np.random.default_rng(1).standard_normal(SR).astype(np.float32)
    assert np.max(np.abs(mix_at_snr(speech, noise, 0.0))) <= 0.999 + 1e-6


def test_noise_pick_is_deterministic_and_seed_dependent():
    bank = {"OMEETING": np.arange(100_000, dtype=np.float32),
            "OOFFICE": -np.arange(100_000, dtype=np.float32)}
    a = pick_noise(bank, "agm-fr-0003", 10.0, 1000, seed=1)
    b = pick_noise(bank, "agm-fr-0003", 10.0, 1000, seed=1)
    assert a[0] == b[0] and np.array_equal(a[1], b[1]) and len(a[1]) == 1000
    assert stable_rng(1, "x").integers(1 << 30) == stable_rng(1, "x").integers(1 << 30)
    assert stable_rng(1, "x").integers(1 << 30) != stable_rng(2, "x").integers(1 << 30)
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv\Scripts\python.exe -m pytest tests/test_rm_audio_noise.py -q`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement**

`study_real_meetings/audio.py`:

```python
"""Audio helpers. All study audio is 16 kHz mono PCM-16 wav."""
from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

from study_real_meetings.config import SAMPLE_RATE


def convert_to_wav16k(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", str(src),
         "-ac", "1", "-ar", str(SAMPLE_RATE), "-sample_fmt", "s16", str(dst)],
        check=True,
    )


def load_segment(path: Path, start: float, end: float) -> np.ndarray:
    info = sf.info(str(path))
    if info.samplerate != SAMPLE_RATE:
        raise ValueError(f"{path} is {info.samplerate} Hz, expected {SAMPLE_RATE}")
    audio, _ = sf.read(
        str(path),
        start=int(round(start * SAMPLE_RATE)),
        stop=int(round(end * SAMPLE_RATE)),
        dtype="float32",
        always_2d=False,
    )
    return audio.mean(axis=1).astype(np.float32) if audio.ndim > 1 else audio


def write_wav(path: Path, audio: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), np.clip(audio, -1.0, 1.0), SAMPLE_RATE, subtype="PCM_16")


def wav_duration(path: Path) -> float:
    info = sf.info(str(path))
    return info.frames / info.samplerate
```

`study_real_meetings/noise.py`:

```python
"""Real-noise mixing (DEMAND) at a controlled signal-to-noise ratio."""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import soundfile as sf

from study_real_meetings.config import DEMAND_ENVS, SAMPLE_RATE


def stable_rng(*parts) -> np.random.Generator:
    digest = hashlib.sha256(":".join(map(str, parts)).encode("utf-8")).hexdigest()
    return np.random.default_rng(int(digest[:16], 16))


def mix_at_snr(speech: np.ndarray, noise: np.ndarray, snr_db: float) -> np.ndarray:
    if len(noise) < len(speech):
        noise = np.tile(noise, int(np.ceil(len(speech) / len(noise))))
    s = speech.astype(np.float64)
    n = noise[: len(speech)].astype(np.float64)
    p_speech, p_noise = np.mean(s ** 2), np.mean(n ** 2)
    if p_speech == 0 or p_noise == 0:
        return speech.astype(np.float32).copy()
    scale = np.sqrt(p_speech / (p_noise * 10 ** (snr_db / 10)))
    mix = s + scale * n
    peak = np.max(np.abs(mix))
    if peak > 0.999:
        mix *= 0.999 / peak  # scales speech and noise together: SNR unchanged
    return mix.astype(np.float32)


def pick_noise(bank: dict[str, np.ndarray], segment_id: str, snr_db: float,
               n_samples: int, seed: int) -> tuple[str, np.ndarray]:
    rng = stable_rng(seed, segment_id, snr_db)
    kinds = sorted(bank)
    kind = kinds[int(rng.integers(len(kinds)))]
    source = bank[kind]
    if len(source) <= n_samples:
        return kind, source
    offset = int(rng.integers(0, len(source) - n_samples))
    return kind, source[offset : offset + n_samples]


def load_demand_bank(demand_dir: Path) -> dict[str, np.ndarray]:
    bank: dict[str, np.ndarray] = {}
    for env in DEMAND_ENVS:
        path = next(p for p in demand_dir.rglob("ch01.wav") if p.parent.name == env)
        audio, sr = sf.read(str(path), dtype="float32", always_2d=False)
        if sr != SAMPLE_RATE:
            raise ValueError(f"{path}: {sr} Hz, expected {SAMPLE_RATE}")
        bank[env] = audio if audio.ndim == 1 else audio[:, 0]
    return bank
```

- [ ] **Step 4: Run to verify pass**

Run: `.venv\Scripts\python.exe -m pytest tests/test_rm_audio_noise.py -q`
Expected: 7 passed.

- [ ] **Step 5: Commit**

```powershell
git add study_real_meetings/audio.py study_real_meetings/noise.py tests/test_rm_audio_noise.py
git commit -F <msgfile>   # "feat(study): audio I/O and deterministic DEMAND noise mixing at fixed SNR"
```

---

### Task 5: Source builders (AGM, AMI, SUMM-RE) and the data-build script

**Files:**
- Create: `study_real_meetings/sources/agm.py`, `study_real_meetings/sources/ami.py`, `study_real_meetings/sources/summre.py`
- Create: `study_real_meetings/scripts/build_data.py`
- Test: `tests/test_rm_sources.py`

**Interfaces:**
- Consumes: `Unit`, `Segment`, `merge_units`, `split_for`, `parse_srt`, `convert_to_wav16k`, `write_wav`, `wav_duration`.
- Produces:
  - `agm.find_agm_files(agm_dir: Path) -> dict[str, tuple[Path, Path]]` (lang → (audio, srt))
  - `agm.build_agm_segments(language: str, srt_text: str, audio_rel: str, audio_duration: float) -> list[Segment]`
  - `ami.select_rows(rows: list[dict], meetings, min_s, max_s) -> list[dict]`
  - `ami.pair_key(row: dict) -> str`
  - `ami.segment_for_row(row: dict, mic: str, audio_rel: str) -> Segment`
  - `summre.parse_tokens(csv_text: str) -> list[Unit]` (TokensAlign tier, markers dropped)
  - `summre.ipus(tokens: list[Unit], max_gap_s=IPU_MAX_GAP_S) -> list[Unit]`
  - `summre.build_summre_segments(meeting: str, participant: str, tokens: list[Unit], audio_rel: str) -> list[Segment]`
  - `summre.tokens_in_span(tokens: list[Unit], start: float, end: float) -> str`
  - `summre.speech_regions(tokens: list[Unit], max_gap_s: float = 0.3) -> list[tuple[float, float]]`
  - Files written by the script: `datasets/real_meetings/manifests/{agm,ami-ihm,ami-sdm,summre,noise}.jsonl`, `datasets/real_meetings/audio/...`, `datasets/real_meetings/rttm/<meeting>.rttm`, `datasets/real_meetings/audio/summre-mix/<meeting>.wav`, `datasets/real_meetings/raw/summre/tokens/<recording>.json`

- [ ] **Step 1: Write the failing tests**

`tests/test_rm_sources.py`:

```python
from pathlib import Path

from study_real_meetings.manifest import Unit
from study_real_meetings.sources import agm, ami, summre

SRT = "\n\n".join(
    f"{i + 1}\n00:{(i * 5) // 60:02d}:{(i * 5) % 60:02d},000 --> 00:{(i * 5 + 5) // 60:02d}:{(i * 5 + 5) % 60:02d},000\nmot{i}"
    for i in range(60)  # 60 cues x 5 s = 300 s
)


def test_agm_segments_cover_cues_with_ids_clusters_and_split():
    segs = agm.build_agm_segments("fr", SRT, "audio/agm/fr.wav", audio_duration=300.0)
    assert segs[0].segment_id == "agm-fr-0000"
    assert segs[0].reference == "mot0 mot1 mot2"
    assert {s.split for s in segs} == {"dev", "test"}
    assert segs[0].cluster == "agm-fr-b00" and segs[-1].cluster == "agm-fr-b02"
    for a, b in zip(segs, segs[1:]):
        assert a.end <= b.start  # padding never overlaps the next segment
    assert all(s.pair_key == s.segment_id for s in segs)


def test_find_agm_files_matches_language_tags(tmp_path):
    for lang in ("DE", "EN", "FR"):
        (tmp_path / f"Nestlé Chair & CEO ｜ Annual General Meeting 2026 ({lang}).mp3").touch()
        (tmp_path / f"[English] Nestlé Chair & CEO  Annual General Meeting 2026 ({lang}) [DownSub.com].srt").touch()
    found = agm.find_agm_files(tmp_path)
    assert set(found) == {"de", "en", "fr"}
    assert found["fr"][0].suffix == ".mp3" and found["fr"][1].suffix == ".srt"


def _row(meeting, speaker, begin, end, text="HELLO THERE"):
    return {"meeting_id": meeting, "speaker_id": speaker, "begin_time": begin,
            "end_time": end, "text": text, "audio_id": f"AMI_{meeting}_{speaker}_{begin}"}


def test_ami_selection_and_pairing():
    rows = [_row("EN2002a", "MEE073", 10.0, 12.0), _row("EN2002a", "MEE073", 20.0, 20.5),
            _row("XX0000a", "MEE001", 10.0, 12.0), _row("EN2002a", "MEE073", 30.0, 70.0)]
    kept = ami.select_rows(rows, {"EN2002a"}, 1.0, 30.0)
    assert len(kept) == 1
    seg_ihm = ami.segment_for_row(kept[0], "ihm", "audio/ami-ihm/x.wav")
    seg_sdm = ami.segment_for_row(kept[0], "sdm", "audio/ami-sdm/x.wav")
    assert seg_ihm.pair_key == seg_sdm.pair_key == "EN2002a-MEE073-0001000"
    assert seg_ihm.dataset == "ami-ihm" and seg_ihm.cluster == "ami-EN2002a-MEE073"
    assert (seg_ihm.start, seg_ihm.end) == (0.0, 2.0)  # each utterance is its own wav
    assert seg_ihm.split == "dev"


TOKENS_CSV = (
    '\ufeff"TokensAlign",0.0,0.9,"#"\n'
    '"TokensAlign",0.9,1.8,"bonjour"\n'
    '"TokensAlign",1.8,2.0,"@"\n'
    '"TokensAlign",2.0,2.4,"à"\n'
    '"TokensAlign",2.4,2.9,"tous"\n'
    '"TokensAlign",4.5,5.4,"euh"\n'
    '"TokensAlign",5.4,6.0,"bon"\n'
    '"PhonAlign",0.9,1.1,"b"\n'
)


def test_summre_tokens_ipus_and_segments():
    tokens = summre.parse_tokens(TOKENS_CSV)
    assert [t.text for t in tokens] == ["bonjour", "à", "tous", "euh", "bon"]
    assert [u.text for u in summre.ipus(tokens)] == ["bonjour à tous", "euh bon"]
    segs = summre.build_summre_segments("018a_EARZ", "055", tokens, "audio/summre/018a_EARZ_055.wav")
    assert len(segs) == 1 and segs[0].reference == "bonjour à tous euh bon"
    assert segs[0].cluster == "summre-018a_EARZ-055" and segs[0].speaker == "055"
    assert summre.tokens_in_span(tokens, 0.0, 3.0) == "bonjour à tous"
    assert summre.speech_regions(tokens) == [(0.9, 2.9), (4.5, 6.0)]
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv\Scripts\python.exe -m pytest tests/test_rm_sources.py -q`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement the AGM builder**

`study_real_meetings/sources/agm.py`:

```python
"""Nestlé AGM 2026: same speech in DE/EN/FR, with captions published by Nestlé."""
from __future__ import annotations

from pathlib import Path

from study_real_meetings.config import AGM_BLOCK_S, AGM_LANGUAGES, SEGMENT_PAD_S
from study_real_meetings.manifest import Segment, merge_units, split_for
from study_real_meetings.srt import parse_srt


def find_agm_files(agm_dir: Path) -> dict[str, tuple[Path, Path]]:
    found: dict[str, tuple[Path, Path]] = {}
    for lang in AGM_LANGUAGES:
        tag = f"({lang.upper()})"
        audio = [p for p in agm_dir.iterdir() if p.suffix.lower() in {".mp3", ".mp4", ".m4a", ".wav"} and tag in p.name]
        srt = [p for p in agm_dir.iterdir() if p.suffix.lower() == ".srt" and tag in p.name]
        if len(audio) != 1 or len(srt) != 1:
            raise FileNotFoundError(f"Expected one audio and one .srt for {tag} in {agm_dir}, got {audio} / {srt}")
        found[lang] = (audio[0], srt[0])
    return found


def build_agm_segments(language: str, srt_text: str, audio_rel: str, audio_duration: float) -> list[Segment]:
    groups = merge_units(parse_srt(srt_text))
    segments: list[Segment] = []
    for k, group in enumerate(groups):
        raw_start, raw_end = group[0].start, group[-1].end
        prev_end = groups[k - 1][-1].end if k > 0 else 0.0
        next_start = groups[k + 1][0].start if k + 1 < len(groups) else audio_duration
        start = max(raw_start - SEGMENT_PAD_S, (prev_end + raw_start) / 2, 0.0)
        end = min(raw_end + SEGMENT_PAD_S, (raw_end + next_start) / 2, audio_duration)
        segment_id = f"agm-{language}-{k:04d}"
        segments.append(Segment(
            segment_id=segment_id, dataset="agm", language=language, audio_path=audio_rel,
            start=round(start, 3), end=round(end, 3),
            reference=" ".join(u.text for u in group),
            cluster=f"agm-{language}-b{int(raw_start // AGM_BLOCK_S):02d}",
            split=split_for(raw_start), pair_key=segment_id,
        ))
    return segments
```

- [ ] **Step 4: Implement the AMI builder**

`study_real_meetings/sources/ami.py`:

```python
"""AMI Meeting Corpus (HF edinburghcstr/ami, parquet): one wav per official utterance."""
from __future__ import annotations

from study_real_meetings.manifest import Segment, split_for


def select_rows(rows: list[dict], meetings, min_s: float, max_s: float) -> list[dict]:
    keep = set(meetings)
    return [r for r in rows
            if r["meeting_id"] in keep and min_s <= r["end_time"] - r["begin_time"] <= max_s]


def pair_key(row: dict) -> str:
    return f"{row['meeting_id']}-{row['speaker_id']}-{int(round(row['begin_time'] * 100)):07d}"


def segment_for_row(row: dict, mic: str, audio_rel: str) -> Segment:
    key = pair_key(row)
    return Segment(
        segment_id=f"ami-{mic}-{key}", dataset=f"ami-{mic}", language="en",
        audio_path=audio_rel, start=0.0,
        end=round(row["end_time"] - row["begin_time"], 3),
        reference=row["text"],
        cluster=f"ami-{row['meeting_id']}-{row['speaker_id']}",
        split=split_for(row["begin_time"]), speaker=row["speaker_id"], pair_key=key,
    )
```

- [ ] **Step 5: Implement the SUMM-RE builder**

`study_real_meetings/sources/summre.py`:

```python
"""SUMM-RE ASRU (French meetings, one channel per participant, gold word alignment)."""
from __future__ import annotations

import csv
import io

from study_real_meetings.config import IPU_MAX_GAP_S, SEGMENT_PAD_S
from study_real_meetings.manifest import Segment, Unit, merge_units, split_for

_TIER = "TokensAlign"


def _is_word(label: str) -> bool:
    label = label.strip()
    return bool(label) and label != "#" and "@" not in label and "*" not in label and label.lower() != "xxx"


def parse_tokens(csv_text: str) -> list[Unit]:
    rows = csv.reader(io.StringIO(csv_text.lstrip("\ufeff")))
    return [Unit(float(r[1]), float(r[2]), r[3].strip())
            for r in rows if len(r) >= 4 and r[0] == _TIER and _is_word(r[3])]


def ipus(tokens: list[Unit], max_gap_s: float = IPU_MAX_GAP_S) -> list[Unit]:
    out: list[Unit] = []
    for tok in sorted(tokens, key=lambda t: t.start):
        if out and tok.start - out[-1].end <= max_gap_s:
            last = out[-1]
            out[-1] = Unit(last.start, tok.end, f"{last.text} {tok.text}")
        else:
            out.append(tok)
    return out


def build_summre_segments(meeting: str, participant: str, tokens: list[Unit], audio_rel: str) -> list[Segment]:
    segments: list[Segment] = []
    for k, group in enumerate(merge_units(ipus(tokens))):
        start = max(group[0].start - SEGMENT_PAD_S, 0.0)
        end = group[-1].end + SEGMENT_PAD_S
        segment_id = f"summre-{meeting}-{participant}-{k:04d}"
        segments.append(Segment(
            segment_id=segment_id, dataset="summre", language="fr", audio_path=audio_rel,
            start=round(start, 3), end=round(end, 3),
            reference=" ".join(u.text for u in group),
            cluster=f"summre-{meeting}-{participant}", split=split_for(group[0].start),
            speaker=participant, pair_key=segment_id,
        ))
    return segments


def tokens_in_span(tokens: list[Unit], start: float, end: float) -> str:
    return " ".join(t.text for t in tokens if t.start >= start and t.end <= end)


def speech_regions(tokens: list[Unit], max_gap_s: float = 0.3) -> list[tuple[float, float]]:
    return [(u.start, u.end) for u in ipus(tokens, max_gap_s=max_gap_s)]
```

- [ ] **Step 6: Run to verify pass**

Run: `.venv\Scripts\python.exe -m pytest tests/test_rm_sources.py -q`
Expected: 4 passed.

- [ ] **Step 7: Write the data-build script**

`study_real_meetings/scripts/build_data.py`:

```python
"""Download, convert and segment every study source.

Usage (from repo root):
  .venv\\Scripts\\python.exe -m study_real_meetings.scripts.build_data --agm-dir "<folder with AGM mp3+srt>"
Idempotent: existing converted files are reused.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

import librosa
import numpy as np
import pyarrow.parquet as pq
import soundfile as sf
from dotenv import load_dotenv
from huggingface_hub import HfApi, hf_hub_download

from study_real_meetings import config as C
from study_real_meetings.audio import convert_to_wav16k, wav_duration, write_wav
from study_real_meetings.manifest import Segment, write_manifest
from study_real_meetings.noise import load_demand_bank, stable_rng
from study_real_meetings.sources import agm, ami, summre


def rel(path: Path) -> str:
    return path.relative_to(C.DATA).as_posix()


def build_agm(agm_dir: Path) -> list[Segment]:
    segments: list[Segment] = []
    for lang, (src, srt) in agm.find_agm_files(agm_dir).items():
        wav = C.AUDIO / "agm" / f"agm_{lang}.wav"
        if not wav.exists():
            convert_to_wav16k(src, wav)
        text = srt.read_text(encoding="utf-8-sig")
        (C.RAW / "agm").mkdir(parents=True, exist_ok=True)
        (C.RAW / "agm" / f"agm_{lang}.srt").write_text(text, encoding="utf-8")
        segments += agm.build_agm_segments(lang, text, rel(wav), wav_duration(wav))
    return segments


def _decode(audio_struct: dict) -> np.ndarray:
    audio, sr = sf.read(io.BytesIO(audio_struct["bytes"]), dtype="float32", always_2d=False)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    if sr != C.SAMPLE_RATE:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=C.SAMPLE_RATE)
    return audio.astype(np.float32)


def build_ami(token: str | None) -> dict[str, list[Segment]]:
    out: dict[str, list[Segment]] = {}
    files = HfApi(token=token).list_repo_files(C.AMI_REPO, repo_type="dataset")
    for mic in ("ihm", "sdm"):
        segments: list[Segment] = []
        for shard in sorted(f for f in files if f.startswith(f"{mic}/test-")):
            local = hf_hub_download(C.AMI_REPO, shard, repo_type="dataset", token=token)
            for batch in pq.ParquetFile(local).iter_batches(batch_size=256):
                for row in ami.select_rows(batch.to_pylist(), C.AMI_MEETINGS, C.AMI_MIN_S, C.AMI_MAX_S):
                    wav = C.AUDIO / f"ami-{mic}" / f"{ami.pair_key(row)}.wav"
                    if not wav.exists():
                        write_wav(wav, _decode(row["audio"]))
                    segments.append(ami.segment_for_row(row, mic, rel(wav)))
        out[f"ami-{mic}"] = sorted(segments, key=lambda s: s.segment_id)
    return out


def build_summre(token: str | None) -> list[Segment]:
    files = HfApi(token=token).list_repo_files(C.SUMMRE_REPO, repo_type="dataset")
    recordings = sorted({Path(f).name.split("_anon")[0] for f in files
                         if f.startswith("audio_anonymized/") and Path(f).name.startswith(C.SUMMRE_MEETINGS)})
    segments: list[Segment] = []
    by_meeting: dict[str, list[tuple[str, Path, list]]] = defaultdict(list)
    for rec in recordings:
        meeting, participant = rec.rsplit("_", 1)
        src = hf_hub_download(C.SUMMRE_REPO, f"audio_anonymized/{rec}_anon.wav", repo_type="dataset", token=token)
        gold = hf_hub_download(C.SUMMRE_REPO, f"gold_transcriptions/csv/{rec}_anon.csv", repo_type="dataset", token=token)
        ext = hf_hub_download(C.SUMMRE_REPO,
                              f"whisper_transcriptions/{C.SUMMRE_EXTERNAL_WHISPER}/csv/{rec}-palign_anon.csv",
                              repo_type="dataset", token=token)
        wav = C.AUDIO / "summre" / f"{rec}.wav"
        if not wav.exists():
            convert_to_wav16k(Path(src), wav)
        tokens = summre.parse_tokens(Path(gold).read_text(encoding="utf-8-sig"))
        external = summre.parse_tokens(Path(ext).read_text(encoding="utf-8-sig"))
        tok_dir = C.RAW / "summre" / "tokens"
        tok_dir.mkdir(parents=True, exist_ok=True)
        (tok_dir / f"{rec}.json").write_text(json.dumps({
            "gold": [[t.start, t.end, t.text] for t in tokens],
            "external_whisper": [[t.start, t.end, t.text] for t in external],
        }, ensure_ascii=False), encoding="utf-8")
        segments += summre.build_summre_segments(meeting, participant, tokens, rel(wav))
        by_meeting[meeting].append((participant, wav, tokens))
    for meeting, channels in by_meeting.items():  # D1: summed mix + reference RTTM
        audios = [sf.read(str(w), dtype="float32")[0] for _, w, _ in channels]
        mix = np.zeros(max(len(a) for a in audios), dtype=np.float32)
        for a in audios:
            mix[: len(a)] += a
        write_wav(C.AUDIO / "summre-mix" / f"{meeting}.wav", mix / len(audios))
        C.RTTM.mkdir(parents=True, exist_ok=True)
        lines = [f"SPEAKER {meeting} 1 {s:.3f} {e - s:.3f} <NA> <NA> {p} <NA> <NA>"
                 for p, _, toks in channels for s, e in summre.speech_regions(toks)]
        (C.RTTM / f"{meeting}.rttm").write_text("\n".join(sorted(lines, key=lambda l: float(l.split()[3]))) + "\n", encoding="utf-8")
    return segments


def build_noise() -> list[Segment]:
    demand_dir = C.RAW / "demand"
    for env in C.DEMAND_ENVS:
        if not any(p.parent.name == env for p in demand_dir.rglob("ch01.wav")):
            demand_dir.mkdir(parents=True, exist_ok=True)
            zpath = demand_dir / f"{env}_16k.zip"
            urllib.request.urlretrieve(C.DEMAND_URL.format(env=env), zpath)
            zipfile.ZipFile(zpath).extractall(demand_dir)
    bank = load_demand_bank(demand_dir)
    segments: list[Segment] = []
    n = int(C.NOISE_ONLY_SECONDS * C.SAMPLE_RATE)
    for k in range(C.NOISE_ONLY_CLIPS):
        rng = stable_rng(C.SEED, "noise-only", k)
        env = C.DEMAND_ENVS[k % len(C.DEMAND_ENVS)]
        offset = int(rng.integers(0, len(bank[env]) - n))
        wav = C.AUDIO / "noise" / f"noise_{k:02d}_{env}.wav"
        clip = bank[env][offset: offset + n]
        write_wav(wav, 0.1 * clip / max(float(np.sqrt(np.mean(clip ** 2))), 1e-9))
        segments.append(Segment(f"noise-{k:02d}", "noise", "en", rel(wav), 0.0, C.NOISE_ONLY_SECONDS,
                                "", f"noise-{env}", "test", pair_key=f"noise-{k:02d}"))
    return segments


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agm-dir", type=Path, required=True)
    args = parser.parse_args()
    load_dotenv(C.ROOT / ".env")
    token = os.getenv("HF_TOKEN")
    manifests = {"agm": build_agm(args.agm_dir), **build_ami(token),
                 "summre": build_summre(token), "noise": build_noise()}
    for name, segments in manifests.items():
        write_manifest(C.MANIFESTS / f"{name}.jsonl", segments)
        hours = sum(s.duration for s in segments) / 3600
        test = sum(s.split == "test" for s in segments)
        print(f"{name:8} segments={len(segments):5} test={test:5} hours={hours:5.2f}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 8: Build the real data**

AGM audio and captions are public Nestlé material. Copy only the `AGMDEENFR` folder (never `audioReunionréel/` itself) into the git-ignored raw folder:

```powershell
New-Item -ItemType Directory -Force datasets\real_meetings\raw\agm_src | Out-Null
Copy-Item -LiteralPath "C:\Users\ulric\Documents\autoresearch-win-rtx\audioReunionréel\AGMDEENFR\*" -Destination datasets\real_meetings\raw\agm_src
.venv\Scripts\python.exe -m study_real_meetings.scripts.build_data --agm-dir datasets\real_meetings\raw\agm_src
```

Expected: about 2.5 GB AMI + about 1.5 GB SUMM-RE + about 280 MB DEMAND downloaded (tens of minutes). It ends with a table such as:
`agm segments≈270 (≈90/language)`, `ami-ihm` / `ami-sdm` with equal counts (≥ 1 h each), `summre ≈ 1 h`, `noise 30`.

**Checks (stop and investigate if any fails):**
- `ami-ihm` and `ami-sdm` have the same number of segments, and the same `pair_key` set.
- Every `datasets/real_meetings/rttm/<meeting>.rttm` exists for the 3 SUMM-RE meetings.
- Listen to `datasets/real_meetings/audio/summre-mix/018a_EARZ.wav` for 30 s: the voices must sound simultaneous and natural (channels are synchronised). If there is an echo or lag between voices, the channels are not aligned. Stop, and record it as a blocker for D1 in PROTOCOL.md.

- [ ] **Step 9: Commit (code only; data is ignored)**

```powershell
git add study_real_meetings/sources study_real_meetings/scripts/build_data.py tests/test_rm_sources.py
git commit -F <msgfile>   # "feat(study): AGM/AMI/SUMM-RE/DEMAND source builders and data-build script"
```

---

### Task 6: Transcriber adapters

**Files:**
- Create: `study_real_meetings/transcribers.py`
- Test: `tests/test_rm_runner.py` (GPU smoke test only; marked `gpu`)

**Interfaces:**
- Produces:
  - `Transcript(text: str, detected_language: str | None, seconds: float)`
  - Each adapter has attributes `system: str`, `model_id: str`, `compute_type: str` and the method `transcribe(audio: np.ndarray, *, language: str | None, prompt: str | None) -> Transcript`
  - `SYSTEMS = ("whisper-small", "whisper-large-v3", "mms-1b-all", "conformer-ctc-large", "hf-whisper-small", "hf-whisper-small-lora")`
  - `make_transcriber(system: str)`, `release(transcriber) -> None`

- [ ] **Step 1: Implement**

`study_real_meetings/transcribers.py`:

```python
"""One interface for the four model families compared in the study.

CTC systems (MMS, Conformer) need the language: it is given "by construction",
exactly as in the canonical campaign. Whisper can run forced or auto.
"""
from __future__ import annotations

import gc
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from study_real_meetings.audio import write_wav
from study_real_meetings.config import LORA_ADAPTER, SAMPLE_RATE

SYSTEMS = ("whisper-small", "whisper-large-v3", "mms-1b-all", "conformer-ctc-large",
           "hf-whisper-small", "hf-whisper-small-lora")
_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


@dataclass(frozen=True)
class Transcript:
    text: str
    detected_language: str | None
    seconds: float


class FasterWhisperTranscriber:
    def __init__(self, size: str, compute_type: str = "float16"):
        from faster_whisper import WhisperModel
        self.model = WhisperModel(size, device=_DEVICE, compute_type=compute_type if _DEVICE == "cuda" else "int8")
        self.system, self.model_id, self.compute_type = f"whisper-{size}", size, compute_type

    def transcribe(self, audio, *, language, prompt):
        t0 = time.perf_counter()
        segments, info = self.model.transcribe(
            audio, language=language, initial_prompt=prompt, beam_size=5,
            temperature=[0.0], condition_on_previous_text=False, vad_filter=False,
        )
        text = " ".join(s.text.strip() for s in segments)  # consuming the generator runs decoding
        return Transcript(text.strip(), info.language, time.perf_counter() - t0)


class HFWhisperTranscriber:
    """transformers Whisper, optionally with the thesis LoRA adapter merged (same backend for J0/J)."""

    def __init__(self, adapter_dir: Path | None = None, base: str = "openai/whisper-small"):
        from transformers import WhisperForConditionalGeneration, WhisperProcessor
        self.dtype = torch.float16 if _DEVICE == "cuda" else torch.float32
        self.processor = WhisperProcessor.from_pretrained(str(adapter_dir) if adapter_dir else base)
        model = WhisperForConditionalGeneration.from_pretrained(base, torch_dtype=self.dtype)
        if adapter_dir:
            from peft import PeftModel
            model = PeftModel.from_pretrained(model, str(adapter_dir)).merge_and_unload()
        self.model = model.to(_DEVICE).eval()
        self.system = "hf-whisper-small-lora" if adapter_dir else "hf-whisper-small"
        self.model_id = f"{base}+{adapter_dir.name}" if adapter_dir else base
        self.compute_type = str(self.dtype).replace("torch.", "")

    def transcribe(self, audio, *, language, prompt):
        if prompt:
            raise ValueError("Prompting is only evaluated with faster-whisper (H4b).")
        t0 = time.perf_counter()
        feats = self.processor.feature_extractor(audio, sampling_rate=SAMPLE_RATE, return_tensors="pt").input_features
        with torch.no_grad():
            ids = self.model.generate(feats.to(_DEVICE, self.dtype), language=language, task="transcribe",
                                      num_beams=5, max_new_tokens=440)
        text = self.processor.tokenizer.batch_decode(ids, skip_special_tokens=True)[0].strip()
        return Transcript(text, language, time.perf_counter() - t0)


class MMSTranscriber:
    LANGS = {"en": "eng", "fr": "fra", "de": "deu"}

    def __init__(self, model_id: str = "facebook/mms-1b-all"):
        from transformers import AutoProcessor, Wav2Vec2ForCTC
        self.dtype = torch.float16 if _DEVICE == "cuda" else torch.float32
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model = Wav2Vec2ForCTC.from_pretrained(model_id, torch_dtype=self.dtype,
                                                    ignore_mismatched_sizes=True).to(_DEVICE).eval()
        self.current = None
        self.system, self.model_id, self.compute_type = "mms-1b-all", model_id, str(self.dtype).replace("torch.", "")

    def transcribe(self, audio, *, language, prompt):
        if language is None:
            raise ValueError("MMS needs the language (given by construction).")
        if self.current != language:
            self.processor.tokenizer.set_target_lang(self.LANGS[language])
            self.model.load_adapter(self.LANGS[language])
            self.current = language
        t0 = time.perf_counter()
        inputs = self.processor(audio, sampling_rate=SAMPLE_RATE, return_tensors="pt")
        kwargs = {"input_values": inputs.input_values.to(_DEVICE, self.dtype)}
        if getattr(inputs, "attention_mask", None) is not None:
            kwargs["attention_mask"] = inputs.attention_mask.to(_DEVICE)
        with torch.no_grad():
            ids = torch.argmax(self.model(**kwargs).logits, dim=-1)[0]
        return Transcript(self.processor.decode(ids).strip(), language, time.perf_counter() - t0)


class NemoConformerTranscriber:
    MODELS = {"en": "nvidia/stt_en_conformer_ctc_large",
              "fr": "nvidia/stt_fr_conformer_ctc_large",
              "de": "nvidia/stt_de_conformer_ctc_large"}

    def __init__(self):
        self.models: dict = {}
        self.system, self.model_id, self.compute_type = "conformer-ctc-large", "nvidia/stt_{en,fr,de}_conformer_ctc_large", "float32"
        self.tmp = Path(tempfile.mkdtemp(prefix="rm_nemo_"))

    def _model(self, language):
        if language not in self.models:
            import nemo.collections.asr as nemo_asr
            for old in list(self.models):  # one checkpoint in VRAM at a time
                del self.models[old]
            gc.collect()
            torch.cuda.empty_cache()
            try:
                model = nemo_asr.models.EncDecCTCModelBPE.from_pretrained(self.MODELS[language])
            except Exception:
                model = nemo_asr.models.EncDecCTCModel.from_pretrained(self.MODELS[language])
            self.models[language] = model.to(_DEVICE).eval()
        return self.models[language]

    def transcribe(self, audio, *, language, prompt):
        if language is None:
            raise ValueError("Conformer checkpoints are monolingual (language given by construction).")
        model = self._model(language)
        wav = self.tmp / "segment.wav"
        write_wav(wav, audio)
        t0 = time.perf_counter()
        out = model.transcribe([str(wav)])  # same call as backend/training/eval_conformer.py
        hyp = out[0] if out else ""
        if isinstance(hyp, (list, tuple)):
            hyp = hyp[0]
        text = hyp.text if hasattr(hyp, "text") else str(hyp)
        return Transcript(text.strip(), language, time.perf_counter() - t0)


def make_transcriber(system: str):
    if system == "whisper-small":
        return FasterWhisperTranscriber("small")
    if system == "whisper-large-v3":
        return FasterWhisperTranscriber("large-v3")
    if system == "mms-1b-all":
        return MMSTranscriber()
    if system == "conformer-ctc-large":
        return NemoConformerTranscriber()
    if system == "hf-whisper-small":
        return HFWhisperTranscriber(None)
    if system == "hf-whisper-small-lora":
        return HFWhisperTranscriber(LORA_ADAPTER)
    raise ValueError(f"Unknown system {system!r}; expected one of {SYSTEMS}")


def release(transcriber) -> None:
    del transcriber
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
```

- [ ] **Step 2: Write the GPU smoke test**

Create `tests/test_rm_runner.py` with this content. Task 7 appends to it.

```python
import numpy as np
import pytest
import soundfile as sf
from pathlib import Path

SAMPLE = Path(__file__).parent / "sample.wav"


@pytest.mark.gpu
@pytest.mark.parametrize("system", ["whisper-small", "mms-1b-all", "conformer-ctc-large",
                                    "hf-whisper-small", "hf-whisper-small-lora"])
def test_every_system_transcribes_the_sample(system):
    from study_real_meetings.transcribers import make_transcriber, release
    audio, sr = sf.read(str(SAMPLE), dtype="float32")
    assert sr == 16_000
    t = make_transcriber(system)
    out = t.transcribe(audio, language="en", prompt=None)
    assert isinstance(out.text, str) and out.seconds > 0
    release(t)
```

- [ ] **Step 3: Run the GPU smoke test**

Run: `.venv\Scripts\python.exe -m pytest tests/test_rm_runner.py -m gpu -q`
Expected: 5 passed (first run downloads models; NeMo and MMS take several minutes). `whisper-large-v3` is exercised in Task 13's dev run. If NeMo fails to import, rerun the 16/09 diagnosis (`audits/diarization_20260916/DIAGNOSTIC.md`); do not change pinned versions without logging a deviation.

- [ ] **Step 4: Commit**

```powershell
git add study_real_meetings/transcribers.py tests/test_rm_runner.py
git commit -F <msgfile>   # "feat(study): unified transcriber adapters (faster-whisper, HF+LoRA, MMS, NeMo)"
```

---

### Task 7: Condition runner with provenance and resumable CSV

**Files:**
- Create: `study_real_meetings/runner.py`
- Test: `tests/test_rm_runner.py` (append)

**Interfaces:**
- Consumes: `Segment`, `load_segment`, `pick_noise`, `mix_at_snr`, `score_words`, `score_chars`, `term_hits`, `has_repetition_loop`, `Transcript`, `config.DOMAIN_PROMPT`.
- Produces:
  - `Condition(forced_language: bool = True, snr_db: float | None = None, prompt: bool = False, denoise: bool = False)` with `.name` (for example `forced-clean`, `auto-snr5`, `forced-snr10-denoise`, `forced-clean-prompt`)
  - `FIELDS: list[str]` (CSV columns, in order)
  - `prepare_audio(segment, condition, bank, seed=SEED, data_root=DATA) -> tuple[np.ndarray, str]`
  - `collect_provenance() -> dict[str, str]`
  - `run(segments, transcriber, condition, *, hypothesis_id, out_csv, bank=None, provenance, seed=SEED, data_root=DATA) -> int`
  - `read_rows(path) -> list[dict]`

- [ ] **Step 1: Append the failing tests**

Append to `tests/test_rm_runner.py`:

```python
from study_real_meetings.audio import write_wav
from study_real_meetings.manifest import Segment
from study_real_meetings.runner import FIELDS, Condition, read_rows, run
from study_real_meetings.transcribers import Transcript


class FakeTranscriber:
    system, model_id, compute_type = "fake", "fake-1", "none"

    def __init__(self, text="the meeting start at nine today"):
        self.text, self.calls = text, []

    def transcribe(self, audio, *, language, prompt):
        self.calls.append((len(audio), language, prompt))
        return Transcript(self.text, language or "en", 0.5)


def _setup(tmp_path):
    write_wav(tmp_path / "audio" / "a.wav", 0.1 * np.sin(np.arange(48_000) / 5).astype(np.float32))
    seg = Segment("s1", "agm", "en", "audio/a.wav", 0.5, 2.5, "the meeting starts at nine", "c1", "test")
    bank = {"OMEETING": np.random.default_rng(0).standard_normal(64_000).astype(np.float32)}
    return seg, bank


PROV = {"git_commit": "abc", "packages": "{}", "gpu": "none"}


def test_condition_names_are_unique_and_readable():
    assert Condition().name == "forced-clean"
    assert Condition(forced_language=False, snr_db=5.0).name == "auto-snr5"
    assert Condition(snr_db=10.0, denoise=True).name == "forced-snr10-denoise"
    assert Condition(prompt=True).name == "forced-clean-prompt"


def test_run_writes_scored_row_and_resumes(tmp_path):
    seg, bank = _setup(tmp_path)
    out = tmp_path / "runs.csv"
    fake = FakeTranscriber()
    n = run([seg], fake, Condition(snr_db=10.0), hypothesis_id="H2", out_csv=out,
            bank=bank, provenance=PROV, data_root=tmp_path)
    assert n == 1 and fake.calls == [(32_000, "en", None)]
    row = read_rows(out)[0]
    assert list(row) == FIELDS
    assert (row["sub"], row["del"], row["ins"], row["n_ref"]) == ("1", "0", "1", "5")
    assert row["condition"] == "forced-snr10" and row["noise_type"] == "OMEETING"
    assert row["git_commit"] == "abc" and row["split"] == "test"
    again = run([seg], fake, Condition(snr_db=10.0), hypothesis_id="H2", out_csv=out,
                bank=bank, provenance=PROV, data_root=tmp_path)
    assert again == 0 and len(read_rows(out)) == 1


def test_auto_condition_passes_no_language_and_prompt_is_injected(tmp_path):
    seg, bank = _setup(tmp_path)
    fake = FakeTranscriber()
    run([seg], fake, Condition(forced_language=False, prompt=True), hypothesis_id="H4", out_csv=tmp_path / "r.csv",
        bank=bank, provenance=PROV, data_root=tmp_path)
    _, language, prompt = fake.calls[0]
    assert language is None and prompt.startswith("Nestlé")
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv\Scripts\python.exe -m pytest tests/test_rm_runner.py -q`
Expected: FAIL with `ImportError: cannot import name 'FIELDS'`.

- [ ] **Step 3: Implement**

`study_real_meetings/runner.py`:

```python
"""Apply one condition and one transcriber to segments; append one row per segment."""
from __future__ import annotations

import csv
import importlib.metadata
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from study_real_meetings.audio import load_segment
from study_real_meetings.config import DATA, DOMAIN_PROMPT, ROOT, SAMPLE_RATE, SEED
from study_real_meetings.manifest import Segment
from study_real_meetings.noise import mix_at_snr, pick_noise
from study_real_meetings.text import has_repetition_loop, score_chars, score_words, term_hits

FIELDS = [
    "hypothesis_id", "dataset", "language", "segment_id", "pair_key", "cluster", "split", "speaker",
    "duration_s", "system", "model_id", "compute_type", "condition", "forced_language", "snr_db",
    "noise_type", "prompt", "denoise", "reference", "hypothesis", "detected_language",
    "n_ref", "sub", "del", "ins", "n_ref_num", "errors_num", "c_ref", "c_errors",
    "term_hits", "term_total", "repetition_loop", "proc_s", "rtf",
    "git_commit", "packages", "gpu", "timestamp",
]


@dataclass(frozen=True)
class Condition:
    forced_language: bool = True
    snr_db: float | None = None
    prompt: bool = False
    denoise: bool = False

    @property
    def name(self) -> str:
        parts = ["forced" if self.forced_language else "auto",
                 "clean" if self.snr_db is None else f"snr{self.snr_db:g}"]
        if self.prompt:
            parts.append("prompt")
        if self.denoise:
            parts.append("denoise")
        return "-".join(parts)


def prepare_audio(segment: Segment, condition: Condition, bank, seed: int = SEED,
                  data_root: Path = DATA) -> tuple[np.ndarray, str]:
    audio = load_segment(data_root / segment.audio_path, segment.start, segment.end)
    noise_type = ""
    if condition.snr_db is not None:
        noise_type, noise = pick_noise(bank, segment.segment_id, condition.snr_db, len(audio), seed)
        audio = mix_at_snr(audio, noise, condition.snr_db)
    if condition.denoise:
        import noisereduce as nr
        audio = nr.reduce_noise(y=audio, sr=SAMPLE_RATE).astype(np.float32)
    return audio, noise_type


def collect_provenance() -> dict[str, str]:
    def git(*args):
        return subprocess.run(["git", *args], capture_output=True, text=True, cwd=ROOT).stdout.strip()

    dirty = bool(git("status", "--porcelain", "--", "study_real_meetings", "backend"))
    versions = {}
    for pkg in ("torch", "faster-whisper", "ctranslate2", "transformers", "nemo-toolkit",
                "peft", "noisereduce", "num2words", "pyannote.audio"):
        try:
            versions[pkg] = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            versions[pkg] = "absent"
    import torch
    gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu"
    return {"git_commit": git("rev-parse", "HEAD") + ("-dirty" if dirty else ""),
            "packages": json.dumps(versions, sort_keys=True), "gpu": gpu}


def read_rows(path: Path) -> list[dict]:
    if not Path(path).exists():
        return []
    with open(path, encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def run(segments, transcriber, condition: Condition, *, hypothesis_id: str, out_csv: Path,
        bank=None, provenance: dict[str, str], seed: int = SEED, data_root: Path = DATA) -> int:
    out_csv = Path(out_csv)
    done = {(r["segment_id"], r["system"], r["condition"]) for r in read_rows(out_csv)}
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    new_file = not out_csv.exists()
    written = 0
    with open(out_csv, "a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        for seg in segments:
            if (seg.segment_id, transcriber.system, condition.name) in done:
                continue
            audio, noise_type = prepare_audio(seg, condition, bank, seed, data_root)
            result = transcriber.transcribe(
                audio, language=seg.language if condition.forced_language else None,
                prompt=DOMAIN_PROMPT if condition.prompt else None)
            words = score_words(seg.reference, result.text, seg.language)
            words_num = score_words(seg.reference, result.text, seg.language, numbers_to_words=True)
            chars = score_chars(seg.reference, result.text, seg.language)
            hits, total = term_hits(seg.reference, result.text, seg.language)
            duration = len(audio) / SAMPLE_RATE
            writer.writerow({
                "hypothesis_id": hypothesis_id, "dataset": seg.dataset, "language": seg.language,
                "segment_id": seg.segment_id, "pair_key": seg.pair_key, "cluster": seg.cluster,
                "split": seg.split, "speaker": seg.speaker, "duration_s": f"{duration:.3f}",
                "system": transcriber.system, "model_id": transcriber.model_id,
                "compute_type": transcriber.compute_type, "condition": condition.name,
                "forced_language": int(condition.forced_language),
                "snr_db": "" if condition.snr_db is None else f"{condition.snr_db:g}",
                "noise_type": noise_type, "prompt": int(condition.prompt), "denoise": int(condition.denoise),
                "reference": seg.reference, "hypothesis": result.text,
                "detected_language": result.detected_language or "",
                "n_ref": words.n_ref, "sub": words.sub, "del": words.dele, "ins": words.ins,
                "n_ref_num": words_num.n_ref, "errors_num": words_num.errors,
                "c_ref": chars.n_ref, "c_errors": chars.errors,
                "term_hits": hits, "term_total": total,
                "repetition_loop": int(has_repetition_loop(result.text, seg.language)),
                "proc_s": f"{result.seconds:.4f}",
                "rtf": f"{result.seconds / duration:.4f}" if duration else "",
                **provenance, "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            })
            handle.flush()
            written += 1
    return written
```

- [ ] **Step 4: Run to verify pass**

Run: `.venv\Scripts\python.exe -m pytest tests/test_rm_runner.py -q`
Expected: 3 passed, 5 deselected (gpu).

- [ ] **Step 5: Commit**

```powershell
git add study_real_meetings/runner.py tests/test_rm_runner.py
git commit -F <msgfile>   # "feat(study): condition runner with resumable provenance-rich CSV"
```

---

### Task 8: Statistics (corpus WER, clustered bootstrap, Holm)

**Files:**
- Create: `study_real_meetings/stats.py`
- Test: `tests/test_rm_stats.py`

**Interfaces:**
- Produces:
  - `Estimate(estimate, ci_low, ci_high, p_value, n_segments, n_clusters)` (frozen dataclass; `p_value` is NaN for single-system intervals)
  - `corpus_wer(errors, n_ref) -> float`
  - `cluster_bootstrap_wer(errors, n_ref, clusters, *, n_resamples=N_BOOTSTRAP, seed=SEED) -> Estimate`
  - `paired_wer_difference(errors_a, errors_b, n_ref, clusters, *, n_resamples, seed) -> Estimate` (A − B)
  - `unpaired_wer_difference(errors_a, n_a, clusters_a, errors_b, n_b, clusters_b, *, n_resamples, seed) -> Estimate` (A − B)
  - `holm(p_values: dict[str, float], alpha=ALPHA) -> dict[str, tuple[float, bool]]` (adjusted p, reject)

- [ ] **Step 1: Write the failing tests**

`tests/test_rm_stats.py`:

```python
import math

import pytest

from study_real_meetings.stats import (
    cluster_bootstrap_wer,
    corpus_wer,
    holm,
    paired_wer_difference,
    unpaired_wer_difference,
)


def test_corpus_wer_is_total_errors_over_total_words():
    assert corpus_wer([1, 3], [10, 30]) == pytest.approx(0.1)


def test_identical_systems_have_zero_difference_and_p_one():
    e = [1, 2, 0, 3, 1, 2]
    est = paired_wer_difference(e, e, [10] * 6, list("aabbcc"), n_resamples=500, seed=1)
    assert (est.estimate, est.ci_low, est.ci_high) == (0.0, 0.0, 0.0)
    assert est.p_value == pytest.approx(1.0)
    assert est.n_clusters == 3


def test_consistently_worse_system_is_detected():
    clusters = [f"c{i // 2}" for i in range(40)]
    est = paired_wer_difference([5] * 40, [1] * 40, [10] * 40, clusters, n_resamples=2000, seed=1)
    assert est.estimate == pytest.approx(0.4)
    assert est.ci_low > 0 and est.p_value < 0.01


def test_single_system_interval_contains_estimate():
    est = cluster_bootstrap_wer([1, 2, 3, 4], [10, 10, 10, 10], ["a", "a", "b", "b"], n_resamples=500, seed=1)
    assert est.ci_low <= est.estimate <= est.ci_high and math.isnan(est.p_value)


def test_unpaired_difference_between_groups():
    est = unpaired_wer_difference([3] * 10, [10] * 10, [f"a{i}" for i in range(10)],
                                  [1] * 10, [10] * 10, [f"b{i}" for i in range(10)],
                                  n_resamples=500, seed=1)
    assert est.estimate == pytest.approx(0.2) and est.ci_low == pytest.approx(0.2)


def test_holm_step_down():
    out = holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert out["a"] == (pytest.approx(0.03), True)
    assert out["c"] == (pytest.approx(0.06), False)
    assert out["b"] == (pytest.approx(0.06), False)
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv\Scripts\python.exe -m pytest tests/test_rm_stats.py -q`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement**

`study_real_meetings/stats.py`:

```python
"""Corpus-level WER with cluster bootstrap.

Corpus WER = total errors / total reference words (not the mean of per-segment WER),
the standard ASR convention. Clusters (meeting x speaker, or 2-minute AGM blocks)
are resampled because segments inside a cluster are not independent.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from study_real_meetings.config import ALPHA, N_BOOTSTRAP, SEED


@dataclass(frozen=True)
class Estimate:
    estimate: float
    ci_low: float
    ci_high: float
    p_value: float
    n_segments: int
    n_clusters: int


def corpus_wer(errors, n_ref) -> float:
    return float(np.sum(errors)) / float(np.sum(n_ref))


def _cluster_sums(clusters, *columns):
    labels = sorted(set(clusters))
    index = {label: i for i, label in enumerate(labels)}
    sums = np.zeros((len(columns), len(labels)))
    for row, label in enumerate(clusters):
        for c, column in enumerate(columns):
            sums[c, index[label]] += column[row]
    return sums


def _p_two_sided(boot: np.ndarray) -> float:
    n = len(boot)
    below = (np.sum(boot <= 0) + 1) / (n + 1)
    above = (np.sum(boot >= 0) + 1) / (n + 1)
    return float(min(1.0, 2 * min(below, above)))


def cluster_bootstrap_wer(errors, n_ref, clusters, *, n_resamples=N_BOOTSTRAP, seed=SEED) -> Estimate:
    e, n = _cluster_sums(list(clusters), list(errors), list(n_ref))
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, e.size, size=(n_resamples, e.size))
    boot = e[idx].sum(axis=1) / n[idx].sum(axis=1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return Estimate(corpus_wer(errors, n_ref), float(lo), float(hi), math.nan, len(list(errors)), e.size)


def paired_wer_difference(errors_a, errors_b, n_ref, clusters, *, n_resamples=N_BOOTSTRAP, seed=SEED) -> Estimate:
    ea, eb, n = _cluster_sums(list(clusters), list(errors_a), list(errors_b), list(n_ref))
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n.size, size=(n_resamples, n.size))
    boot = (ea[idx].sum(axis=1) - eb[idx].sum(axis=1)) / n[idx].sum(axis=1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    point = (float(np.sum(errors_a)) - float(np.sum(errors_b))) / float(np.sum(n_ref))
    return Estimate(point, float(lo), float(hi), _p_two_sided(boot), len(list(n_ref)), n.size)


def unpaired_wer_difference(errors_a, n_a, clusters_a, errors_b, n_b, clusters_b, *,
                            n_resamples=N_BOOTSTRAP, seed=SEED) -> Estimate:
    ea, na = _cluster_sums(list(clusters_a), list(errors_a), list(n_a))
    eb, nb = _cluster_sums(list(clusters_b), list(errors_b), list(n_b))
    rng = np.random.default_rng(seed)
    ia = rng.integers(0, na.size, size=(n_resamples, na.size))
    ib = rng.integers(0, nb.size, size=(n_resamples, nb.size))
    boot = ea[ia].sum(axis=1) / na[ia].sum(axis=1) - eb[ib].sum(axis=1) / nb[ib].sum(axis=1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    point = corpus_wer(errors_a, n_a) - corpus_wer(errors_b, n_b)
    return Estimate(point, float(lo), float(hi), _p_two_sided(boot),
                    len(list(n_a)) + len(list(n_b)), na.size + nb.size)


def holm(p_values: dict[str, float], alpha: float = ALPHA) -> dict[str, tuple[float, bool]]:
    order = sorted(p_values, key=p_values.get)
    m = len(order)
    out: dict[str, tuple[float, bool]] = {}
    running = 0.0
    for rank, key in enumerate(order):
        running = max(running, min(1.0, (m - rank) * p_values[key]))
        out[key] = (running, running <= alpha)
    return out
```

- [ ] **Step 4: Run to verify pass**

Run: `.venv\Scripts\python.exe -m pytest tests/test_rm_stats.py -q`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```powershell
git add study_real_meetings/stats.py tests/test_rm_stats.py
git commit -F <msgfile>   # "feat(study): corpus-WER cluster bootstrap (paired/unpaired) and Holm correction"
```

---

### Task 9: Reference checks and protocol freeze

**Files:**
- Create: `study_real_meetings/scripts/reference_checks.py`
- Create: `study_real_meetings/PROTOCOL.md`
- Create: `study_real_meetings/manifests.sha256`
- Create: `results/real_meetings/agm_spotcheck.csv` (filled in by the author), `results/real_meetings/agm_de_caption_checks.csv`

**Interfaces:**
- Consumes: manifests from Task 5, `load_segment`, `write_wav`, `stable_rng`.
- Produces: the frozen protocol. **No test-split run may start before this commit.**

- [ ] **Step 1: Write the reference-check script**

`study_real_meetings/scripts/reference_checks.py`:

```python
"""(1) Spot-check sheet: 20 random AGM test segments per language (FR, EN), with clips to listen to.
(2) Automatic AGM-DE caption checks: speech rate per segment and coverage vs EN/FR."""
from __future__ import annotations

import csv

from study_real_meetings import config as C
from study_real_meetings.audio import load_segment, wav_duration, write_wav
from study_real_meetings.manifest import read_manifest
from study_real_meetings.noise import stable_rng


def main() -> None:
    segs = [s for s in read_manifest(C.MANIFESTS / "agm.jsonl") if s.split == "test"]
    C.RESULTS.mkdir(parents=True, exist_ok=True)
    sheet = C.RESULTS / "agm_spotcheck.csv"
    if not sheet.exists():  # never overwrite the author's verdicts
        rows = []
        for lang in ("fr", "en"):
            pool = [s for s in segs if s.language == lang]
            picks = stable_rng(C.SEED, "spotcheck", lang).choice(len(pool), size=20, replace=False)
            for i in sorted(picks):
                s = pool[int(i)]
                write_wav(C.SPOTCHECK / f"{s.segment_id}.wav", load_segment(C.DATA / s.audio_path, s.start, s.end))
                rows.append({"segment_id": s.segment_id, "language": lang, "start": s.start, "end": s.end,
                             "reference": s.reference, "verdict": "", "notes": ""})
        with open(sheet, "w", encoding="utf-8", newline="") as h:
            w = csv.DictWriter(h, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    out = C.RESULTS / "agm_de_caption_checks.csv"
    with open(out, "w", encoding="utf-8", newline="") as h:
        w = csv.writer(h)
        w.writerow(["language", "segments", "words", "speech_s", "words_per_s", "coverage", "flagged_segments"])
        for lang in C.AGM_LANGUAGES:
            ls = [s for s in segs if s.language == lang]
            words = sum(len(s.reference.split()) for s in ls)
            speech = sum(s.duration for s in ls)
            flagged = sum(1 for s in ls if not 0.5 <= len(s.reference.split()) / s.duration <= 4.5)
            total = wav_duration(C.AUDIO / "agm" / f"agm_{lang}.wav") - C.DEV_SECONDS
            w.writerow([lang, len(ls), words, f"{speech:.1f}", f"{words / speech:.2f}", f"{speech / total:.3f}", flagged])
    print(f"Spot-check sheet: {sheet}\nClips: {C.SPOTCHECK}\nDE checks: {out}")


if __name__ == "__main__":
    main()
```

Run: `.venv\Scripts\python.exe -m study_real_meetings.scripts.reference_checks`
Expected: 40 clips in `datasets/real_meetings/spotcheck/` and two CSVs in `results/real_meetings/`.

- [ ] **Step 2: Human step: the author fills the spot-check sheet (about 30 min)**

For each row of `results/real_meetings/agm_spotcheck.csv`, play `datasets/real_meetings/spotcheck/<segment_id>.wav`, compare with `reference`, and write `verdict` = `verbatim` | `minor` (hesitations or punctuation-level wording) | `major` (missing or different words), plus `notes`. Report the verbatim rate per language in PROTOCOL §3. If more than 25 % are `major` in a language, AGM claims in that language are restricted to *relative* comparisons (same reference for all systems). Record that in PROTOCOL §9.

- [ ] **Step 3: Write and freeze PROTOCOL.md**

Create `study_real_meetings/PROTOCOL.md` from the template below. Values in `<…>` come from the data-build printout and the reference checks. Every other value is fixed by `config.py`.

```markdown
# PROTOCOL: Real-Meetings Validation Study (frozen <YYYY-MM-DD>, commit <hash>)

Pre-registration of the study described in `docs/specs/2026-10-10-real-meetings-study-design.md`.
Nothing below may change after this commit; changes go to §9 "Deviations" with date and reason.

## 1. Questions and hypotheses
H1, H2, H3, H4a, H4b, H4c, H4d, H5, D1: exactly as in spec §5.

## 2. Data (manifests checksummed in `manifests.sha256`)
| Manifest | Segments (all / test) | Hours | Clusters |
|---|---|---|---|
| agm | <n> / <n> | <h> | 2-min blocks per language |
| ami-ihm | <n> / <n> | <h> | meeting × speaker (meetings EN2002a, ES2004a, IS1009a, TS3003a) |
| ami-sdm | same utterances as ami-ihm (paired by pair_key) | | |
| summre | <n> / <n> | <h> | meeting × participant (018a_EARZ, 032b_EADH, 069c_EEPL) |
| noise | 30 / 30 | 0.08 | DEMAND environment |
Segmentation: caption/IPU units merged to target 15 s, max 20 s, max gap 2 s, padding 0.15 s.
AMI: official utterances, 1–30 s. Dev = first 180 s of each source cluster; test = the rest.

## 3. Reference quality
AGM FR verbatim rate: <x>/20 (minor <y>, major <z>). AGM EN: <x>/20 (...).
AGM DE: publisher captions, partially verified (automatic checks: `results/real_meetings/agm_de_caption_checks.csv`).
AMI and SUMM-RE: published human gold transcripts.

## 4. Systems and decoding
whisper-small, whisper-large-v3 (faster-whisper 1.2.1, CT2 4.6.0, fp16; beam 5, temperature 0 with
no fallback, condition_on_previous_text=False, no VAD); mms-1b-all (greedy CTC, language adapter);
conformer-ctc-large (NeMo stt_{en,fr,de}_conformer_ctc_large, greedy CTC);
hf-whisper-small and hf-whisper-small-lora (transformers, adapter models/lora_small_minds14, beam 5).
CTC systems always receive the language. Whisper receives it in "forced" conditions only.

## 5. Conditions
Noise: DEMAND OMEETING / OOFFICE / PCAFETER (channel 1), one environment and offset per
(segment, SNR) drawn with seed 20261010; SNR 20 / 10 / 5 dB. Denoising: noisereduce spectral gating
per segment. Prompt: the thesis domain prompt (identical text). Streaming (H5): fixed chunks of
1/2/5/10/20 s, no overlap, no context carry-over.

## 6. Metrics
Primary: corpus WER = Σ(S+D+I)/ΣN, thesis normaliser + filler removal (lists in config.py).
Secondary: WER with the digits→words rule (num2words), CER, Nestlé-term recall (10 terms, config.py),
repetition-loop rate (a 4-gram repeated ≥ 3 times), insertions on noise-only clips, DER
(collar 0.25 s, overlap scored), RTF, streaming latency (p50/p95).

## 7. Statistics
95 % CIs by cluster bootstrap (10 000 resamples, seed 20261010). Primary comparisons (Holm, α = 0.05):
P1–P3 H1 large-v3 vs conformer (AGM forced-clean; de, en, fr) · P4 H2 large-v3 forced-snr10 vs
forced-clean (AGM) · P5 H2 large-v3 SDM vs IHM (AMI, paired by pair_key) · P6 H3 large-v3 AMI-IHM
vs AGM-EN (unpaired) · P7 H3 large-v3 SUMM-RE vs AGM-FR (unpaired) · P8 H4a large-v3 auto vs forced
(AGM snr5 + AMI-SDM + SUMM-RE, pooled) · P9 H4d hf-small-lora vs hf-small (AMI-IHM + SUMM-RE, pooled).
Everything else is exploratory (CIs, no significance claims).

## 8. Decision rules
H5 operating point: the smallest chunk whose DEV WER is within 1 point (absolute) of the 20 s chunk,
per system; reported on TEST. Stop rule: everything not run by the end of week 2 → "future work".

## 9. Deviations
- 2026-10-10 (planning): D1 on SUMM-RE instead of AMI, reported per meeting without CI; H5 on AGM only;
  DEMAND instead of MUSAN; optional sources (Senate, investor call, YouTube auto-captions) not run
  (reasons: plan "Deviations" section).
```

Then write the checksums and freeze:

```powershell
.venv\Scripts\python.exe -c "import hashlib,pathlib; m=pathlib.Path('datasets/real_meetings/manifests'); print('\n'.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}' for p in sorted(m.glob('*.jsonl'))))" | Out-File -Encoding ascii study_real_meetings\manifests.sha256
git add study_real_meetings/PROTOCOL.md study_real_meetings/manifests.sha256 study_real_meetings/scripts/reference_checks.py results/real_meetings/agm_spotcheck.csv results/real_meetings/agm_de_caption_checks.csv
git commit -F <msgfile>   # "docs(study): freeze PROTOCOL.md and manifest checksums (pre-registration)"
git tag -a protocol-frozen -m "Real-meetings protocol frozen before any test-split run"
```

---

### Task 10: Experiment plans and the experiment CLI

**Files:**
- Create: `study_real_meetings/plans.py`, `study_real_meetings/scripts/run_experiments.py`
- Test: `tests/test_rm_plans.py`

**Interfaces:**
- Consumes: `Condition`, `run`, `collect_provenance`, `make_transcriber`, `release`, `read_manifest`, `load_demand_bank`.
- Produces: `Job(hypothesis_id: str, system: str, datasets: tuple[str, ...], condition: Condition)`, `PLANS: dict[str, list[Job]]`, `jobs_for(plan: str) -> list[Job]` (`"ALL"` = all plans, deduplicated, ordered by system).

- [ ] **Step 1: Write the failing tests**

`tests/test_rm_plans.py`:

```python
from study_real_meetings.plans import PLANS, jobs_for
from study_real_meetings.runner import Condition


def test_h1_runs_all_four_systems_forced_clean_on_agm():
    systems = {j.system for j in PLANS["H1"]}
    assert systems == {"whisper-small", "whisper-large-v3", "mms-1b-all", "conformer-ctc-large"}
    assert all(j.condition == Condition() and j.datasets == ("agm",) for j in PLANS["H1"])


def test_ctc_systems_never_run_auto_language():
    for job in jobs_for("ALL"):
        if job.system in ("mms-1b-all", "conformer-ctc-large"):
            assert job.condition.forced_language


def test_primary_comparisons_have_both_sides_scheduled():
    keys = {(j.system, d, j.condition.name) for j in jobs_for("ALL") for d in j.datasets}
    needed = [
        ("whisper-large-v3", "agm", "forced-clean"), ("conformer-ctc-large", "agm", "forced-clean"),
        ("whisper-large-v3", "agm", "forced-snr10"),
        ("whisper-large-v3", "ami-ihm", "forced-clean"), ("whisper-large-v3", "ami-sdm", "forced-clean"),
        ("whisper-large-v3", "summre", "forced-clean"),
        ("whisper-large-v3", "agm", "auto-snr5"), ("whisper-large-v3", "agm", "forced-snr5"),
        ("whisper-large-v3", "ami-sdm", "auto-clean"), ("whisper-large-v3", "summre", "auto-clean"),
        ("hf-whisper-small", "ami-ihm", "forced-clean"), ("hf-whisper-small-lora", "summre", "forced-clean"),
    ]
    assert not [k for k in needed if k not in keys]


def test_all_is_deduplicated_and_grouped_by_system():
    jobs = jobs_for("ALL")
    keys = [(j.system, j.datasets, j.condition) for j in jobs]
    assert len(keys) == len(set(keys))
    order = [j.system for j in jobs]
    assert order == sorted(order, key=order.index)  # each system's jobs are contiguous
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv\Scripts\python.exe -m pytest tests/test_rm_plans.py -q`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement the plans**

`study_real_meetings/plans.py`:

```python
"""Which (system, datasets, condition) runs each hypothesis needs. Rows are shared:
a run is identified by (segment, system, condition), so plans may overlap safely."""
from __future__ import annotations

from dataclasses import dataclass

from study_real_meetings.config import SNRS_DB
from study_real_meetings.runner import Condition

FOUR = ("whisper-small", "whisper-large-v3", "mms-1b-all", "conformer-ctc-large")
WHISPER = ("whisper-small", "whisper-large-v3")


@dataclass(frozen=True)
class Job:
    hypothesis_id: str
    system: str
    datasets: tuple[str, ...]
    condition: Condition


PLANS: dict[str, list[Job]] = {
    "H1": [Job("H1", s, ("agm",), Condition()) for s in FOUR],
    "H2": [Job("H2", s, ("agm",), Condition(snr_db=x)) for s in FOUR for x in SNRS_DB]
          + [Job("H2", s, ("ami-ihm", "ami-sdm"), Condition()) for s in FOUR],
    "H3": [Job("H3", s, ("summre",), Condition()) for s in FOUR],
    "H4a": [Job("H4a", s, ("agm",), Condition(forced_language=False, snr_db=5.0)) for s in WHISPER]
           + [Job("H4a", s, ("agm",), Condition(forced_language=False)) for s in WHISPER]
           + [Job("H4a", s, ("ami-sdm", "summre"), Condition(forced_language=False)) for s in WHISPER],
    "H4b": [Job("H4b", "whisper-large-v3", ("agm",), Condition(prompt=True))],
    "H4c": [Job("H4c", "whisper-large-v3", ("agm",), Condition(denoise=True))]
           + [Job("H4c", "whisper-large-v3", ("agm",), Condition(snr_db=x, denoise=True)) for x in SNRS_DB],
    "H4d": [Job("H4d", s, ("ami-ihm", "summre"), Condition()) for s in ("hf-whisper-small", "hf-whisper-small-lora")],
    "NOISE": [Job("NOISE", s, ("noise",), Condition()) for s in FOUR]
             + [Job("NOISE", s, ("noise",), Condition(forced_language=False)) for s in WHISPER],
}


def jobs_for(plan: str) -> list[Job]:
    selected = [j for p in PLANS for j in PLANS[p]] if plan == "ALL" else list(PLANS[plan])
    seen, unique = set(), []
    for job in selected:
        key = (job.system, job.datasets, job.condition)
        if key not in seen:
            seen.add(key)
            unique.append(job)
    order = {s: i for i, s in enumerate(dict.fromkeys(j.system for j in unique))}
    return sorted(unique, key=lambda j: order[j.system])
```

- [ ] **Step 4: Run to verify pass**

Run: `.venv\Scripts\python.exe -m pytest tests/test_rm_plans.py -q`
Expected: 4 passed.

- [ ] **Step 5: Implement the CLI**

`study_real_meetings/scripts/run_experiments.py`:

```python
"""Run one plan (or ALL) on dev, test or both. Resumable: rerun after a crash.

  .venv\\Scripts\\python.exe -m study_real_meetings.scripts.run_experiments --plan H1 --split dev --limit 5
"""
from __future__ import annotations

import argparse

from study_real_meetings import config as C
from study_real_meetings.manifest import read_manifest
from study_real_meetings.noise import load_demand_bank
from study_real_meetings.plans import PLANS, jobs_for
from study_real_meetings.runner import collect_provenance, run
from study_real_meetings.transcribers import make_transcriber, release


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, choices=[*PLANS, "ALL"])
    parser.add_argument("--split", default="test", choices=["dev", "test", "all"])
    parser.add_argument("--limit", type=int, default=0, help="max segments per dataset (smoke runs)")
    parser.add_argument("--out", default=str(C.RESULTS / "runs.csv"))
    args = parser.parse_args()

    if args.split in ("test", "all") and not (C.ROOT / "study_real_meetings" / "PROTOCOL.md").exists():
        raise SystemExit("PROTOCOL.md is not frozen yet: test-split runs are forbidden (Task 9).")
    bank = load_demand_bank(C.RAW / "demand")
    provenance = collect_provenance()
    manifests = {}
    current, transcriber = None, None
    for job in jobs_for(args.plan):
        if job.system != current:
            if transcriber is not None:
                release(transcriber)
            transcriber, current = make_transcriber(job.system), job.system
        for dataset in job.datasets:
            if dataset not in manifests:
                manifests[dataset] = read_manifest(C.MANIFESTS / f"{dataset}.jsonl")
            segs = [s for s in manifests[dataset] if args.split == "all" or s.split == args.split]
            if args.limit:
                segs = segs[: args.limit]
            n = run(segs, transcriber, job.condition, hypothesis_id=job.hypothesis_id,
                    out_csv=args.out, bank=bank, provenance=provenance)
            print(f"{job.hypothesis_id:5} {job.system:22} {dataset:8} {job.condition.name:22} +{n}")
    if transcriber is not None:
        release(transcriber)


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Commit**

```powershell
git add study_real_meetings/plans.py study_real_meetings/scripts/run_experiments.py tests/test_rm_plans.py
git commit -F <msgfile>   # "feat(study): pre-registered experiment plans and resumable CLI"
```

---

### Task 11: Streaming simulation (H5)

**Files:**
- Create: `study_real_meetings/streaming.py`, `study_real_meetings/scripts/run_streaming.py`
- Test: `tests/test_rm_streaming.py`

**Interfaces:**
- Consumes: `score_words`, `make_transcriber`, `release`, `read_manifest`, `backend.evaluation.statistics.latency_summary`.
- Produces:
  - `ChunkResult(index: int, start: float, end: float, text: str, proc_s: float)`
  - `stream_chunks(audio, transcriber, *, chunk_s: float, language: str) -> list[ChunkResult]`
  - `chunk_latencies(results: list[ChunkResult]) -> list[float]` (buffering + compute, seconds)
  - `choose_operating_point(dev_wer: dict[float, float], tolerance: float) -> float`
  - Output: `results/real_meetings/streaming.csv`

- [ ] **Step 1: Write the failing tests**

`tests/test_rm_streaming.py`:

```python
import numpy as np
import pytest

from study_real_meetings.streaming import ChunkResult, choose_operating_point, chunk_latencies, stream_chunks
from study_real_meetings.transcribers import Transcript


class Echo:
    def __init__(self):
        self.lengths = []

    def transcribe(self, audio, *, language, prompt):
        self.lengths.append(len(audio))
        return Transcript(f"w{len(self.lengths)}", language, 0.25)


def test_chunks_cover_audio_without_overlap_and_skip_tiny_tail():
    audio = np.zeros(16_000 * 4 + 800, dtype=np.float32)  # 4.05 s
    echo = Echo()
    out = stream_chunks(audio, echo, chunk_s=2.0, language="fr")
    assert echo.lengths == [32_000, 32_000]  # the 0.05 s tail (< 0.1 s) is dropped
    assert [(r.start, r.end) for r in out] == [(0.0, 2.0), (2.0, 4.0)]
    assert " ".join(r.text for r in out) == "w1 w2"


def test_short_final_chunk_is_kept():
    echo = Echo()
    out = stream_chunks(np.zeros(16_000 * 5, dtype=np.float32), echo, chunk_s=2.0, language="fr")
    assert echo.lengths == [32_000, 32_000, 16_000] and out[-1].end == 5.0


def test_latency_is_buffer_plus_compute():
    rs = [ChunkResult(0, 0.0, 2.0, "a", 0.25), ChunkResult(1, 2.0, 3.0, "b", 0.5)]
    assert chunk_latencies(rs) == pytest.approx([2.25, 1.5])


def test_operating_point_is_smallest_chunk_within_tolerance_of_20s():
    dev = {1.0: 0.30, 2.0: 0.22, 5.0: 0.205, 10.0: 0.20, 20.0: 0.20}
    assert choose_operating_point(dev, tolerance=0.01) == 5.0
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv\Scripts\python.exe -m pytest tests/test_rm_streaming.py -q`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement**

`study_real_meetings/streaming.py`:

```python
"""H5: fixed-chunk streaming. Each chunk is transcribed once it has fully arrived;
word latency ~ chunk length (buffering) + compute time for that chunk."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from study_real_meetings.config import SAMPLE_RATE

_MIN_TAIL_S = 0.1


@dataclass(frozen=True)
class ChunkResult:
    index: int
    start: float
    end: float
    text: str
    proc_s: float


def stream_chunks(audio: np.ndarray, transcriber, *, chunk_s: float, language: str) -> list[ChunkResult]:
    step = int(round(chunk_s * SAMPLE_RATE))
    results: list[ChunkResult] = []
    for index, offset in enumerate(range(0, len(audio), step)):
        chunk = audio[offset : offset + step]
        if len(chunk) < _MIN_TAIL_S * SAMPLE_RATE:
            break
        out = transcriber.transcribe(chunk, language=language, prompt=None)
        results.append(ChunkResult(index, offset / SAMPLE_RATE, (offset + len(chunk)) / SAMPLE_RATE,
                                   out.text, out.seconds))
    return results


def chunk_latencies(results: list[ChunkResult]) -> list[float]:
    return [(r.end - r.start) + r.proc_s for r in results]


def choose_operating_point(dev_wer: dict[float, float], tolerance: float) -> float:
    reference = dev_wer[max(dev_wer)]
    return min(c for c, w in dev_wer.items() if w <= reference + tolerance)
```

`study_real_meetings/scripts/run_streaming.py`:

```python
"""H5 on AGM (de/en/fr): dev window [0,180 s) chooses the chunk, test window [180 s, end) reports it."""
from __future__ import annotations

import csv

from backend.evaluation.statistics import latency_summary
from study_real_meetings import config as C
from study_real_meetings.audio import load_segment, wav_duration
from study_real_meetings.manifest import read_manifest
from study_real_meetings.runner import collect_provenance
from study_real_meetings.streaming import choose_operating_point, chunk_latencies, stream_chunks
from study_real_meetings.text import score_words
from study_real_meetings.transcribers import make_transcriber, release


def main() -> None:
    segs = read_manifest(C.MANIFESTS / "agm.jsonl")
    prov = collect_provenance()
    out = C.RESULTS / "streaming.csv"
    fields = ["system", "language", "split", "chunk_s", "n_ref", "errors", "wer", "lat_n", "lat_median",
              "lat_p95", "realtime_ok_share", "operating_point", "git_commit", "gpu"]
    rows = []
    for system in ("whisper-small", "whisper-large-v3"):
        t = make_transcriber(system)
        for lang in C.AGM_LANGUAGES:
            wav = C.AUDIO / "agm" / f"agm_{lang}.wav"
            windows = {"dev": (0.0, C.DEV_SECONDS), "test": (C.DEV_SECONDS, wav_duration(wav))}
            refs = {sp: " ".join(s.reference for s in segs if s.language == lang and s.split == sp) for sp in windows}
            dev_wer, per_split = {}, {}
            for split, (a, b) in windows.items():
                audio = load_segment(wav, a, b)
                for chunk in C.STREAM_CHUNKS_S:
                    res = stream_chunks(audio, t, chunk_s=chunk, language=lang)
                    counts = score_words(refs[split], " ".join(r.text for r in res), lang)
                    lat = latency_summary(chunk_latencies(res))
                    ok = sum(r.proc_s <= (r.end - r.start) for r in res) / len(res)
                    per_split[(split, chunk)] = (counts, lat, ok)
                    if split == "dev":
                        dev_wer[chunk] = counts.wer
            point = choose_operating_point(dev_wer, C.STREAM_TOLERANCE_WER)
            for (split, chunk), (counts, lat, ok) in per_split.items():
                rows.append({"system": system, "language": lang, "split": split, "chunk_s": chunk,
                             "n_ref": counts.n_ref, "errors": counts.errors, "wer": f"{counts.wer:.4f}",
                             "lat_n": lat["n"], "lat_median": f"{lat['median']:.3f}", "lat_p95": f"{lat['p95']:.3f}",
                             "realtime_ok_share": f"{ok:.3f}", "operating_point": int(chunk == point),
                             "git_commit": prov["git_commit"], "gpu": prov["gpu"]})
            print(system, lang, "operating point:", point)
        release(t)
    C.RESULTS.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run to verify pass**

Run: `.venv\Scripts\python.exe -m pytest tests/test_rm_streaming.py -q`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```powershell
git add study_real_meetings/streaming.py study_real_meetings/scripts/run_streaming.py tests/test_rm_streaming.py
git commit -F <msgfile>   # "feat(study): H5 fixed-chunk streaming simulation with dev-chosen operating point"
```

---

### Task 12: Diarization on real meetings (D1)

**Files:**
- Create: `study_real_meetings/diarization.py`, `study_real_meetings/scripts/run_diarization.py`
- Test: `tests/test_rm_diarization.py`

**Interfaces:**
- Produces:
  - `read_rttm(path: Path) -> pyannote.core.Annotation`
  - `der(reference: Annotation, hypothesis: Annotation, collar: float = 0.25) -> float`
  - Output: `results/real_meetings/diarization.csv` (meeting, n_speakers_ref, n_speakers_hyp, der, collar, git_commit)

- [ ] **Step 1: Write the failing tests**

`tests/test_rm_diarization.py`:

```python
import pytest
from pyannote.core import Annotation, Segment

from study_real_meetings.diarization import der, read_rttm


def test_read_rttm_and_perfect_der(tmp_path):
    p = tmp_path / "m.rttm"
    p.write_text("SPEAKER m 1 0.000 2.000 <NA> <NA> A <NA> <NA>\n"
                 "SPEAKER m 1 3.000 1.500 <NA> <NA> B <NA> <NA>\n", encoding="utf-8")
    ref = read_rttm(p)
    assert set(ref.labels()) == {"A", "B"}
    hyp = Annotation()
    hyp[Segment(0, 2)] = "spk0"  # labels differ: DER uses optimal mapping
    hyp[Segment(3, 4.5)] = "spk1"
    assert der(ref, hyp, collar=0.0) == pytest.approx(0.0)


def test_missed_speech_counts():
    ref = Annotation()
    ref[Segment(0, 4)] = "A"
    hyp = Annotation()
    hyp[Segment(0, 2)] = "x"
    assert der(ref, hyp, collar=0.0) == pytest.approx(0.5)
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv\Scripts\python.exe -m pytest tests/test_rm_diarization.py -q`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement**

`study_real_meetings/diarization.py`:

```python
"""D1: DER of pyannote on SUMM-RE meeting mixes against gold speaker turns."""
from __future__ import annotations

from pathlib import Path

from pyannote.core import Annotation, Segment as Turn
from pyannote.metrics.diarization import DiarizationErrorRate


def read_rttm(path: Path) -> Annotation:
    annotation = Annotation()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) >= 8 and parts[0] == "SPEAKER":
            start, duration = float(parts[3]), float(parts[4])
            annotation[Turn(start, start + duration)] = parts[7]
    return annotation


def der(reference: Annotation, hypothesis: Annotation, collar: float = 0.25) -> float:
    return float(DiarizationErrorRate(collar=collar, skip_overlap=False)(reference, hypothesis))
```

`study_real_meetings/scripts/run_diarization.py`:

```python
"""Run pyannote (same checkpoint as the thesis prototype) on each SUMM-RE mix."""
from __future__ import annotations

import csv
import os

import soundfile as sf
import torch
from dotenv import load_dotenv
from pyannote.audio import Pipeline

from study_real_meetings import config as C
from study_real_meetings.diarization import der, read_rttm
from study_real_meetings.runner import collect_provenance


def main() -> None:
    load_dotenv(C.ROOT / ".env")
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", token=os.getenv("HF_TOKEN"))
    pipeline.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
    prov = collect_provenance()
    rows = []
    for meeting in C.SUMMRE_MEETINGS:
        audio, sr = sf.read(str(C.AUDIO / "summre-mix" / f"{meeting}.wav"), dtype="float32")
        output = pipeline({"waveform": torch.from_numpy(audio).unsqueeze(0), "sample_rate": sr})
        hyp = getattr(output, "speaker_diarization", output)
        ref = read_rttm(C.RTTM / f"{meeting}.rttm")
        value = der(ref, hyp, collar=0.25)
        rows.append({"meeting": meeting, "n_speakers_ref": len(ref.labels()), "n_speakers_hyp": len(hyp.labels()),
                     "der": f"{value:.4f}", "collar": 0.25, "git_commit": prov["git_commit"]})
        print(rows[-1])
    with open(C.RESULTS / "diarization.csv", "w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run to verify pass**

Run: `.venv\Scripts\python.exe -m pytest tests/test_rm_diarization.py -q`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```powershell
git add study_real_meetings/diarization.py study_real_meetings/scripts/run_diarization.py tests/test_rm_diarization.py
git commit -F <msgfile>   # "feat(study): D1 diarization error rate on SUMM-RE mixes"
```

---

### Task 13: Execute the study (dev smoke run → full test runs)

**Files:**
- Produces: `results/real_meetings/runs.csv`, `streaming.csv`, `diarization.csv`
- Modify: `CHANGELOG.md`, `PROMPTS_JOURNAL.md` (one entry per run day)

This task is operational: it uses no new code. Run each command from the repo root and keep the console output in `results/real_meetings/logs/<date>_<plan>.log` (for example `... | Tee-Object -FilePath results\real_meetings\logs\2026-10-15_H1.log`).

- [ ] **Step 1: Dev smoke run (every system, 5 segments per dataset)**

```powershell
.venv\Scripts\python.exe -m study_real_meetings.scripts.run_experiments --plan ALL --split dev --limit 5 --out results\real_meetings\smoke.csv
```

Expected: one `+5` line per job, then no errors. Open `smoke.csv` and check by eye:
- `hypothesis` is in the right language for forced conditions;
- `n_ref` > 0 for every non-noise row;
- `noise_type` is filled only for `snr` conditions;
- WER for `whisper-large-v3` on `agm forced-clean` is plausible (< 30 %).

If a system produces empty or garbage text everywhere, stop and fix the adapter before running test. `smoke.csv` is not committed.

- [ ] **Step 2: Full test runs, cheapest first (resumable)**

```powershell
foreach ($p in "H1","H3","H2","H4a","H4b","H4c","H4d","NOISE") { .venv\Scripts\python.exe -m study_real_meetings.scripts.run_experiments --plan $p --split test }
.venv\Scripts\python.exe -m study_real_meetings.scripts.run_streaming
.venv\Scripts\python.exe -m study_real_meetings.scripts.run_diarization
```

Expected runtime on the RTX 4060: a few hours in total. If interrupted, rerun the same command: finished rows are skipped. **Stop rule:** if the end of week 2 arrives first, stop here and go to Task 14 with what exists.

- [ ] **Step 3: External sanity anchor**

```powershell
.venv\Scripts\python.exe -c "
import json; from study_real_meetings import config as C
from study_real_meetings.manifest import read_manifest
from study_real_meetings.sources.summre import tokens_in_span
from study_real_meetings.manifest import Unit
from study_real_meetings.text import score_words
segs=[s for s in read_manifest(C.MANIFESTS/'summre.jsonl') if s.split=='test']
E=N=0
for s in segs:
    rec=s.audio_path.split('/')[-1][:-4]
    ext=[Unit(*t) for t in json.loads((C.RAW/'summre'/'tokens'/f'{rec}.json').read_text(encoding='utf-8'))['external_whisper']]
    c=score_words(s.reference, tokens_in_span(ext, s.start, s.end), 'fr'); E+=c.errors; N+=c.n_ref
print(f'published ASRU whisper ({C.SUMMRE_EXTERNAL_WHISPER}) WER on our SUMM-RE test segments: {E/N:.3f}')
"
```

Record the number. Our `whisper-large-v3` SUMM-RE WER should be of the same order. A gap larger than 2× means something is wrong with our segmentation or normalisation: investigate before analysis.

- [ ] **Step 4: Log and commit the raw results**

Add a dated entry to `CHANGELOG.md` (runs done, row counts, any crash and how it was resumed) and to `PROMPTS_JOURNAL.md` (prompts used with Claude Code that day).

```powershell
git add results/real_meetings/runs.csv results/real_meetings/streaming.csv results/real_meetings/diarization.csv results/real_meetings/logs CHANGELOG.md PROMPTS_JOURNAL.md
git commit -F <msgfile>   # "data(study): real-meetings test runs (H1-H5, D1, noise-only)"
```

---

### Task 14: Analysis, primary tests and LaTeX tables

**Files:**
- Create: `study_real_meetings/analysis.py`, `study_real_meetings/scripts/analyse.py`
- Test: `tests/test_rm_analysis.py`
- Produces: `results/real_meetings/summary.csv`, `primary.csv`, `Memoire_LaTeX/generated/real_meetings_summary.tex`, `real_meetings_primary.tex`, `real_meetings_snr.pdf`

**Interfaces:**
- Consumes: `read_rows`, `cluster_bootstrap_wer`, `paired_wer_difference`, `unpaired_wer_difference`, `holm`, `corpus_wer`.
- Produces:
  - `summarise(rows: list[dict]) -> list[dict]` (group by dataset, language, system, condition; test split only)
  - `PRIMARY: list[Comparison]`, with `Comparison(key, hypothesis, a: Selector, b: Selector, paired_on: str | None)`, `Selector(system, condition, datasets: tuple[str, ...], language: str | None = None)`
  - `primary_tests(rows: list[dict]) -> list[dict]` (with Holm-adjusted p)
  - `to_latex(rows: list[dict], columns: list[tuple[str, str]], caption: str, label: str) -> str`

- [ ] **Step 1: Write the failing tests**

`tests/test_rm_analysis.py`:

```python
from study_real_meetings.analysis import PRIMARY, primary_tests, summarise, to_latex


def _row(system, condition, dataset, seg, errors, n=10, lang="en", split="test", pair=None, cluster=None):
    return {"system": system, "condition": condition, "dataset": dataset, "language": lang,
            "segment_id": f"{dataset}-{seg}", "pair_key": pair or f"{dataset}-{seg}",
            "cluster": cluster or f"c{seg % 4}", "split": split, "sub": str(errors), "del": "0",
            "ins": "0", "n_ref": str(n), "errors_num": str(errors), "n_ref_num": str(n),
            "c_errors": "0", "c_ref": "1", "term_hits": "0", "term_total": "0",
            "repetition_loop": "0", "rtf": "0.1", "detected_language": lang}


def test_summary_ignores_dev_and_computes_corpus_wer():
    rows = [_row("A", "forced-clean", "agm", i, 2) for i in range(8)] + [_row("A", "forced-clean", "agm", 99, 10, split="dev")]
    (s,) = summarise(rows)
    assert s["n_segments"] == 8 and abs(float(s["wer"]) - 0.2) < 1e-9


def test_primary_tests_cover_nine_comparisons_and_apply_holm():
    assert len(PRIMARY) == 9
    rows = []
    for lang in ("de", "en", "fr"):
        rows += [_row("whisper-large-v3", "forced-clean", "agm", i, 1, lang=lang) for i in range(8)]
        rows += [_row("conformer-ctc-large", "forced-clean", "agm", i, 3, lang=lang) for i in range(8)]
    out = {r["key"]: r for r in primary_tests(rows)}
    assert out["P1"]["status"] == "ok" and float(out["P1"]["estimate"]) < 0
    assert out["P5"]["status"] == "missing"
    assert "p_holm" in out["P1"]


def test_latex_table_escapes_and_has_booktabs():
    tex = to_latex([{"system": "whisper_large", "wer": "0.123"}], [("system", "System"), ("wer", "WER")], "Cap", "tab:x")
    assert "\\toprule" in tex and "whisper\\_large" in tex and "\\label{tab:x}" in tex
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv\Scripts\python.exe -m pytest tests/test_rm_analysis.py -q`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement**

`study_real_meetings/analysis.py`:

```python
"""Summary tables and the nine pre-registered primary comparisons (PROTOCOL §7)."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from study_real_meetings.stats import (
    cluster_bootstrap_wer,
    holm,
    paired_wer_difference,
    unpaired_wer_difference,
)


def _int(row, key):
    return int(row[key])


def _errors(row):
    return _int(row, "sub") + _int(row, "del") + _int(row, "ins")


def summarise(rows: list[dict]) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        if r["split"] == "test":
            groups[(r["dataset"], r["language"], r["system"], r["condition"])].append(r)
    out = []
    for (dataset, language, system, condition), rs in sorted(groups.items()):
        n_ref = [_int(r, "n_ref") for r in rs]
        summary = {"dataset": dataset, "language": language, "system": system, "condition": condition,
                   "n_segments": len(rs), "n_ref_words": sum(n_ref)}
        if sum(n_ref):
            est = cluster_bootstrap_wer([_errors(r) for r in rs], n_ref, [r["cluster"] for r in rs])
            summary |= {"wer": f"{est.estimate:.4f}", "ci_low": f"{est.ci_low:.4f}", "ci_high": f"{est.ci_high:.4f}",
                        "wer_num": f"{sum(_int(r, 'errors_num') for r in rs) / sum(_int(r, 'n_ref_num') for r in rs):.4f}",
                        "cer": f"{sum(_int(r, 'c_errors') for r in rs) / max(1, sum(_int(r, 'c_ref') for r in rs)):.4f}"}
        else:  # noise-only clips: report spurious words instead of WER
            summary |= {"wer": "", "ci_low": "", "ci_high": "", "wer_num": "", "cer": "",
                        "spurious_words_per_clip": f"{sum(_int(r, 'ins') for r in rs) / len(rs):.2f}"}
        terms_total = sum(_int(r, "term_total") for r in rs)
        summary |= {
            "term_recall": f"{sum(_int(r, 'term_hits') for r in rs) / terms_total:.3f}" if terms_total else "",
            "loop_rate": f"{sum(_int(r, 'repetition_loop') for r in rs) / len(rs):.3f}",
            "lang_mismatch_rate": f"{sum(r['detected_language'] != r['language'] for r in rs) / len(rs):.3f}",
            "median_rtf": f"{sorted(float(r['rtf']) for r in rs)[len(rs) // 2]:.4f}",
        }
        out.append(summary)
    return out


@dataclass(frozen=True)
class Selector:
    system: str
    condition: str
    datasets: tuple[str, ...]
    language: str | None = None

    def pick(self, rows):
        return [r for r in rows if r["split"] == "test" and r["system"] == self.system
                and r["condition"] == self.condition and r["dataset"] in self.datasets
                and (self.language is None or r["language"] == self.language)]


@dataclass(frozen=True)
class Comparison:
    key: str
    hypothesis: str
    a: Selector
    b: Selector
    paired_on: str | None  # "segment_id", "pair_key", or None for unpaired


L3 = "whisper-large-v3"
PRIMARY = [
    *[Comparison(f"P{i + 1}", "H1", Selector(L3, "forced-clean", ("agm",), lang),
                 Selector("conformer-ctc-large", "forced-clean", ("agm",), lang), "segment_id")
      for i, lang in enumerate(("de", "en", "fr"))],
    Comparison("P4", "H2", Selector(L3, "forced-snr10", ("agm",)), Selector(L3, "forced-clean", ("agm",)), "segment_id"),
    Comparison("P5", "H2", Selector(L3, "forced-clean", ("ami-sdm",)), Selector(L3, "forced-clean", ("ami-ihm",)), "pair_key"),
    Comparison("P6", "H3", Selector(L3, "forced-clean", ("ami-ihm",)), Selector(L3, "forced-clean", ("agm",), "en"), None),
    Comparison("P7", "H3", Selector(L3, "forced-clean", ("summre",)), Selector(L3, "forced-clean", ("agm",), "fr"), None),
    Comparison("P8", "H4a", Selector(L3, "auto-snr5", ("agm",)), Selector(L3, "forced-snr5", ("agm",)), "segment_id"),
    Comparison("P9", "H4d", Selector("hf-whisper-small-lora", "forced-clean", ("ami-ihm", "summre")),
               Selector("hf-whisper-small", "forced-clean", ("ami-ihm", "summre")), "segment_id"),
]
# P8 pools AGM snr5 with AMI-SDM and SUMM-RE "auto-clean vs forced-clean":
P8_EXTRA = (Selector(L3, "auto-clean", ("ami-sdm", "summre")), Selector(L3, "forced-clean", ("ami-sdm", "summre")))


def _paired(a_rows, b_rows, key):
    if key == "pair_key":  # IHM vs SDM live in different datasets: match on pair_key alone
        b_by = {r[key]: r for r in b_rows}
        return [(a, b_by[a[key]]) for a in a_rows if a[key] in b_by]
    b_by = {(r["dataset"], r[key]): r for r in b_rows}
    return [(a, b_by[(a["dataset"], a[key])]) for a in a_rows if (a["dataset"], a[key]) in b_by]


def primary_tests(rows: list[dict]) -> list[dict]:
    results = []
    for comp in PRIMARY:
        a_rows, b_rows = comp.a.pick(rows), comp.b.pick(rows)
        if comp.key == "P8":
            a_rows += P8_EXTRA[0].pick(rows)
            b_rows += P8_EXTRA[1].pick(rows)
        base = {"key": comp.key, "hypothesis": comp.hypothesis,
                "a": f"{comp.a.system}|{comp.a.condition}|{'+'.join(comp.a.datasets)}|{comp.a.language or 'all'}",
                "b": f"{comp.b.system}|{comp.b.condition}|{'+'.join(comp.b.datasets)}|{comp.b.language or 'all'}"}
        if not a_rows or not b_rows:
            results.append(base | {"status": "missing"})
            continue
        if comp.paired_on:
            pairs = _paired(a_rows, b_rows, comp.paired_on)
            if not pairs:
                results.append(base | {"status": "missing"})
                continue
            est = paired_wer_difference([_errors(a) for a, _ in pairs], [_errors(b) for _, b in pairs],
                                        [_int(a, "n_ref") for a, _ in pairs], [a["cluster"] for a, _ in pairs])
        else:
            est = unpaired_wer_difference([_errors(r) for r in a_rows], [_int(r, "n_ref") for r in a_rows],
                                          [r["cluster"] for r in a_rows], [_errors(r) for r in b_rows],
                                          [_int(r, "n_ref") for r in b_rows], [r["cluster"] for r in b_rows])
        results.append(base | {"status": "ok", "estimate": f"{est.estimate:.4f}", "ci_low": f"{est.ci_low:.4f}",
                               "ci_high": f"{est.ci_high:.4f}", "p_value": f"{est.p_value:.4f}",
                               "n_segments": est.n_segments, "n_clusters": est.n_clusters})
    adjusted = holm({r["key"]: float(r["p_value"]) for r in results if r["status"] == "ok"})
    for r in results:
        if r["key"] in adjusted:
            p, reject = adjusted[r["key"]]
            r |= {"p_holm": f"{p:.4f}", "reject_h0": int(reject)}
        else:
            r |= {"p_holm": "", "reject_h0": ""}
    return results


def _tex(value) -> str:
    text = str(value)
    for char, repl in (("\\", r"\textbackslash{}"), ("_", r"\_"), ("%", r"\%"), ("&", r"\&"), ("#", r"\#")):
        text = text.replace(char, repl)
    return text


def to_latex(rows: list[dict], columns: list[tuple[str, str]], caption: str, label: str) -> str:
    head = " & ".join(_tex(title) for _, title in columns)
    body = "\n".join(" & ".join(_tex(r.get(key, "")) for key, _ in columns) + r" \\" for r in rows)
    return (
        "% Generated by study_real_meetings/scripts/analyse.py. Do not edit by hand.\n"
        "\\begin{table}[htbp]\n\\centering\\small\n"
        f"\\begin{{tabular}}{{{'l' * len(columns)}}}\n\\toprule\n{head} \\\\\n\\midrule\n{body}\n"
        "\\bottomrule\n\\end{tabular}\n"
        f"\\caption{{{caption}}}\n\\label{{{label}}}\n\\end{{table}}\n"
    )
```

`study_real_meetings/scripts/analyse.py`:

```python
"""Write summary.csv, primary.csv, LaTeX tables and the WER-vs-SNR figure."""
from __future__ import annotations

import csv

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from study_real_meetings import config as C  # noqa: E402
from study_real_meetings.analysis import primary_tests, summarise, to_latex  # noqa: E402
from study_real_meetings.runner import read_rows  # noqa: E402


def _write_csv(path, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, "w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    rows = read_rows(C.RESULTS / "runs.csv")
    summary, primary = summarise(rows), primary_tests(rows)
    _write_csv(C.RESULTS / "summary.csv", summary)
    _write_csv(C.RESULTS / "primary.csv", primary)
    C.GENERATED_TEX.mkdir(parents=True, exist_ok=True)
    pct = lambda v: f"{100 * float(v):.1f}" if v not in ("", None) else "--"  # noqa: E731
    main_rows = [r | {"wer_pct": pct(r["wer"]), "ci": f"[{pct(r['ci_low'])}, {pct(r['ci_high'])}]"}
                 for r in summary if r["condition"] == "forced-clean" and r["dataset"] != "noise"]
    (C.GENERATED_TEX / "real_meetings_summary.tex").write_text(to_latex(
        main_rows, [("dataset", "Data"), ("language", "Lang."), ("system", "System"), ("n_segments", "Seg."),
                    ("wer_pct", "WER (\\%)"), ("ci", "95\\% CI")],
        "Corpus WER on real meeting and corporate audio (test split, forced language, clean).",
        "tab:rm_summary"), encoding="utf-8")
    prim_rows = [r | {"est_pct": pct(r.get("estimate", "")),
                      "ci": f"[{pct(r.get('ci_low', ''))}, {pct(r.get('ci_high', ''))}]"} for r in primary]
    (C.GENERATED_TEX / "real_meetings_primary.tex").write_text(to_latex(
        prim_rows, [("key", "Test"), ("hypothesis", "H"), ("est_pct", "$\\Delta$WER (pts)"), ("ci", "95\\% CI"),
                    ("p_holm", "$p_{\\text{Holm}}$"), ("status", "Status")],
        "Pre-registered primary comparisons (A $-$ B, cluster bootstrap, Holm-corrected).",
        "tab:rm_primary"), encoding="utf-8")
    fig, ax = plt.subplots(figsize=(5, 3.2))
    for system in ("whisper-small", "whisper-large-v3", "mms-1b-all", "conformer-ctc-large"):
        pts = []
        for label, x in (("forced-clean", 30), ("forced-snr20", 20), ("forced-snr10", 10), ("forced-snr5", 5)):
            vals = [r for r in summary if r["dataset"] == "agm" and r["system"] == system and r["condition"] == label]
            if vals:
                n = sum(int(v["n_ref_words"]) for v in vals)
                pts.append((x, 100 * sum(float(v["wer"]) * int(v["n_ref_words"]) for v in vals) / n))
        if pts:
            ax.plot(*zip(*pts), marker="o", label=system)
    ax.set_xlabel("SNR (dB); 30 = clean")
    ax.set_ylabel("WER (%)")
    ax.invert_xaxis()
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(C.GENERATED_TEX / "real_meetings_snr.pdf")
    print(f"summary: {len(summary)} groups; primary: {sum(r['status'] == 'ok' for r in primary)}/9 computed")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run to verify pass**

Run: `.venv\Scripts\python.exe -m pytest tests/test_rm_analysis.py -q`
Expected: 3 passed. Then run the whole suite: `.venv\Scripts\python.exe -m pytest -q` (all pass, gpu deselected).

- [ ] **Step 5: Run the analysis on the real results**

Run: `.venv\Scripts\python.exe -m study_real_meetings.scripts.analyse`
Expected: `summary: … groups; primary: 9/9 computed`, or fewer if the stop rule cut runs short; any `missing` comparison is reported as future work. Check by hand that one number in `summary.csv` matches a manual computation from `runs.csv`, for example Σerrors/Σn_ref for `whisper-large-v3 / agm / fr / forced-clean`.

- [ ] **Step 6: Update the source-of-truth documents and commit**

Add the headline numbers (with CIs) and the primary-test verdicts to `ETAT_ACTUEL.md` §5 and a dated `CHANGELOG.md` entry.

```powershell
git add study_real_meetings/analysis.py study_real_meetings/scripts/analyse.py tests/test_rm_analysis.py results/real_meetings/summary.csv results/real_meetings/primary.csv Memoire_LaTeX/generated ETAT_ACTUEL.md CHANGELOG.md
git commit -F <msgfile>   # "feat(study): analysis, pre-registered primary tests and generated LaTeX tables"
```

**Hand-off to week 3 (separate plan):** writing `Memoire_LaTeX/real_meetings.tex` (methods, results, threats to validity) from the generated tables; learning notes 01–10 and defense preparation follow their own short plans.
