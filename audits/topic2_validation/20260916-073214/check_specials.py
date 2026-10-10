import re, pathlib
BS = chr(92)
t = pathlib.Path("Memoire_LaTeX/validation_20260916.tex").read_text(encoding="utf-8")
body = "\n".join(l for l in t.split("\n") if not l.lstrip().startswith("%"))
issues = []
for ch, label in (("_", "_ non echappe"), ("%", "% non echappe"), ("#", "# non echappe")):
    for m in re.finditer("(?<!" + BS + BS + ")" + re.escape(ch), body):
        issues.append((label, body[max(0, m.start() - 30):m.start() + 15].replace("\n", " ")))
for m in re.finditer("(?<!" + BS + BS + ")&", body):
    line = body[body.rfind("\n", 0, m.start()) + 1:body.find("\n", m.start())]
    if BS + BS not in line and "hline" not in line:
        issues.append(("& hors tableau", line[:80]))
print("problemes:", len(issues))
for k, s in issues[:12]:
    print("  ", k, "->", repr(s))
