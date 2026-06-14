"""
Generates a Markdown evaluation report from STT results CSV.
Thesis-ready format with tables, findings, and interpretations.
"""
import csv
import math
from collections import defaultdict
from pathlib import Path
from datetime import datetime
from typing import Optional


def _load_csv(csv_path: str) -> list[dict]:
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _safe_float(val: str) -> Optional[float]:
    try:
        v = float(val)
        return None if math.isnan(v) or math.isinf(v) else v
    except (ValueError, TypeError):
        return None


def _avg(values: list[float]) -> Optional[float]:
    clean = [v for v in values if v is not None]
    return round(sum(clean) / len(clean), 4) if clean else None


def _pct(v: Optional[float]) -> str:
    return f"{v * 100:.2f}%" if v is not None else "N/A"


def _fmt(v: Optional[float], decimals: int = 4) -> str:
    return f"{v:.{decimals}f}" if v is not None else "N/A"


def generate_report(results_csv: str, output_path: str, hardware_notes: str = "") -> str:
    """
    Generate a Markdown evaluation report from results CSV.

    Args:
        results_csv: Path to the CSV produced by run_evaluation().
        output_path: Where to write the .md report.
        hardware_notes: Optional string describing the test hardware.

    Returns:
        The generated Markdown as a string.
    """
    rows = _load_csv(results_csv)
    if not rows:
        raise ValueError(f"No results found in {results_csv}")

    # Parse numeric fields
    for row in rows:
        for key in ("wer", "cer", "real_time_factor", "duration_audio_seconds", "processing_time_seconds"):
            row[f"_{key}"] = _safe_float(row.get(key, ""))

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    model_sizes = sorted(set(r.get("model", "?") for r in rows))
    languages   = sorted(set(r.get("language", "?") for r in rows))
    conditions  = sorted(set(r.get("noise_condition", "?") for r in rows))

    lines = []
    a = lines.append

    a("# STT Evaluation Report — Topic 2")
    a(f"\n**Generated:** {now}  ")
    a(f"**Results file:** `{results_csv}`\n")

    a("---\n")
    a("## 1. Experiment Setup\n")
    a("### Objective")
    a(
        "Evaluate faster-whisper STT accuracy and efficiency across different preprocessing "
        "configurations, domain adaptation strategies, and noise conditions — "
        "in support of Master Thesis Topic 2: *Advanced Speech-to-Text Models for "
        "Noisy, Multilingual Corporate Meetings*.\n"
    )
    a("### Evaluation Conditions")
    a("| Condition Label | Preprocessing | Domain Prompt | Language |")
    a("|---|---|---|---|")
    cond_labels = {}
    for row in rows:
        key = (row["preprocessing_enabled"], row["domain_prompt_enabled"], row["forced_language"])
        if key not in cond_labels:
            label = f"C{len(cond_labels)+1}"
            cond_labels[key] = label
            prep  = "Yes" if row["preprocessing_enabled"] == "True" else "No"
            prompt= "Yes" if row["domain_prompt_enabled"]  == "True" else "No"
            lang  = row["forced_language"] if row["forced_language"] and row["forced_language"] != "None" else "Auto"
            a(f"| {label} | {prep} | {prompt} | {lang} |")
    a("")

    a("### Model Configuration")
    a(f"- **STT Engine:** faster-whisper")
    a(f"- **Model sizes tested:** {', '.join(model_sizes)}")
    a(f"- **Languages in dataset:** {', '.join(languages)}")
    a(f"- **Noise conditions:** {', '.join(conditions)}\n")

    if hardware_notes:
        a("### Hardware")
        a(hardware_notes)
        a("")

    a("---\n")
    a("## 2. Metrics Reference\n")
    a("| Metric | Formula | Interpretation |")
    a("|---|---|---|")
    a("| **WER** | (S+D+I) / N_ref_words | 0 = perfect; lower is better |")
    a("| **CER** | (S+D+I) / N_ref_chars | Stricter than WER; lower is better |")
    a("| **RTF** | processing_time / audio_duration | <1 = faster than real-time (good) |")
    a("")

    a("---\n")
    a("## 3. Results Table\n")
    a("| File | Language | Noise | Model | Prep | Prompt | Lang | WER | CER | RTF | Time (s) |")
    a("|---|---|---|---|---|---|---|---|---|---|---|")
    for row in rows:
        prep  = "✓" if row["preprocessing_enabled"] == "True" else "✗"
        prompt= "✓" if row["domain_prompt_enabled"]  == "True" else "✗"
        lang  = row.get("forced_language", "auto") or "auto"
        a(
            f"| {row['filename']} | {row['language']} | {row['noise_condition']} "
            f"| {row['model']} | {prep} | {prompt} | {lang} "
            f"| {_pct(row['_wer'])} | {_pct(row['_cer'])} "
            f"| {_fmt(row['_real_time_factor'], 3)} | {_fmt(row['_processing_time_seconds'], 1)} |"
        )
    a("")

    a("---\n")
    a("## 4. Aggregated Results by Condition\n")
    by_cond = defaultdict(list)
    for row in rows:
        key = (row["preprocessing_enabled"], row["domain_prompt_enabled"], row.get("forced_language", ""))
        by_cond[key].append(row)

    a("| Condition | n | Mean WER | Mean CER | Mean RTF |")
    a("|---|---|---|---|---|")
    for key, cond_rows in sorted(by_cond.items()):
        label = cond_labels.get(key, str(key))
        wers = [r["_wer"] for r in cond_rows]
        cers = [r["_cer"] for r in cond_rows]
        rtfs = [r["_real_time_factor"] for r in cond_rows]
        a(f"| {label} | {len(cond_rows)} | {_pct(_avg(wers))} | {_pct(_avg(cers))} | {_fmt(_avg(rtfs), 3)} |")
    a("")

    a("### Aggregated Results by Noise Condition\n")
    a("| Noise Condition | n | Mean WER | Mean CER | Mean RTF |")
    a("|---|---|---|---|---|")
    by_noise = defaultdict(list)
    for row in rows:
        by_noise[row["noise_condition"]].append(row)
    for noise, nrows in sorted(by_noise.items()):
        wers = [r["_wer"] for r in nrows]
        cers = [r["_cer"] for r in nrows]
        rtfs = [r["_real_time_factor"] for r in nrows]
        a(f"| {noise} | {len(nrows)} | {_pct(_avg(wers))} | {_pct(_avg(cers))} | {_fmt(_avg(rtfs), 3)} |")
    a("")

    a("---\n")
    a("## 5. Key Findings\n")
    a("<!-- Fill in after reviewing the data above. Example findings: -->")
    a("")
    a("1. **Preprocessing impact:** Noise reduction (noisereduce) [improved/degraded] WER by X% on noisy recordings.")
    a("2. **Domain prompt impact:** The Nestlé vocabulary prompt [reduced/had no effect on] WER for brand names.")
    a("3. **RTF performance:** The system achieved RTF < 1 on [X%] of samples, confirming faster-than-real-time performance on this hardware.")
    a("4. **Language detection accuracy:** Auto language detection [was/was not] reliable across the tested languages.")
    a("5. **Proper noun limitation:** Names such as 'Navratil' were transcribed incorrectly, highlighting the need for fine-tuning.\n")

    a("---\n")
    a("## 6. Limitations\n")
    a("- Evaluation dataset is small (see `datasets/stt_eval/README.md` for instructions on adding files).")
    a("- Reference transcripts may contain stylistic differences not accounted for by WER normalization.")
    a("- Diarization quality (speaker labelling) was not evaluated due to dataset constraints.")
    a("- All results obtained on local hardware; GPU performance will differ on Azure NC-series VMs.\n")

    a("---\n")
    a("## 7. Thesis Interpretation\n")
    a(
        "These results constitute the empirical foundation for Topic 2. "
        "The comparison across preprocessing conditions directly addresses **Research Question 1** "
        "(*How can STT models be optimized for noisy corporate environments?*). "
        "The domain prompt experiments address **Research Question 2** "
        "(*What fine-tuning strategies best adapt STT to Nestlé-specific vocabulary?*). "
        "The RTF measurements address **Research Question 3** "
        "(*How can real-time transcription latency be minimized?*).\n"
    )
    a("The next step is to run these experiments on a GPU-enabled Azure NC-series VM and compare RTF values.")

    report_text = "\n".join(lines)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(report_text, encoding="utf-8")
    return report_text
