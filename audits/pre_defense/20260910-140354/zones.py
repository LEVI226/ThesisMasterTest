import re, pathlib

BS = chr(92)
d = pathlib.Path("Memoire_LaTeX")
txt = (d / "main_revised.tex").read_text(encoding="utf-8")
lines = txt.splitlines()

# geometry scope boundaries
bounds = []
for i, l in enumerate(lines, 1):
    if re.search(BS + BS + r"geometry\{", l) and "newgeometry" not in l:
        bounds.append((i, "preambule \\geometry{total=170mm,left=20mm,top=20mm}"))
    if BS + "newgeometry" in l:
        bounds.append((i, "\\newgeometry{left=2.25cm,top=2.2cm,bottom=2.2cm}"))
    if BS + "restoregeometry" in l:
        bounds.append((i, "\\restoregeometry"))

print("Frontieres de geometrie :")
for ln, what in bounds:
    print("  l.%-5d %s" % (ln, what))
print("  -> AUCUN \\restoregeometry : la derniere \\newgeometry court jusqu'a \\end{document}")
print()


def zone(ln):
    z = "preambule (170mm)"
    for b, what in bounds:
        if b <= ln and "newgeometry" in what:
            z = "newgeometry (largeur NON specifiee)"
        elif b <= ln and "restore" in what:
            z = "preambule (170mm)"
    return z


print("Tableaux et leur zone :")
for m in re.finditer(BS + BS + r"begin\{(tabular|longtable)\}", txt):
    ln = txt.count("\n", 0, m.start()) + 1
    seg = txt[m.end():m.end() + 120].split("\n")[0]
    fixed = "textwidth" in seg
    print("  l.%-5d %-12s %-36s %s" % (ln, m.group(1),
          zone(ln), "largeurs \\textwidth" if fixed else "dimensionne par le contenu"))

print()
print("topic2_completion.tex est \\input a la l.%d -> zone : %s" %
      (txt.count("\n", 0, txt.index(BS + "input{topic2_completion}")) + 1,
       zone(txt.count("\n", 0, txt.index(BS + "input{topic2_completion}")) + 1)))
