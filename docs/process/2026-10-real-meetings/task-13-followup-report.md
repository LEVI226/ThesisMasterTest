# Task 13 follow-up report

Commits: 1bb42f4 (Part A, transcribers.py), f6017ba (Part B, analysis.py + tests). Smoke CSVs/logs/diag scripts NOT committed (results/real_meetings/, diag_*.py in logs/).

## Part A - MMS "CUDA out of memory" (R17)
Root cause: NOT GPU memory. The "OOM" is the host (Windows) commit limit being hit during CUDA lazy init of cuDNN/cuBLAS.
Evidence (diag_mms.py, diag2.py, diag3.py in results/real_meetings/logs):
- After load: 1096 params, all fp16 on cuda:0 (no fp32, no duplicate GPU copy), 964.8M params, memory_allocated 1841 MB; audio 1-D float32 (16.87 s); grad tracking only off inside transcribe's no_grad. GPU peak at failure 1.88 GB of 8 GB.
- Failures were varied and non-deterministic: "CUDA error: out of memory", "CUDA error: unknown error", "bad allocation", CUBLAS_STATUS_NOT_SUPPORTED, MemoryError in unrelated Python import, torch.OutOfMemoryError "tried 14 MiB, 4.9 GiB free" -> all host-allocation failures.
- Process private commit (psutil) after load BEFORE fix: 6.8 GB (start 2.2 GB; +2.4 GB from reading state dict to CPU; +2.2 GB when moving to cuda; not returned after `del state`; gc). System free virtual memory was ~7 GB, so the first real conv (lazy cuDNN/cuBLAS module load) failed.
Fix (transcribers.py, interface/decoding unchanged): _read_safetensors takes `device`; tensors are read tensor-by-tensor straight to the GPU; model built on the meta device and filled with load_state_dict(assign=True) (strict check on missing/unexpected keys), replacing from_pretrained(state_dict=...) with its CPU model.
After: commit after load 4.4 GB (-2.4 GB); GPU alloc 1841 MB.
Clip lengths (same de AGM clip tiled), peak max_memory_allocated: 3 s 1890 MB; 10 s 1978 MB; 16.87 s (the original clip) 2064 MB; 20 s 2104 MB. Transcript of the original clip: "t damen und herrennesle als unternehmen zeichnet sich seit e..." (correct German).
GPU test: `pytest tests/test_rm_runner.py -m gpu -k mms -q` -> 1 passed, 7 deselected (27 s).
Default suite: 120 passed before B.

## Part B - R16 TDD
RED: test_summary_excludes_empty_reference_rows_from_wer (wer 5.7 vs 0.2 with the 440-insertion row) and test_primary_test_ignores_empty_reference_rows both failed. GREEN after change: summarise drops n_ref==0 rows for dataset != noise, adds n_excluded_empty_ref (0 if none; groups with no remaining rows are skipped); Selector.pick excludes dataset != noise and n_ref == "0". Full suite: 122 passed.
(The primary test needed a paired partner row on the other side: an unpaired n_ref=0 row is silently dropped by pairing anyway.)

## Part C - SDM sanity (R18), diagnostic only
(1) 5 random dev ami-sdm wavs vs ihm pair (rms/peak): SDM 0.0026/0.012, 0.0049/0.025, 0.0030/0.021, 0.0044/0.029, 0.0022/0.011; IHM 0.0045/0.020, 0.0060/0.040, 0.0036/0.032, 0.0090/0.047, 0.0128/0.112. SDM is non-silent, consistently quieter (~1.2-6x lower RMS), plausible far-field levels.
(2) whisper-large-v3, forced-clean, ALL dev (smoke_sdm.csv, 375 rows), corpus WER excluding n_ref==0 (2 segments excluded):
- ami-ihm 13.5 % (136 seg, 1291 ref words)
- ami-sdm 26.6 % (same)
- agm forced-snr20 6.5 %, snr10 6.5 %, snr5 8.1 % (33 seg, 958 words)
Examples ami-sdm: REF "SO WHAT DO WE NEED TO TALK ABOUT" / HYP "So we need to talk about it."; REF "OH I DON'T MIND AS WELL" / HYP "Oh, I dropped mine as well. Give it this."; REF "THIS WASN'T A GOOD START" / HYP "This wasn't a good start."
Verdict: the 88-106 % in the smoke was a 5-clip artefact (n_ref=17 incl. 1-s "OKAY"/"UH" clips); SDM is healthy at ~2x IHM WER. No pipeline bug.

## R9 - MMS on all agm dev (smoke_mms.csv, 33 seg, forced-clean)
en 13.5 % (11 seg, 304 words), fr 18.9 % (333), de 16.2 % (321). All < 60 %: R9 PASS.
Examples (normalised hyp, lowercase unpunctuated as expected for MMS CTC):
- en REF "Ladies and gentlemen, for 160 years, Nestle has been a company defined by resilience, by r.." HYP "ladies and gentlemen for ost years nesle has been a company defined by resiliencs by reinv.."
- en REF "I step into the role of Nestle Chair with humility..." HYP "i stepp into the role of nesle' chair with humility and appreciation for this rich heritag.."
- fr REF "Mesdames et messieurs. Depuis 160 ans, Nestle est une entreprise marquee par la resilience" HYP "mesdames et messieurs depuis cent soixante ansnesley est une entreprise marquee par la resilience"
- fr REF "a creer de la valeur pour les consommateurs et la societe. C'est avec humilite et reconnaissance" HYP "cree de la valeur pour les consommateurs et lieavecumilite et reconnaissancepurcericepatr.."
- de REF "Ladies and Gentlemen. Geehrte Damen und Herren, Nestle, Nestle als Unternehmen zeichnet si.." HYP "t damen und herrennesle als unternehmen zeichnet sich seit einhundertsechzig jahren durch.."
- de REF "um fuer Konsumenten und die Gesellschaft Werte zu schaffen..." HYP "um fuer konsumenten und die gesellschaft werte zu schaffen ich trete das amt des praesidente.."
(Accents shown ASCII-folded here; console mojibake only.)
Note: the mojibake seen in the console earlier is a console-encoding artefact; CSV is UTF-8.
