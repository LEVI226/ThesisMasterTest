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
