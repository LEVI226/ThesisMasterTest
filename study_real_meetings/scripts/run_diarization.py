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
