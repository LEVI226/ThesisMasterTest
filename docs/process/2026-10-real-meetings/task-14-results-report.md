# Task 14 results report (steps 5-6)

analyse output: `summary: 101 groups; primary: 9/9 computed`. No code changed. Default tests: 122 passed.

## Hand checks
(a) runs.csv, whisper-large-v3 / agm / fr / forced-clean / test / n_ref>0: 68 rows, sum(sub+del+ins)/sum(n_ref) = 0.10514 ; summary.csv wer = 0.1051. OK.
(b) Pooled recomputation from runs.csv: P1 per-language WER difference de -0.0577 (0.0916-0.1493; CSV -0.0576), en -0.0535, fr -0.0498 (exact); P4 +0.00075 (CSV 0.0008); P5 0.393-0.175 = +0.218; P6 0.175-0.0432 = +0.1318; P7 0.3012-0.1051 = +0.1961 (CSV 0.1960); P8 pooled (AGM snr5 + AMI-SDM/SUMM-RE auto-clean vs forced; 2152 rows each) +0.03445 (CSV 0.0344); P9 pooled AMI-IHM+SUMM-RE -0.10086 (CSV -0.1009). All signs and magnitudes agree.
(c) LaTeX: no `\textbackslash` in the .tex files (grep count 0); headers use `$\Delta$WER (pts)` and `$p_{\text{Holm}}$`. No pdflatex/lualatex on PATH: compile check skipped.

## primary.csv
key,hypothesis,a,b,status,estimate,ci_low,ci_high,p_value,n_segments,n_clusters,holm_m,p_holm,reject_h0
P1,H1,whisper-large-v3|forced-clean|agm|de,conformer-ctc-large|forced-clean|agm|de,ok,-0.0576,-0.0668,-0.0481,0.0002,69,11,9,0.0018,1
P2,H1,whisper-large-v3|forced-clean|agm|en,conformer-ctc-large|forced-clean|agm|en,ok,-0.0535,-0.0740,-0.0322,0.0002,66,10,9,0.0018,1
P3,H1,whisper-large-v3|forced-clean|agm|fr,conformer-ctc-large|forced-clean|agm|fr,ok,-0.0498,-0.0981,0.0114,0.1030,68,11,9,0.2060,0
P4,H2,whisper-large-v3|forced-snr10|agm|all,whisper-large-v3|forced-clean|agm|all,ok,0.0008,-0.0084,0.0082,0.8215,203,32,9,0.8215,0
P5,H2,whisper-large-v3|forced-clean|ami-sdm|all,whisper-large-v3|forced-clean|ami-ihm|all,ok,0.2180,0.1600,0.2764,0.0002,1300,16,9,0.0018,1
P6,H3,whisper-large-v3|forced-clean|ami-ihm|all,whisper-large-v3|forced-clean|agm|en,ok,0.1318,0.0977,0.1665,0.0002,1366,26,9,0.0018,1
P7,H3,whisper-large-v3|forced-clean|summre|all,whisper-large-v3|forced-clean|agm|fr,ok,0.1960,0.1316,0.2487,0.0002,717,23,9,0.0018,1
P8,H4a,whisper-large-v3|auto-snr5|agm|all,whisper-large-v3|forced-snr5|agm|all,ok,0.0344,0.0103,0.0672,0.0002,2152,60,9,0.0018,1
P9,H4d,hf-whisper-small-lora|forced-clean|ami-ihm+summre|all,hf-whisper-small|forced-clean|ami-ihm+summre|all,ok,-0.1009,-0.1903,-0.0292,0.0016,1949,28,9,0.0048,1

## whisper-large-v3 forced-clean headline (summary.csv)
dataset language  n_segments  n_ref_words  n_excluded_empty_ref    wer  ci_low  ci_high
    agm       de          69         2117                     0 0.0916  0.0704   0.1120
    agm       en          66         2037                     0 0.0432  0.0286   0.0600
    agm       fr          68         2511                     0 0.1051  0.0614   0.1684
ami-ihm       en        1300        11594                    16 0.1750  0.1447   0.2059
ami-sdm       en        1300        11594                    16 0.3930  0.3086   0.4769
 summre       fr         649        13063                    28 0.3012  0.2769   0.3283

## Surprising / to flag
- P3 (fr) CI includes 0 (p_holm 0.206). P8 positive pooled (+3.4 pts) although AGM snr5 alone is auto 0.0812 vs forced 0.0786 (+0.25 pt): the pooled estimate includes AMI-SDM and SUMM-RE auto-clean vs forced-clean.
- D1: 032b_EADH DER 0.2743 (5 hyp speakers vs 4 ref) vs 0.0786 and 0.1123.
- Excluded empty refs: AMI-IHM 16, AMI-SDM 16, SUMM-RE 28 per condition, AGM 0.
- Anchor: ASRU 0.297 vs ours 0.301.
