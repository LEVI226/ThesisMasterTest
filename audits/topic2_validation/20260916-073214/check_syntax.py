import re, pathlib
from collections import Counter

BS = chr(92)
d = pathlib.Path("Memoire_LaTeX")
for name in ["main_revised.tex", "topic2_completion.tex", "validation_20260916.tex"]:
    t = (d / name).read_text(encoding="utf-8")
    body = re.sub(r"(?<!" + BS + BS + r")%.*", "", t)          # strip comments (not \%)
    opens = body.count("{") - body.count(BS + "{")
    closes = body.count("}") - body.count(BS + "}")
    begins = re.findall(BS + BS + r"begin\{(\w+\*?)\}", body)
    ends = re.findall(BS + BS + r"end\{(\w+\*?)\}", body)
    cb, ce = Counter(begins), Counter(ends)
    bad = {k: (cb[k], ce[k]) for k in set(cb) | set(ce) if cb[k] != ce[k]}
    abs_paths = re.findall(r"[A-Za-z]:[/\\]|/Users/|/home/", body)
    print("%-26s braces %d/%d %s | envs %s | abs paths: %d" % (
        name, opens, closes, "OK" if opens == closes else "MISMATCH",
        "OK" if not bad else "MISMATCH " + str(bad), len(abs_paths)))
main = (d / "main_revised.tex").read_text(encoding="utf-8")
print("inputs:", re.findall(BS + BS + r"input\{([^}]*)\}", main))
print("bib   :", re.findall(BS + BS + r"bibliography\{([^}]*)\}", main))
print("images:", re.findall(BS + BS + r"includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", main))
