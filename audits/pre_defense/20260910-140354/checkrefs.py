import re, pathlib, collections

BS = chr(92)
d = pathlib.Path("Memoire_LaTeX")
txt = "".join((d / f).read_text(encoding="utf-8", errors="replace")
              for f in ["main_revised.tex", "topic2_completion.tex", "validation_20260916.tex"])

labels = [m.group(1) for m in re.finditer(BS + BS + r"label\{([^}]*)\}", txt)]
refs = set()
for cmd in ("ref", "pageref", "autoref", "nameref", "eqref"):
    for m in re.finditer(BS + BS + cmd + r"\{([^}]*)\}", txt):
        refs |= {r.strip() for r in m.group(1).split(",") if r.strip()}

L = set(labels)
dup = [k for k, v in collections.Counter(labels).items() if v > 1]

print("labels definis :", len(labels), "| uniques:", len(L))
print("labels DUPLIQUES:", dup or "aucun")
print("cles \\ref utilisees :", len(refs))
print()
missing = sorted(refs - L)
print("REFERENCEES SANS \\label  ->", len(missing))
for k in missing:
    print("   !!", k)
unused = sorted(L - refs)
print("\nlabels jamais references (sans effet sur le rendu) ->", len(unused))
for k in unused:
    print("   -", k)
