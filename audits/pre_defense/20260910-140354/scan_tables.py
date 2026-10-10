import re, pathlib

BS = chr(92)
d = pathlib.Path("Memoire_LaTeX")
TW = 482.6  # 170mm text width in pt


def balanced(s, start):
    """Return the {...} group starting at s[start] == '{', brace-matched."""
    assert s[start] == "{"
    depth, i = 0, start
    while i < len(s):
        if s[i] == "{" and (i == 0 or s[i - 1] != BS):
            depth += 1
        elif s[i] == "}" and s[i - 1] != BS:
            depth -= 1
            if depth == 0:
                return s[start + 1:i], i
        i += 1
    return None, start


for name in ["main_revised.tex", "topic2_completion.tex", "validation_20260916.tex"]:
    txt = (d / name).read_text(encoding="utf-8", errors="replace")
    print("=" * 72)
    print(name)
    print("=" * 72)

    for env in ("tabular", "longtable", "tabularx"):
        for m in re.finditer(BS + BS + r"begin\{" + env + r"\}", txt):
            j = m.end()
            while j < len(txt) and txt[j] in " \t":
                j += 1
            if j < len(txt) and txt[j] == "[":       # optional [t]/[b]
                j = txt.index("]", j) + 1
                while j < len(txt) and txt[j] in " \t":
                    j += 1
            if env == "tabularx":                     # skip width arg
                _, e = balanced(txt, j)
                j = e + 1
                while j < len(txt) and txt[j] in " \t":
                    j += 1
            if j >= len(txt) or txt[j] != "{":
                continue
            spec, _ = balanced(txt, j)
            line = txt.count("\n", 0, m.start()) + 1
            widths = [float(w) for w in
                      re.findall(r"([0-9.]+)" + BS + BS + r"textwidth", spec)]
            if not widths:
                continue
            n = len(widths)
            pad = (2 * n * 6.0) / TW
            if "@{}" in spec:
                pad -= (2 * 6.0) / TW
            total = sum(widths) + pad
            over = (total - 1.0) * TW
            flag = "OVERFULL +%.0f pt" % over if over > 0.5 else "ok"
            print("l.%-5d %-9s cols=%d somme=%.3f (+pad %.3f) = %.3f  %s"
                  % (line, env, n, sum(widths), pad, total, flag))
            if over > 0.5:
                print("         spec: %s" % spec)

    print("\n-- tokens \\texttt{} longs et insecables --")
    for m in re.finditer(BS + BS + r"texttt\{", txt):
        body, _ = balanced(txt, m.end() - 1)
        if body is None:
            continue
        line = txt.count("\n", 0, m.start()) + 1
        vis = body.replace(BS + "_", "_").replace(BS + "{", "{").replace(BS + "}", "}")
        toks = vis.split()
        if not toks:
            continue
        longest = max(toks, key=len)
        if len(longest) >= 20:
            print("l.%-5d len=%-3d  %s" % (line, len(longest), vis[:95]))
    print()
