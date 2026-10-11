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
