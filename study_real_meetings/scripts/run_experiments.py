"""Run one plan (or ALL) on dev, test or both. Resumable: rerun after a crash.

  .venv/Scripts/python.exe -m study_real_meetings.scripts.run_experiments --plan H1 --split dev --limit 5
  .venv/Scripts/python.exe -m study_real_meetings.scripts.run_experiments --plan ALL --split dev --system whisper-large-v3
"""
from __future__ import annotations

import argparse
import subprocess

from study_real_meetings import config as C
from study_real_meetings.manifest import read_manifest
from study_real_meetings.noise import load_demand_bank
from study_real_meetings.plans import PLANS, jobs_for
from study_real_meetings.runner import collect_provenance, run
from study_real_meetings.transcribers import SYSTEMS, make_transcriber, release


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, choices=[*PLANS, "ALL"])
    parser.add_argument("--split", default="test", choices=["dev", "test", "all"])
    parser.add_argument("--limit", type=int, default=0, help="max segments per dataset (smoke runs)")
    parser.add_argument("--out", default=str(C.RESULTS / "runs.csv"))
    parser.add_argument("--system", default=None, choices=SYSTEMS,
                        help="run only this system (one model per process); default: all systems")
    args = parser.parse_args()

    frozen = subprocess.run(["git", "tag", "-l", "protocol-frozen"], capture_output=True, text=True,
                            cwd=C.ROOT).stdout.strip()
    if args.split in ("test", "all") and not frozen:
        raise SystemExit("Protocol not frozen (git tag 'protocol-frozen' missing): test-split runs are forbidden (Task 9).")

    jobs = jobs_for(args.plan)
    if args.system is not None:
        jobs = [j for j in jobs if j.system == args.system]
        if not jobs:
            print(f"No jobs for plan {args.plan} and system {args.system}; nothing to do.")
            return

    bank = load_demand_bank(C.RAW / "demand")
    provenance = collect_provenance()
    manifests = {}
    current, transcriber = None, None
    for job in jobs:
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
