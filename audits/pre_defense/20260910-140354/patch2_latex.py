"""Round-2 fixes, each targeting a warning confirmed in the TeXPage log.
Scientific content untouched. LF line endings preserved (binary write)."""
import pathlib, shutil, sys

BS = chr(92)
d = pathlib.Path("Memoire_LaTeX")
bak = pathlib.Path(sys.argv[1])
bak.mkdir(parents=True, exist_ok=True)

main = d / "main_revised.tex"
for p in (main,):
    tag = bak / (p.name + ".r2orig")
    if not tag.exists():
        shutil.copy2(p, tag)

txt = main.read_bytes().decode("utf-8")
applied = []


def sub(old, new, label, count=1):
    global txt
    n = txt.count(old)
    if n != count:
        raise SystemExit("ABORT [%s]: attendu %d, trouve %d\n  %r"
                         % (label, count, n, old[:100]))
    txt = txt.replace(old, new)
    applied.append(label)


# --- 1. Table III.7: 24.8 pt overfull. Column padding 6pt -> 3.5pt on 7
#        columns frees 7*2*2.5 = 35 pt. Font size untouched (\small kept).
sub(BS + "begin{tabular}{|l|c|c|c|c|c|c|}",
    BS + "setlength{" + BS + "tabcolsep}{3.5pt}%\n" + BS + "begin{tabular}{|l|c|c|c|c|c|c|}",
    "Table III.7: tabcolsep 6pt -> 3.5pt (libere 35 pt)")

# --- 2. Cover: p{} columns are justified, which stretches the supervisor
#        name across the cell. Ragged-right on the two text columns.
sub("{@{}p{0.20" + BS + "textwidth}p{0.33" + BS + "textwidth}p{0.41" + BS + "textwidth}@{}}",
    "{@{}p{0.20" + BS + "textwidth}"
    + ">{" + BS + "raggedright" + BS + "arraybackslash}p{0.33" + BS + "textwidth}"
    + ">{" + BS + "raggedright" + BS + "arraybackslash}p{0.41" + BS + "textwidth}@{}}",
    "Couverture: raggedright sur les colonnes 2 et 3")

# --- 3. Duplicate page.1: the cover is arabic page 1 and the body restarts
#        at arabic 1, so \thepage is "1" twice and plainpages=false cannot
#        separate them. Numbering the cover Roman (I) makes the two anchors
#        distinct. titlepage uses \thispagestyle{empty}: nothing becomes visible.
sub("%=========================== [Title page] =======================\n"
    + BS + "begin{titlepage}",
    "%=========================== [Title page] =======================\n"
    + "% Cover numbered Roman so its hyperref anchor is page.I, not a second page.1.\n"
    + BS + "pagenumbering{Roman}\n"
    + BS + "begin{titlepage}",
    "Couverture numerotee Roman (anchor page.I)")

# --- 4. Font shapes that do not exist in Latin Modern.
#        T1/lmss/m/sc, T1/lmss/bx/sc and T1/lmr/bx/sc are all undefined;
#        LaTeX was already substituting the non-small-caps shape, so dropping
#        the small-caps request changes nothing on the page.
sub(BS + "large{" + BS + "textsc{" + BS + "textbf{Master of Science Program in Artificial Intelligence}}}",
    BS + "large{" + BS + "textbf{Master of Science Program in Artificial Intelligence}}",
    "Couverture l.129: textsc retire (T1/lmss/bx/sc inexistant)")

sub(BS + "large{" + BS + "textsc{" + BS + "textbf{Master's Thesis}}}",
    BS + "large{" + BS + "textbf{Master's Thesis}}",
    "Couverture l.135: textsc retire (T1/lmss/bx/sc inexistant)")

sub("title={" + BS + "textsc{Bibliography}}]",
    "title={Bibliography}]",
    "Bibliographie l.670: textsc retire (T1/lmss/m/sc inexistant)")

sub("{" + BS + "normalfont" + BS + "Large" + BS + "filcenter" + BS + "rmfamily " + BS + "bfseries " + BS + "scshape " + BS + "color{myColor}}",
    "{" + BS + "normalfont" + BS + "Large" + BS + "filcenter" + BS + "rmfamily " + BS + "bfseries " + BS + "color{myColor}}",
    "titleformat chapitre: scshape retire (T1/lmr/bx/sc inexistant)")

main.write_bytes(txt.encode("utf-8"))

print("Correctifs round 2 :")
for a in applied:
    print("  -", a)
b = main.read_bytes()
print("\nfins de ligne: CRLF=%d LF=%d" % (b.count(b"\r\n"), b.count(b"\n")))
