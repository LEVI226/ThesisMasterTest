"""Targeted manuscript corrections (main_revised.tex). Historical figures untouched;
revised material lives in validation_20260916.tex. Each edit asserts a unique match."""
import pathlib, shutil
ROOT = pathlib.Path(__file__).resolve().parents[3]
P = ROOT / "Memoire_LaTeX/main_revised.tex"
BAK = pathlib.Path(__file__).parent / "pristine" / "main_revised.tex.manuscript_orig"
if not BAK.exists():
    shutil.copy2(P, BAK)
t = P.read_text(encoding="utf-8")
log = []


def sub(old, new, label):
    global t
    n = t.count(old)
    assert n == 1, f"{label}: {n} match(es)"
    t = t.replace(old, new); log.append(label)


# 1. Abstract EN: latency scope + reference-quality finding
sub("In the historical 22-observation live study, excluding first utterances yields a median server-side post-endpointing latency of 0.56\\,s and a p95 of 0.84\\,s. The extended-log audit at the end of this thesis reports additional slower observations; these historical values are not an end-to-end guarantee.",
    "In the historical 22-observation live study, excluding first utterances yields a median server-side post-endpointing latency of 0.56\\,s and a p95 of 0.84\\,s; this is computation time after the end-of-speech decision, not the caption delay, which also includes the utterance duration and is unbounded on continuous speech because the live path imposes no maximum utterance length. A post-submission audit (Annex, 16~September~2026) found seven of the sixteen English and French reference transcripts of the published corpus to be truncated or incorrect; a sensitivity revision with re-annotated references lowers absolute WER levels by roughly 10 to 15 points while preserving the model-size ordering and the noise effect, and confirms that the LoRA, prompting and aggregate forced-language contrasts all have intervals containing zero.",
    "abstract EN: latency scope, reference quality, small contrasts")

# 2. Abstract FR
sub("Le prototype WebSocket atteint, hors démarrage à froid, une latence médiane de 0{,}56\\,s et un p95 de 0{,}84\\,s après détection de fin de parole.",
    "Le prototype WebSocket atteint, hors démarrage à froid, une latence médiane de 0{,}56\\,s et un p95 de 0{,}84\\,s après détection de fin de parole ; il s'agit du temps de calcul après la décision de fin de parole, non du délai de sous-titrage, qui inclut aussi la durée de l'énoncé et n'est pas borné sur une parole continue, le chemin direct n'imposant aucune longueur maximale d'énoncé. Un audit postérieur à la soumission (annexe, 16~septembre~2026) a révélé que sept des seize références anglaises et françaises du corpus publié sont tronquées ou erronées ; une révision de sensibilité avec des références réannotées abaisse les niveaux absolus de WER d'environ 10 à 15 points en préservant l'ordre des tailles de modèle et l'effet du bruit, et confirme que les contrastes LoRA, prompt et langue forcée en agrégé ont tous des intervalles contenant zéro.",
    "abstract FR: same")

# 3. Metrics: estimator and independence
sub("The Word Error Rate (WER) is the word-level edit distance between a hypothesis and a reference transcript: the sum of substitutions, deletions and insertions divided by the number of reference words.",
    "The Word Error Rate (WER) is the word-level edit distance between a hypothesis and a reference transcript: the sum of substitutions, deletions and insertions divided by the number of reference words. Unless stated otherwise, every aggregate WER or CER in this thesis is the arithmetic mean of per-file rates over the 36 evaluation files (24 clean and 12 noisy; English, French and German), not a corpus-level rate weighted by word count; because insertions are unbounded, a per-file WER can exceed 100\\,\\%. The 12 noisy files are derived copies of 12 of the clean recordings and are never treated as independent recordings.",
    "metrics: estimator, languages, conditions, non-independence")

# 4. H4 verdict
sub("H4 is \\textbf{strongly supported}: in a genuinely multilingual deployment,",
    "H4 is \\textbf{supported at the script level}, while its aggregate WER effect is not statistically established at this sample size (post-submission interval [$-2.6$, $+7.0$] points, Annex): in a genuinely multilingual deployment,",
    "H4: script-level support, aggregate not established")

# 5. RQ3: three quantities, no max utterance length
sub("RQ3 is therefore \\emph{partially answered}: the prototype demonstrates steady-state sub-second processing after endpointing, but it does not establish optimal streaming latency without loss of accuracy.",
    "RQ3 is therefore \\emph{partially answered}: the prototype demonstrates steady-state sub-second processing after endpointing, but it does not establish optimal streaming latency without loss of accuracy. Three quantities must be kept apart: the real-time factor, this post-endpointing computation time, and the end-to-end caption delay, which additionally contains the utterance duration itself. The live handler imposes no maximum utterance length, so on continuous speech without a 0.6\\,s pause the utterance, and with it the caption delay, grows until a pause or a stop command; utterances of 70\\,s and 149\\,s were observed after submission (Annex). A low RTF is therefore not evidence of a low captioning delay.",
    "RQ3: RTF vs compute vs caption delay; no max utterance length")

# 6. Diarization: live-window limits
sub("The honest conclusion is architectural rather than metric: the diarization path works mechanically end-to-end, cross-talk remains untested (turns are sequential by construction), and a valid accuracy assessment requires real multi-speaker recordings with per-s",
    "On the live path, in addition, the speaker label is taken from the last active speaker within a 10\\,s context window and assigned to the whole utterance; labels are local to that window and no mechanism guarantees a persistent identity across windows, so a recurring label does not establish one speaker. The honest conclusion is architectural rather than metric: the diarization path works mechanically end-to-end, cross-talk remains untested (turns are sequential by construction), and a valid accuracy assessment requires real multi-speaker recordings with per-s",
    "diarization: live 10 s window, last speaker, no identity tracking")

# 7. Hypotheses revisited
sub("H4 receives the strongest qualitative support, although the missing pilot-time language labels make the 42\\,\\% French figure an inference from paired outputs rather than a direct LID accuracy measurement.",
    "H4 receives the strongest qualitative support at the script level, although the missing pilot-time language labels make the 42\\,\\% French figure an inference from paired outputs rather than a direct LID accuracy measurement, and its aggregate WER effect is not statistically established.",
    "discussion: H4 qualified")

# 8. Positioning: external comparison exists in the annex, not a benchmark
sub("no head-to-head evaluation of that service was performed here.",
    "no head-to-head evaluation of that service was performed here; a qualitative comparison on one public recording, made after submission, is reported in the Annex and is not a benchmark.",
    "positioning: annex comparison, not a benchmark")

# 9. Conclusion: LoRA/prompt wording + reference quality
sub("Prompting and LoRA each shift mean WER by approximately one point; the LoRA interval [-2.4, 5.3] spans zero, while prompting cannot be evaluated on its intended Nestl\\'e vocabulary.",
    "Prompting and LoRA each shift mean WER by approximately one point; the LoRA interval [-2.4, 5.3] spans zero, which establishes no benefit on this sample and does not show equivalence, while prompting cannot be evaluated on its intended Nestl\\'e vocabulary. A post-submission audit further showed that seven of the sixteen English and French reference transcripts of the published corpus are defective; the absolute WER levels reported above are therefore overestimates, the orderings survive a sensitivity revision, and the German references remain unverified (Annex).",
    "conclusion: LoRA wording, reference quality")

# 10. include the annex
sub("\\input{topic2_completion}\n", "\\input{topic2_completion}\n\\input{validation_20260916}\n", "include annex")

P.write_text(t, encoding="utf-8")
print("manuscript edits:", len(log))
for l in log:
    print("  -", l)
