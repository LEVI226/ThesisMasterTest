import re, pathlib

BS = chr(92)
B = pathlib.Path("Memoire_LaTeX/texpage_bundle")
texs = sorted(B.glob("*.tex"))
blob = "".join(t.read_text(encoding="utf-8", errors="replace") for t in texs)

def find(cmd):
    return [m.group(1) for m in
            re.finditer(BS + BS + cmd + r"(?:\[[^\]]*\])?\{([^}]*)\}", blob)]

ok, bad = [], []

for tgt in find("includegraphics"):
    p = B / tgt
    hit = p if p.exists() else next(
        (q for q in (B / (tgt + e) for e in (".png", ".jpg", ".jpeg", ".pdf", ".eps"))
         if q.exists()), None)
    (ok if hit else bad).append(("includegraphics", tgt, hit.name if hit else "INTROUVABLE"))

for tgt in find("input") + find("include"):
    p = B / tgt
    hit = p if p.exists() else (B / (tgt + ".tex") if (B / (tgt + ".tex")).exists() else None)
    (ok if hit else bad).append(("input", tgt, hit.name if hit else "INTROUVABLE"))

for tgt in find("bibliography") + find("addbibresource"):
    for t in tgt.split(","):
        t = t.strip()
        p = B / t
        hit = p if p.exists() else (B / (t + ".bib") if (B / (t + ".bib")).exists() else None)
        (ok if hit else bad).append(("bibliography", t, hit.name if hit else "INTROUVABLE"))

print("Fichiers du dossier :")
for f in sorted(B.rglob("*")):
    if f.is_file():
        print("   ", f.relative_to(B).as_posix(), "(%d o)" % f.stat().st_size)

print("\nReferences resolues :")
for kind, tgt, hit in ok:
    print("   OK   %-16s %-28s -> %s" % (kind, tgt, hit))
print("\nReferences NON resolues :", len(bad))
for kind, tgt, hit in bad:
    print("   !!   %-16s %-28s -> %s" % (kind, tgt, hit))

pkgs = sorted(set(sum((m.group(1).split(",") for m in
              re.finditer(BS + BS + r"usepackage(?:\[[^\]]*\])?\{([^}]*)\}", blob)), [])))
print("\nPaquets requis (%d) :" % len(pkgs))
print("   " + ", ".join(p.strip() for p in pkgs))

opts = re.search(BS + BS + r"documentclass(\[[^\]]*\])?\{(\w+)\}", blob)
print("\nClasse :", opts.group(2), opts.group(1) or "")
print("Fichier principal : main_revised.tex" if (B / "main_revised.tex").exists() else "?")
