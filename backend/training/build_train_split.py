"""
ÉTAPE 1 — Build training split sans contamination.
Charge PolyAI/MInDS-14 en-US / fr-FR / de-DE depuis HuggingFace.
Exclut tout échantillon dont le transcript normalisé correspond à
l'une des 24 références eval de datasets/stt_eval/references/.
Sélectionne 100 clips/langue par tirage aléatoire (seed=42).
Sauvegarde WAV + manifest CSV.
"""
import re
import sys
import csv
import random
import numpy as np
import soundfile as sf
from pathlib import Path

# Fix: retirer projet du sys.path pour éviter que datasets/ local
# masque le package HF datasets.
_root = str(Path(__file__).resolve().parents[2])
sys.path = [p for p in sys.path if p not in ("", ".", _root)]

from datasets import load_dataset, Audio   # HF datasets

EVAL_REFS_DIR    = Path("datasets/stt_eval/references")
TRAIN_AUDIO_DIR  = Path("datasets/lora_train/audio")
MANIFEST_CSV     = Path("datasets/lora_train/manifest.csv")
SAMPLES_PER_LANG = 100
SEED             = 42

LANG_MAP = {"en": "en-US", "fr": "fr-FR", "de": "de-DE"}


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def load_eval_refs(lang: str) -> dict[str, str]:
    """Load eval refs as {normalized → original} dict, explicit UTF-8."""
    refs = {}
    for p in sorted(EVAL_REFS_DIR.glob(f"minds14_{lang}_clean_*.txt")):
        original = p.read_text(encoding="utf-8").strip()
        refs[normalize(original)] = original
    return refs


def main():
    random.seed(SEED)
    MANIFEST_CSV.parent.mkdir(parents=True, exist_ok=True)
    all_rows     = []
    all_eval_norms: set[str] = set()

    # (a) Vérification encodage : afficher une ref DE pour confirmer que
    #     "möchte" apparaît correctement (et non "mÃ¶chte").
    de_refs = load_eval_refs("de")
    print("\n=== VÉRIFICATION ENCODAGE DE ===")
    for norm, orig in list(de_refs.items())[:3]:
        print(f"  orig: {orig!r}")
        print(f"  norm: {norm!r}")
    if any("mchte" in n for n in de_refs):
        print("  WARNING: 'ö' semble manqué dans la normalisation — vérifier.")
    else:
        print("  OK — caractères unicode présents.")

    all_eval_norms.update(de_refs.keys())

    for lang_code, hf_lang in LANG_MAP.items():
        print(f"\n[{lang_code}] Chargement MInDS-14 {hf_lang}...")
        ds = load_dataset("PolyAI/minds14", hf_lang, split="train")
        refs = load_eval_refs(lang_code)
        all_eval_norms.update(refs.keys())
        print(f"  {len(refs)} références eval chargées")

        # Itérer SANS décoder l'audio (évite torchcodec / FFmpeg DLL manquantes
        # sur Windows). On filtre uniquement par transcription textuelle.
        ds_nodecode = ds.cast_column("audio", Audio(decode=False))
        kept_indices, excluded = [], 0
        for i, sample in enumerate(ds_nodecode):
            if normalize(sample["transcription"]) in refs:
                excluded += 1
            else:
                kept_indices.append(i)

        # (b) Afficher exclusions par langue — 0 exclusion en DE = bug d'encodage.
        print(f"  {len(ds)} total → {excluded} exclus (chevauchement eval) "
              f"→ {len(kept_indices)} disponibles")
        if lang_code == "de" and excluded == 0:
            raise RuntimeError(
                "BUG D'ENCODAGE PROBABLE : 0 exclusion DE alors que "
                "les 8 références viennent du même corpus. Stop."
            )

        n = min(SAMPLES_PER_LANG, len(kept_indices))
        selected_indices = random.sample(kept_indices, n)   # tirage aléatoire, seed fixé
        lang_dir = TRAIN_AUDIO_DIR / lang_code
        lang_dir.mkdir(parents=True, exist_ok=True)

        for write_idx, ds_idx in enumerate(selected_indices):
            # Récupérer le texte depuis ds_nodecode (pas de décodage audio).
            transcription = ds_nodecode[ds_idx]["transcription"]
            # Charger l'audio du cache HF via soundfile (bypass torchcodec).
            raw = ds_nodecode[ds_idx]["audio"]
            if raw.get("bytes"):
                import io
                arr, sr = sf.read(io.BytesIO(raw["bytes"]))
            else:
                arr, sr = sf.read(raw["path"])
            arr = np.array(arr, dtype=np.float32)
            if arr.ndim > 1:
                arr = arr.mean(axis=1)   # stéréo → mono
            out = lang_dir / f"{lang_code}_{write_idx:04d}.wav"
            sf.write(str(out), arr, sr)
            all_rows.append({
                "audio_path":    str(out),
                "transcription": transcription,
                "language":      lang_code,
            })

        print(f"  {n} sélectionnés (random.sample, seed={SEED})")

    with open(MANIFEST_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["audio_path", "transcription", "language"])
        w.writeheader()
        w.writerows(all_rows)

    # (c) Assertion finale de non-contamination.
    contaminated = []
    for row in all_rows:
        n = normalize(row["transcription"])
        if n in all_eval_norms:
            contaminated.append(row["transcription"])

    if contaminated:
        raise AssertionError(
            f"CONTAMINATION DÉTECTÉE ({len(contaminated)} lignes) :\n"
            + "\n".join(contaminated[:5])
        )
    print(f"\nCONTAMINATION CHECK: PASS")
    print(f"MANIFEST: {len(all_rows)} lignes → {MANIFEST_CSV}")
    print("RÉPARTITION:", {
        lang: sum(1 for r in all_rows if r["language"] == lang)
        for lang in LANG_MAP
    })


if __name__ == "__main__":
    main()
