# Task 13 runs report (test split, protocol-frozen eb080cb)

Commands: run_experiments --plan ALL --split test --system S for S in whisper-small, whisper-large-v3, conformer-ctc-large, mms-1b-all, hf-whisper-small, hf-whisper-small-lora (driver: results/real_meetings/logs/chain_test.sh, sequential, one process per system); then run_streaming, run_diarization.
Timings: whisper-small ~ several hours (night of 10-10, ends before 23:07); whisper-large-v3 23:07-00:28 (crash); conformer 00:39 end; mms 00:39-00:45; hf-whisper-small 00:45-01:04; lora 01:04-01:21; streaming attempt 1 01:21-01:47 (failed OOM); diarization 01:47-01:50 (rc 0, torchcodec DLL warnings only, DER produced); whisper-large-v3 rerun 01:50-02:57 (rc 0); streaming rerun 02:57-04:35 (rc 0).

## Crashes / retries
- whisper-large-v3 attempt 1: MemoryError "bad allocation" in ctranslate2 generate after ~1h20 (during ami-sdm auto-clean); attempts 2-4 (driver auto-retries, immediately) failed CUDA OOM at model load; conformer attempts 1-3 also failed at once (rc 1,1,127), attempt 4 succeeded. Whisper-large-v3 rerun in isolation finished OK (resumable, no duplicates).
- run_streaming attempt 1: CUDA OOM loading large-v3 after whisper-small in the same process (script loads both in one process; code not modified). Log kept as 2026-10-10_streaming_attempt1_OOM.log. Rerun alone succeeded.
- Note: GPU OOM at load recurred for ~2 retries after a prior crash; a fresh process after a pause worked. Cause not investigated (8 GB RTX).

## Integrity
- runs.csv 26,463 rows; all split=test; all git_commit = eb080cba40ab...; no -dirty; no duplicate keys.
- Rows per system: whisper-small 6580, whisper-large-v3 7595, conformer 4151, mms 4151, hf-whisper-small 1993, lora 1993.
- Per dataset/condition: agm 203, ami-ihm 1316, ami-sdm 1316, summre 677, noise 30 for every condition present; no shortfall.
- streaming.csv 60 rows (+header); diarization.csv 3 rows.

## Anchor
Published ASRU 2023 Whisper (WX_vad_noprompt) WER on our SUMM-RE test segments: 0.297. Ours whisper-large-v3 forced-clean summre (649 rows with n_ref>0): 0.301. Ratio 1.01, well within 2x.

## H5 operating points (chunk s)
whisper-small: de 10, en 10, fr 20. whisper-large-v3: de 10, en 20, fr 20.

## D1 DER (collar 0.25)
018a_EARZ 0.0786 (4/4 spk); 032b_EADH 0.2743 (ref 4, hyp 5); 069c_EEPL 0.1123 (4/4).
