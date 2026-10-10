# Topic 2: live latency evidence audit

Source: `results/live_latency.csv`; 38 observations.
SHA-256: `25edc39477b5cfa33660b4fa62ffc148ca9ec9cbe9e7af5a1950dabec33f1fad`.

Sessions are inferred from utterance_id restarting at 1. The legacy CSV
does not record timestamps, model, device, load or reference transcripts.
Session comparability and live WER therefore cannot be established.

| Inferred session | Cold start (s) | Steady n | Median (s) | p95 (s) | Max (s) |
|---|---:|---:|---:|---:|---:|
| 1 | 3.612 | 1 | 0.458 | 0.458 | 0.458 |
| 2 | 2.601 | 19 | 0.557 | 0.861 | 1.177 |
| 3 | 3.519 | 15 | 0.657 | 4.814 | 11.021 |

Pooled descriptive summary: n=35, median=0.575 s, p95=1.614 s, max=11.021 s.

## Interpretation

No slow observation is discarded. The first observation in each session is
reported separately as the legacy cold-start proxy; loading itself was not isolated.
The historical 22-row study covers the first two inferred sessions only.
Appended sessions must not silently replace that study or be hidden by its summary.
The timer excludes the configured silence window and does not establish browser
render latency. Adding 0.6 s is an approximation, not a measured end-to-end result.

A new controlled run must log run/session IDs, timestamp, model/device,
endpointing configuration, final-speech time, endpoint time, server send time,
browser receipt/render time and reference/hypothesis for the SAME utterance.
Use monotonic durations; do not subtract unsynchronised client/server clocks.
Report WER and latency together, retain failures, and compare identical audio
across configurations with repeated trials. No accuracy/latency optimum is proven.
