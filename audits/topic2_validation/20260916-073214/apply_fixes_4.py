"""Round 4 — browser side of the end-of-speech fix, on BOTH live interfaces.

1. Send the residual PCM (< 1 packet) before `__end__`, so the last word that
   never reached a full 1 s packet is not thrown away.
2. Disconnect waits for the server's `flushed` ack (sent only after the flush
   transcription completed) instead of a fixed 2 s; a long fallback guards
   against a dead server; the status shows "Finishing…".
3. Same protocol in frontend/live_transcribe.html (route /live), which had none.
"""
import pathlib, shutil

ROOT = pathlib.Path(__file__).resolve().parents[3]
PRISTINE = pathlib.Path(__file__).parent / "pristine"
applied = []


def patch(rel, pairs, backup_name=None):
    p = ROOT / rel
    bak = PRISTINE / (backup_name or (p.name + ".r4orig"))
    if not bak.exists():
        shutil.copy2(p, bak)
    raw = p.read_bytes(); crlf = b"\r\n" in raw
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new, label in pairs:
        n = t.count(old)
        if n != 1:
            raise SystemExit("ABORT %s [%s]: %d" % (rel, label, n))
        t = t.replace(old, new); applied.append("%-30s %s" % (rel, label))
    if crlf:
        t = t.replace("\n", "\r\n")
    p.write_bytes(t.encode("utf-8"))


# ------------------------------------------------------------ index.html
patch("frontend/index.html", [
    ("    function liveStopRecord() {\n"
     "      liveRecording = false;\n"
     "      // Ask the server to transcribe whatever is still buffered (last sentence).\n"
     "      if (liveWs && liveWs.readyState === WebSocket.OPEN) { try { liveWs.send('__end__'); } catch {} }\n",
     "    function liveStopRecord() {\n"
     "      liveRecording = false;\n"
     "      if (liveWs && liveWs.readyState === WebSocket.OPEN) {\n"
     "        // 1) push the residual samples that never filled a 1 s packet (last word),\n"
     "        // 2) ask the server to transcribe whatever it now holds.\n"
     "        try {\n"
     "          if (livePcmBuf.length > 0) { liveWs.send(liveF32toI16(livePcmBuf).buffer); livePcmBuf = new Float32Array(0); }\n"
     "          liveWs.send('__end__');\n"
     "          liveSetStatus('connecting', 'Finishing…');\n"
     "        } catch {}\n"
     "      }\n",
     "residual PCM sent before __end__"),

    ("    function liveDisconnect() {\n"
     "      liveStopRecord();\n"
     "      // Give the server up to 2 s to deliver the flushed last utterance before closing.\n"
     "      const ws = liveWs; liveWs = null;\n"
     "      if (!ws) return;\n"
     "      let closed = false;\n"
     "      const done = () => { if (!closed) { closed = true; try { ws.close(); } catch {} } };\n"
     "      const prev = ws.onmessage;\n"
     "      ws.onmessage = (e) => { if (prev) prev(e); try { if (JSON.parse(e.data).type === 'flushed') done(); } catch {} };\n"
     "      setTimeout(done, 2000);\n"
     "    }\n",
     "    function liveDisconnect() {\n"
     "      liveStopRecord();\n"
     "      // Close only once the server acknowledges the flush ({type:'flushed'} is sent after\n"
     "      // the final transcription completed, however long it took). The long timeout only\n"
     "      // guards against a server that never answers.\n"
     "      const ws = liveWs; liveWs = null;\n"
     "      if (!ws) return;\n"
     "      let closed = false;\n"
     "      const done = () => { if (!closed) { closed = true; try { ws.close(); } catch {} } };\n"
     "      const prev = ws.onmessage;\n"
     "      ws.onmessage = (e) => { if (prev) prev(e); try { if (JSON.parse(e.data).type === 'flushed') done(); } catch {} };\n"
     "      setTimeout(done, 30000);\n"
     "    }\n",
     "disconnect waits for flushed ack (30 s guard)"),

    # a flushed ack while still connected (Stop Recording only) restores the status
    ("      liveWs.onmessage = (e) => {\n"
     "        if (typeof e.data === 'string') {\n"
     "          try { liveAppendSegment(JSON.parse(e.data)); } catch {}\n"
     "        }\n"
     "      };\n",
     "      liveWs.onmessage = (e) => {\n"
     "        if (typeof e.data === 'string') {\n"
     "          try {\n"
     "            const m = JSON.parse(e.data);\n"
     "            if (m.type === 'flushed') { liveSetStatus('connected', 'Connected'); return; }\n"
     "            liveAppendSegment(m);\n"
     "          } catch {}\n"
     "        }\n"
     "      };\n",
     "flushed ack restores status; not appended as a segment"),
])

# ------------------------------------------------------ live_transcribe.html
patch("frontend/live_transcribe.html", [
    ("function stopRecording() {\n"
     "  if (processorNode) {\n",
     "function stopRecording() {\n"
     "  // Send the residual samples (< 1 packet) and ask the server to flush what it holds.\n"
     "  if (ws && ws.readyState === WebSocket.OPEN) {\n"
     "    try {\n"
     "      if (pcmBuffer.length > 0) { ws.send(float32ToInt16(pcmBuffer).buffer); pcmBuffer = new Float32Array(0); }\n"
     "      ws.send('__end__');\n"
     "    } catch {}\n"
     "  }\n"
     "  if (processorNode) {\n",
     "/live: residual PCM + __end__ on stop"),

    ("function disconnect() {\n"
     "  stopRecording();\n"
     "  if (ws) { ws.close(); ws = null; }\n"
     "  setState(STATE.IDLE);\n"
     "}\n",
     "function disconnect() {\n"
     "  stopRecording();\n"
     "  // Close after the server acknowledges the flush; 30 s guard for a dead server.\n"
     "  const sock = ws; ws = null;\n"
     "  setState(STATE.IDLE);\n"
     "  if (!sock) return;\n"
     "  let closed = false;\n"
     "  const done = () => { if (!closed) { closed = true; try { sock.close(); } catch {} } };\n"
     "  const prev = sock.onmessage;\n"
     "  sock.onmessage = (evt) => { if (prev) prev(evt); try { if (JSON.parse(evt.data).type === 'flushed') done(); } catch {} };\n"
     "  setTimeout(done, 30000);\n"
     "}\n",
     "/live: disconnect waits for flushed ack"),
])

# /live onmessage must ignore the ack rather than render it as a segment
p = ROOT / "frontend/live_transcribe.html"
t = p.read_bytes().decode("utf-8")
i = t.index("  ws.onmessage = (evt) => {")
j = t.index("\n", i) + 1
line2 = t[j:t.index("\n", j) + 1]
if "flushed" not in t[i:i + 400]:
    t = t[:j] + "    try { if (JSON.parse(evt.data).type === 'flushed') return; } catch {}\n" + t[j:]
    p.write_bytes(t.encode("utf-8")); applied.append("%-30s %s" % ("frontend/live_transcribe.html", "/live: ignore flushed ack in onmessage"))

print("Round 4 applied:")
for a in applied:
    print("  -", a)
