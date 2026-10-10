"""Re-apply each original line's own ending on untouched lines; new or changed
lines take the file's dominant ending. Keeps the diff limited to real edits."""
import difflib, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[3]
P = pathlib.Path(__file__).parent / "pristine"

for rel in ["backend/main.py", "backend/evaluation/runner.py"]:
    f = ROOT / rel
    orig = (P / (f.name + ".orig")).read_bytes()
    new = f.read_bytes()
    o_lines = orig.split(b"\n")
    o_text = [l.rstrip(b"\r") for l in o_lines]
    o_end = [b"\r\n" if l.endswith(b"\r") else b"\n" for l in o_lines]
    n_text = [l.rstrip(b"\r") for l in new.split(b"\n")]
    dominant = b"\r\n" if orig.count(b"\r\n") * 2 > orig.count(b"\n") else b"\n"
    out = []
    sm = difflib.SequenceMatcher(a=o_text, b=n_text, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                out.append(n_text[j1 + k] + o_end[i1 + k])
        else:
            for k in range(j1, j2):
                out.append(n_text[k] + dominant)
    # the last split element is the text after the final newline (usually empty)
    data = b"".join(out)
    if data.endswith(dominant) and not new.endswith(b"\n"):
        data = data[: -len(dominant)]
    f.write_bytes(data)
    b = f.read_bytes()
    print("%-32s CRLF=%d LF-seuls=%d (orig CRLF=%d LF-seuls=%d)" % (
        rel, b.count(b"\r\n"), b.count(b"\n") - b.count(b"\r\n"),
        orig.count(b"\r\n"), orig.count(b"\n") - orig.count(b"\r\n")))
