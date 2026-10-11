"""Final wording corrections: chronology, re-annotated references, forced-language nuance.
Applies to main_revised.tex and validation_20260916.tex. Figures untouched. LF preserved."""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[3]
log = []


def patch(rel, pairs):
    p = ROOT / rel
    t = p.read_bytes().decode("utf-8")
    for old, new, label in pairs:
        n = t.count(old)
        assert n == 1, f"{rel} [{label}]: {n} match(es)"
        t = t.replace(old, new); log.append(f"{p.name}: {label}")
    p.write_bytes(t.replace("\r\n", "\n").encode("utf-8"))


EN_AUDIT = "supplementary audit conducted on 16~September~2026"
FR_AUDIT = "audit complémentaire du 16~septembre~2026"
EN_FORCE = "Forcing the language can help when the expected language is known and stable, but it does not resolve language changes within a single intervention"
FR_FORCE = "Forcer la langue peut aider lorsque la langue attendue est connue et stable, mais ne résout pas les changements de langue au sein d'une même intervention"

patch("Memoire_LaTeX/main_revised.tex", [
    # --- abstract EN
    ("Forcing the language repairs several wrong-script outputs at no measurable computational cost. Model size remains",
     "Forcing the language repairs several wrong-script outputs at no measurable computational cost; it can help when the expected language is known and stable, but it does not resolve language changes within a single intervention. Model size remains",
     "abstract EN: forced-language nuance"),
    ("A post-submission audit (Annex, 16~September~2026) found seven of the sixteen English and French reference transcripts of the published corpus to be truncated or incorrect;",
     f"A {EN_AUDIT} (Annex) found that seven of the sixteen English and French reference transcripts differ after re-annotation, two of them only in audible hesitations, with some passages remaining uncertain;",
     "abstract EN: chronology + references wording"),
    # --- abstract FR
    ("Forcer la langue corrige plusieurs sorties en mauvais alphabet sans coût de calcul mesurable. La taille du modèle reste",
     "Forcer la langue corrige plusieurs sorties en mauvais alphabet sans coût de calcul mesurable ; cela peut aider lorsque la langue attendue est connue et stable, mais ne résout pas les changements de langue au sein d'une même intervention. La taille du modèle reste",
     "abstract FR: forced-language nuance"),
    ("Un audit postérieur à la soumission (annexe, 16~septembre~2026) a révélé que sept des seize références anglaises et françaises du corpus publié sont tronquées ou erronées ;",
     f"Un {FR_AUDIT} (annexe) a montré que sept des seize références anglaises et françaises présentent des différences après réannotation, deux d'entre elles ne portant que sur des hésitations audibles, certains passages restant incertains ;",
     "abstract FR: chronology + references wording"),
    # --- H4
    ("H4 is \\textbf{supported at the script level}, while its aggregate WER effect is not statistically established at this sample size (post-submission interval [$-2.6$, $+7.0$] points, Annex):",
     f"H4 is \\textbf{{supported at the script level}}, while its aggregate WER effect is not statistically established at this sample size (interval [$-2.6$, $+7.0$] points from the {EN_AUDIT}, Annex):",
     "H4: chronology"),
    ("forcing the expected language per speaker, channel or meeting is a zero-cost, immediately deployable mitigation.\n",
     f"forcing the expected language per speaker, channel or meeting is a zero-cost mitigation. {EN_FORCE} (Annex).\n",
     "H4: forced-language nuance"),
    # --- RQ3
    ("utterances of 70\\,s and 149\\,s were observed after submission (Annex).",
     f"utterances of 70\\,s and 149\\,s were observed in the {EN_AUDIT} (Annex).",
     "RQ3: chronology"),
    # --- positioning
    ("a qualitative comparison on one public recording, made after submission, is reported in the Annex and is not a benchmark.",
     f"a qualitative comparison on one public recording, made in the {EN_AUDIT}, is reported in the Annex and is not a benchmark.",
     "positioning: chronology"),
    # --- chapter III summary
    ("forced language identification is the clearest actionable win, and model size is the largest single accuracy lever at bounded computational cost.",
     "forced language identification is the clearest actionable win where the expected language is known and stable (it does not resolve language changes within a single intervention), and model size is the largest single accuracy lever at bounded computational cost.",
     "chapter III summary: forced-language nuance"),
    # --- conclusion
    ("Fourth, forcing the expected language repairs several wrong-script outputs, although direct LID accuracy was not logged in the CPU pilot.",
     f"Fourth, forcing the expected language repairs several wrong-script outputs, although direct LID accuracy was not logged in the CPU pilot; {EN_FORCE.lower()[0] + EN_FORCE[1:]}.",
     "conclusion: forced-language nuance"),
    ("A post-submission audit further showed that seven of the sixteen English and French reference transcripts of the published corpus are defective; the absolute WER levels reported above are therefore overestimates, the orderings survive a sensitivity revision, and the German references remain unverified (Annex).",
     f"A {EN_AUDIT} further showed that seven of the sixteen English and French reference transcripts differ after re-annotation (two only in audible hesitations, some passages remaining uncertain); the absolute WER levels reported above are therefore likely overestimates, the orderings survive a sensitivity revision, and the German references remain unverified (Annex).",
     "conclusion: chronology + references wording"),
])

patch("Memoire_LaTeX/validation_20260916.tex", [
    ("\\section*{Annex: Post-Submission Validation Audit (16 September 2026)}",
     "\\section*{Annex: Supplementary Audit Conducted on 16 September 2026}", "annex title"),
    ("\\addcontentsline{toc}{section}{Annex: Post-Submission Validation Audit (16 September 2026)}",
     "\\addcontentsline{toc}{section}{Annex: Supplementary Audit Conducted on 16 September 2026}", "annex toc"),
    ("This annex reports work carried out after the manuscript above was frozen.",
     "This annex reports a supplementary audit conducted on 16~September~2026, while the manuscript above was being prepared for review.",
     "annex intro: chronology"),
    ("The author then\nre-transcribed the 16 English and French clips by listening. \\textbf{Seven} differ from the published reference:\n\\texttt{en\\_01}, \\texttt{en\\_03} and \\texttt{fr\\_03} are truncated, \\texttt{en\\_02} and \\texttt{en\\_07} are\nmis-transcribed, and \\texttt{en\\_08} and \\texttt{fr\\_07} omit hesitations that are audible.",
     "The author then\nre-transcribed the 16 English and French clips by listening. \\textbf{Seven} differ from the published reference after\nre-annotation: \\texttt{en\\_01}, \\texttt{en\\_03} and \\texttt{fr\\_03} end earlier than the audio, \\texttt{en\\_02} and\n\\texttt{en\\_07} differ in wording, and \\texttt{en\\_08} and \\texttt{fr\\_07} differ only in audible hesitations. These are\ndifferences between one annotator's hearing and the published text, not all established errors of the corpus, and some\npassages remain uncertain (below).",
     "annex A.2: references wording"),
    ("The forced-language effect is\ntherefore supported at the script level (Chapter~III) but not as an aggregate WER gain.",
     f"The forced-language effect is\ntherefore supported at the script level (Chapter~III) but not as an aggregate WER gain. {EN_FORCE} (A.5).",
     "annex A.3: forced-language nuance"),
    ("Forcing French translated the\n  German and English into French. The failure is therefore a property of the single language decision, not of\n  model size, and it produces silent omission or silent translation, never an error.",
     f"Forcing French translated the\n  German and English into French. The failure is therefore a property of the single language decision, not of\n  model size, and it produces silent omission or silent translation, never an error. {EN_FORCE}.",
     "annex A.5: forced-language nuance"),
])
print("\n".join("  - " + l for l in log))
