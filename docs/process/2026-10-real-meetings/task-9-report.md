# Task 9 (part 1) report
Script run OK: 40 clips in datasets/real_meetings/spotcheck/, agm_spotcheck.csv (verdict/notes empty), agm_de_caption_checks.csv.
DE checks (test): de 69 seg, 1.90 w/s, cov 0.969, 0 flagged; en 66, 1.83, 0.966, 1 flagged; fr 68, 2.19, 0.997, 0 flagged.
Sec.2 numbers (read_manifest; hours = sum duration/3600; clusters = distinct .cluster; all/test):
agm 236/203, 1.10/0.94 h, 35/32; ami-ihm & ami-sdm 1454/1316, 1.35/1.20 h, 16/16; summre 757/677, 1.29/1.14 h, 12/12; noise 30/30, 0.08 h, 3/3.
PROTOCOL.md is DRAFT (R11, R14, R12, R8, R2 lines added). No manifests.sha256, no tag. Tests: 120 passed.
Concern: AGM cluster count is 35 all / 32 test (I report distinct values, not the "2-min blocks" nominal).
