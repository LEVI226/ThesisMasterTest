"""Apply the log-confirmed layout/navigation fixes. Content is not touched.
Every replacement asserts its target exists; nothing is silently skipped."""
import pathlib, shutil, sys

BS = chr(92)
d = pathlib.Path("Memoire_LaTeX")
bak = pathlib.Path(sys.argv[1])           # audit dir for pristine copies
bak.mkdir(parents=True, exist_ok=True)

applied = []


def edit(path, old, new, label, count=1):
    txt = path.read_text(encoding="utf-8")
    n = txt.count(old)
    if n != count:
        raise SystemExit("ABORT [%s]: attendu %d occurrence(s), trouve %d\n  %r"
                         % (label, count, n, old[:90]))
    path.write_text(txt.replace(old, new), encoding="utf-8")
    applied.append("%-28s %s (x%d)" % (path.name, label, n))


main = d / "main_revised.tex"
comp = d / "topic2_completion.tex"
for p in (main, comp):
    if not (bak / (p.name + ".orig")).exists():
        shutil.copy2(p, bak / (p.name + ".orig"))

# --- 1. geometry: drop the overridden declaration, keep the canevas value ---
edit(main,
     BS + "usepackage[margin=1in]{geometry}\n",
     "",
     "geometry: supprime margin=1in (ecrase par le canevas)")

# --- 2. hyperref: distinct page anchors (fixes duplicate page.1) ---
edit(main,
     "urlcolor=myColor]{hyperref}",
     "urlcolor=myColor,plainpages=false,pdfpagelabels]{hyperref}",
     "hyperref: plainpages=false,pdfpagelabels")

# --- 3. lmodern: supplies T1 bold small caps (missing in default CM) ---
edit(main,
     BS + "usepackage[T1]{fontenc}",
     BS + "usepackage{lmodern}\n" + BS + "usepackage[T1]{fontenc}",
     "lmodern: fournit T1 bx/sc")

# --- 4. jury tabular: 1.10 -> 0.94 textwidth, outer padding removed ---
edit(main,
     "{p{0.20" + BS + "textwidth} p{0.28" + BS + "textwidth} p{0.62" + BS + "textwidth}}",
     "{@{}p{0.20" + BS + "textwidth}p{0.33" + BS + "textwidth}p{0.41" + BS + "textwidth}@{}}",
     "tableau jury: largeurs 1.10 -> 0.94")

# --- 5. Conformer identifier: breakpoints, printed text unchanged ---
edit(main,
     BS + "texttt{stt" + BS + "_" + BS + "{en,fr,de" + BS + "}" + BS + "_conformer" + BS + "_ctc" + BS + "_large}",
     BS + "texttt{stt" + BS + "_" + BS + "allowbreak " + BS + "{en,fr,de" + BS + "}" + BS + "_"
     + BS + "allowbreak conformer" + BS + "_" + BS + "allowbreak ctc" + BS + "_" + BS + "allowbreak large}",
     "identifiant Conformer: points de coupure")

# --- 6. phantomsection before every \addcontentsline (TOC anchors) ---
for path, n in ((main, 10), (comp, 1)):
    txt = path.read_text(encoding="utf-8")
    assert BS + "phantomsection" not in txt, "phantomsection deja present"
    c = txt.count(BS + "addcontentsline")
    if c != n:
        raise SystemExit("ABORT phantomsection %s: attendu %d, trouve %d" % (path.name, n, c))
    path.write_text(txt.replace(BS + "addcontentsline",
                                BS + "phantomsection\n" + BS + "addcontentsline"),
                    encoding="utf-8")
    applied.append("%-28s phantomsection avant addcontentsline (x%d)" % (path.name, c))

# --- 7. long texttt tokens in the supplement ---
edit(comp,
     BS + "texttt{results/live" + BS + "_latency.csv}",
     BS + "texttt{results/" + BS + "allowbreak live" + BS + "_" + BS + "allowbreak latency.csv}",
     "texttt live_latency.csv: coupure")

edit(comp,
     BS + "texttt{python -m backend.evaluation.topic2" + BS + "_readiness}",
     BS + "texttt{python -m backend." + BS + "allowbreak evaluation." + BS + "allowbreak topic2"
     + BS + "_" + BS + "allowbreak readiness}",
     "texttt topic2_readiness: coupure")

print("Correctifs appliques :")
for a in applied:
    print("  -", a)
