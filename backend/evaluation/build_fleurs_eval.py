"""
BLOC 8 — ÉTAPE 0 + 1 : Test de chargement FLEURS + construction du sous-ensemble.

ÉTAPE 0 (gate check) :
  Vérifie que google/fleurs se charge pour en_us / fr_fr / de_de (split test)
  avec decode=False pour éviter torchcodec sur Windows.
  Si le chargement échoue → erreur explicite, arrêt.

ÉTAPE 1 :
  20 clips × 3 langues, tirage seedé (seed=42).
  WAV 16 kHz mono → datasets/fleurs_eval/audio/
  Transcripts     → datasets/fleurs_eval/references/
  Metadata CSV    → datasets/fleurs_eval/metadata.csv
                    (même format que datasets/stt_eval/metadata.csv)
"""
import io
import sys
import csv
import random
import logging
import numpy as np
import soundfile as sf
from pathlib import Path

# Fix : éviter que le dossier datasets/ local masque le package HF datasets.
_root = str(Path(__file__).resolve().parents[2])
sys.path = [p for p in sys.path if p not in ("", ".", _root)]

from datasets import load_dataset, Audio   # HF datasets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OUT_AUDIO        = Path("datasets/fleurs_eval/audio")
OUT_REFS         = Path("datasets/fleurs_eval/references")
OUT_META         = Path("datasets/fleurs_eval/metadata.csv")
SAMPLES_PER_LANG = 20
SEED             = 42
SR_TARGET        = 16_000
NOTE = (
    "FLEURS = parole lue propre, haute qualité — "
    "PAS comparable au MInDS-14 téléphonique bruité. "
    "Source : google/fleurs (CC-BY-4.0), split test."
)

LANG_MAP = {
    "en": "en_us",
    "fr": "fr_fr",
    "de": "de_de",
}


def load_audio_raw(raw: dict) -> tuple[np.ndarray, int]:
    """
    Charge l'audio depuis le dict decode=False (bytes ou path) sans torchcodec.
    Essaie soundfile d'abord (FLAC/WAV/OGG), puis librosa en fallback.
    """
    src = raw.get("bytes") or raw.get("path")
    if raw.get("bytes"):
        buf = io.BytesIO(raw["bytes"])
        try:
            arr, sr = sf.read(buf)
        except Exception:
            import librosa
            buf.seek(0)
            arr, sr = librosa.load(buf, sr=None, mono=True)
    else:
        path = raw["path"]
        try:
            arr, sr = sf.read(path)
        except Exception:
            import librosa
            arr, sr = librosa.load(path, sr=None, mono=True)
    arr = np.array(arr, dtype=np.float32)
    if arr.ndim > 1:
        arr = arr.mean(axis=1)   # stéréo → mono
    return arr, int(sr)


def resample_to(arr: np.ndarray, sr_in: int, sr_out: int) -> np.ndarray:
    if sr_in == sr_out:
        return arr
    import librosa
    return librosa.resample(arr, orig_sr=sr_in, target_sr=sr_out)


def main():
    random.seed(SEED)
    OUT_AUDIO.mkdir(parents=True, exist_ok=True)
    OUT_REFS.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict] = []

    for lang_code, hf_lang in LANG_MAP.items():

        # ── ÉTAPE 0 ────────────────────────────────────────────────────────
        logger.info("ÉTAPE 0 — Chargement google/fleurs '%s' split='test'…", hf_lang)
        try:
            ds = load_dataset(
                "google/fleurs", hf_lang,
                split="test",
                trust_remote_code=True,
            )
            ds_nodecode = ds.cast_column("audio", Audio(decode=False))
            n_total = len(ds_nodecode)
            logger.info("  OK — %d échantillons disponibles (decode=False)", n_total)
        except Exception as e:
            raise SystemExit(
                f"\n⛔  ÉTAPE 0 ÉCHOUE pour '{hf_lang}' : {e}\n"
                "    → Arrêt. Vérifiez réseau / espace disque / cache HF."
            )

        # ── ÉTAPE 1 ────────────────────────────────────────────────────────
        logger.info("ÉTAPE 1 — Sélection de %d clips (seed=%d)…", SAMPLES_PER_LANG, SEED)
        selected = random.sample(range(n_total), min(SAMPLES_PER_LANG, n_total))

        written = 0
        for write_idx, ds_idx in enumerate(selected, start=1):
            sample = ds_nodecode[ds_idx]

            # FLEURS a 'transcription' (normalisée) et 'raw_transcription'
            transcript = sample.get("transcription") or sample.get("raw_transcription", "")

            try:
                arr, sr = load_audio_raw(sample["audio"])
            except Exception as e:
                logger.warning("  Clip %d ignoré (chargement audio) : %s", ds_idx, e)
                continue

            arr = resample_to(arr, sr, SR_TARGET)

            stem     = f"fleurs_{lang_code}_clean_{write_idx:02d}"
            wav_path = OUT_AUDIO / f"{stem}.wav"
            txt_path = OUT_REFS  / f"{stem}.txt"

            sf.write(str(wav_path), arr, SR_TARGET)
            txt_path.write_text(transcript, encoding="utf-8")

            all_rows.append({
                "audio_filename":     f"{stem}.wav",
                "reference_filename": f"{stem}.txt",
                "language":           lang_code,
                "noise_condition":    "clean",
                "speaker_count":      1,
                "notes":              NOTE,
            })
            written += 1

        logger.info("  %d/%d clips sauvegardés pour '%s'", written, SAMPLES_PER_LANG, lang_code)

    # ── Metadata CSV ────────────────────────────────────────────────────────
    FIELDNAMES = [
        "audio_filename", "reference_filename", "language",
        "noise_condition", "speaker_count", "notes",
    ]
    with open(OUT_META, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(all_rows)

    dist = {}
    for r in all_rows:
        dist[r["language"]] = dist.get(r["language"], 0) + 1

    logger.info("\nÉTAPE 0+1 TERMINÉE")
    logger.info("  %d clips → %s", len(all_rows), OUT_AUDIO)
    logger.info("  Metadata → %s", OUT_META)
    logger.info("  Répartition : %s", dist)
    print("\nCHECK : PASS — FLEURS chargé et sous-ensemble construit.")


if __name__ == "__main__":
    main()
