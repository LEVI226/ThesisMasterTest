"""Round 3: the last font notice. Selects an actually available shape for the
URL/DOI labels biblatex sets in small caps."""
import pathlib, shutil, sys

BS = chr(92)
d = pathlib.Path("Memoire_LaTeX")
bak = pathlib.Path(sys.argv[1])
bak.mkdir(parents=True, exist_ok=True)
main = d / "main_revised.tex"
tag = bak / (main.name + ".r3orig")
if not tag.exists():
    shutil.copy2(main, tag)

txt = main.read_bytes().decode("utf-8")

old = "  maxbibnames=100]{biblatex}\n"
new = ("  maxbibnames=100]{biblatex}\n"
       "% The canevas sets \\familydefault to \\sfdefault (l. 90) and Latin Modern\n"
       "% Sans has no small caps, so biblatex's small-caps URL/DOI labels fell back\n"
       "% to T1/lmr/m/sc with a notice. Select that available shape explicitly:\n"
       "% same rendering, no substitution.\n"
       + BS + "renewrobustcmd*{" + BS + "mkbibacro}[1]{{" + BS + "rmfamily" + BS
       + "textsc{" + BS + "MakeLowercase{#1}}}}\n")

n = txt.count(old)
if n != 1:
    raise SystemExit("ABORT: ancre biblatex trouvee %d fois" % n)
txt = txt.replace(old, new)

main.write_bytes(txt.encode("utf-8"))
b = main.read_bytes()
print("mkbibacro: famille romaine explicite pour URL/DOI")
print("fins de ligne: CRLF=%d LF=%d" % (b.count(b"\r\n"), b.count(b"\n")))
