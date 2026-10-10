import re, pathlib, collections

d = pathlib.Path("Memoire_LaTeX")
tex = "".join((d / f).read_text(encoding="utf-8", errors="replace")
              for f in ["main_revised.tex", "topic2_completion.tex", "validation_20260916.tex"])

BS = chr(92)
pat = re.compile(BS + BS + r"(?:cite|parencite|textcite|autocite|citep|citet)" +
                 r"\*?(?:\[[^\]]*\])*\{([^}]*)\}")
keys = set()
for m in pat.finditer(tex):
    keys |= {k.strip() for k in m.group(1).split(",") if k.strip()}

bib = (d / "bibitem_revised.bib").read_text(encoding="utf-8", errors="replace")
entries = [m.group(1).strip() for m in re.finditer(r"^@\w+\{([^,]+),", bib, re.M)]
ents = set(entries)
dup = [k for k, v in collections.Counter(entries).items() if v > 1]

print("cles citees    :", len(keys))
print("entrees bib    :", len(entries), "| uniques:", len(ents))
print("cles dupliquees:", dup or "aucune")

missing = sorted(keys - ents)
unused = sorted(ents - keys)
print("\nCITEES MAIS ABSENTES DU .bib  ->", len(missing))
for k in missing:
    print("   !!", k)
print("\nDANS LE .bib MAIS JAMAIS CITEES ->", len(unused))
for k in unused:
    print("   -", k)

na = [(i, l.strip()[:90]) for i, l in enumerate(bib.splitlines(), 1)
      if any(ord(c) > 127 for c in l)]
print("\nLignes .bib avec du non-ASCII (risque avec backend=bibtex) ->", len(na))
for i, l in na[:20]:
    print("   l.%d: %s" % (i, l))
