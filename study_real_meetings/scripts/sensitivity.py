"""EXPLORATORY post-freeze sensitivity analyses -> results/real_meetings/sensitivity.csv (PROTOCOL §9)."""
from __future__ import annotations

import csv

from study_real_meetings import config as C
from study_real_meetings.runner import read_rows
from study_real_meetings.sensitivity import COLUMNS, sensitivity_rows


def main() -> None:
    rows = sensitivity_rows(read_rows(C.RESULTS / "runs.csv"))
    with open(C.RESULTS / "sensitivity.csv", "w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"sensitivity: {len(rows)} rows (exploratory_post_freeze)")


if __name__ == "__main__":
    main()
