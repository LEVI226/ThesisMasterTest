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
