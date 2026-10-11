"""Targeted fixes for the three reproduced contract defects, plus a configurable
live-latency CSV path so validation runs never append to the historical file.
Every replacement asserts a single match; originals are copied to pristine/."""
import pathlib, shutil

BS = chr(92)
ROOT = pathlib.Path(__file__).resolve().parents[3]
PRISTINE = pathlib.Path(__file__).parent / "pristine"
PRISTINE.mkdir(exist_ok=True)
applied = []


def patch(rel, pairs):
    p = ROOT / rel
    bak = PRISTINE / (p.name + ".orig")
    if not bak.exists():
        shutil.copy2(p, bak)
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    txt = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new, label in pairs:
        n = txt.count(old)
        if n != 1:
            raise SystemExit("ABORT %s [%s]: %d match(es)" % (rel, label, n))
        txt = txt.replace(old, new)
        applied.append("%-32s %s" % (rel, label))
    if crlf:
        txt = txt.replace("\n", "\r\n")
    p.write_bytes(txt.encode("utf-8"))


# ============================================================ backend/main.py
patch("backend/main.py", [
    # --- imports: Form + Query
    ("from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect",
     "from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException, WebSocket, WebSocketDisconnect",
     "import Form, Query"),

    # --- defect 1: accept language from multipart form (frontend) or query string
    ("    file: UploadFile = File(..., description=\"Audio or video file (mp3, mp4, wav, m4a\u2026)\"),\n"
     "    language: str | None = None,\n",
     "    file: UploadFile = File(..., description=\"Audio or video file (mp3, mp4, wav, m4a\u2026)\"),\n"
     "    language: str | None = Form(None, description=\"Force language (fr/en/de) as a form field\"),\n"
     "    language_query: str | None = Query(None, alias=\"language\", include_in_schema=False),\n",
     "defect 1: language via Form or Query"),

    ("            lambda: transcribe_file(str(save_path), forced_language=language),",
     "            lambda: transcribe_file(str(save_path), forced_language=(language or language_query)),",
     "defect 1: forward whichever was given"),

    # --- live latency CSV configurable (never append validation runs to history)
    ("    LATENCY_CSV = Path(\"results/live_latency.csv\")\n",
     "    # Historical file by default; validation runs override with LIVE_LATENCY_CSV.\n"
     "    LATENCY_CSV = Path(os.environ.get(\"LIVE_LATENCY_CSV\", \"results/live_latency.csv\"))\n"
     "    END_SIGNAL = \"__end__\"   # text frame the client sends to flush the last utterance\n",
     "latency CSV path from env"),

    # --- defect 2: receive() so text end-signal is visible; flush on end/disconnect
    ("                # 1. Accept raw 16kHz mono PCM (binary)\n"
     "                try:\n"
     "                    chunk = await self.websocket.receive_bytes()\n"
     "                except WebSocketDisconnect:\n"
     "                    break\n"
     "                except Exception as e:\n"
     "                    logger.error(f\"WS receive error: {e}\")\n"
     "                    break\n"
     "\n"
     "                if not chunk:\n"
     "                    continue\n",
     "                # 1. Accept raw 16kHz mono PCM (binary) or the text end-signal\n"
     "                try:\n"
     "                    msg = await self.websocket.receive()\n"
     "                except WebSocketDisconnect:\n"
     "                    break\n"
     "                except Exception as e:\n"
     "                    logger.error(f\"WS receive error: {e}\")\n"
     "                    break\n"
     "\n"
     "                if msg.get(\"type\") == \"websocket.disconnect\":\n"
     "                    break\n"
     "                if msg.get(\"text\") is not None:\n"
     "                    if msg[\"text\"].strip() == self.END_SIGNAL:\n"
     "                        await self._flush_pending(_model, _diarization_pipeline, reason=\"end_signal\")\n"
     "                        try:\n"
     "                            await self.websocket.send_json({\"type\": \"flushed\"})\n"
     "                        except Exception:\n"
     "                            pass\n"
     "                    continue\n"
     "                chunk = msg.get(\"bytes\")\n"
     "                if not chunk:\n"
     "                    continue\n",
     "defect 2: receive() + end-signal handling"),

    ("        except Exception as e:\n"
     "            logger.error(f\"WebSocket loop error: {e}\")\n"
     "        finally:\n"
     "            logger.info(\"WebSocket STT client disconnected.\")\n",
     "        except Exception as e:\n"
     "            logger.error(f\"WebSocket loop error: {e}\")\n"
     "        finally:\n"
     "            # Best effort: transcribe whatever was still buffered when the client\n"
     "            # left. Delivery may fail (socket gone) but the text is still logged.\n"
     "            await self._flush_pending(_model, _diarization_pipeline, reason=\"disconnect\")\n"
     "            logger.info(\"WebSocket STT client disconnected.\")\n"
     "\n"
     "    async def _flush_pending(self, model, diarizer, reason: str):\n"
     "        \"\"\"Transcribe the pending buffer without waiting for a silence window.\"\"\"\n"
     "        if not self.audio_buffer:\n"
     "            return\n"
     "        logger.info(\"Flushing pending audio (%d bytes, reason=%s)\", len(self.audio_buffer), reason)\n"
     "        self.is_speaking = False\n"
     "        self._t_silence_end = time.monotonic()\n"
     "        try:\n"
     "            _vad_model = __import__(\"backend.stt.engine\", fromlist=[\"_vad_model\"])._vad_model\n"
     "            if _vad_model is not None:\n"
     "                _vad_model.reset_states()\n"
     "        except Exception:\n"
     "            pass\n"
     "        await self._transcribe_and_diarize(model, diarizer)\n"
     "        self.audio_buffer = bytearray()\n"
     "        self.silence_frames = 0\n",
     "defect 2: flush on disconnect + _flush_pending"),
])

# ===================================================== backend/evaluation/runner.py
patch("backend/evaluation/runner.py", [
    ("TRANSCRIPT_DIR = Path(\"results/transcripts\")\n",
     "# Historical location by default; new campaigns should set TRANSCRIPT_DIR so\n"
     "# their side files never overwrite the canonical ones.\n"
     "TRANSCRIPT_DIR = Path(os.environ.get(\"TRANSCRIPT_DIR\", \"results/transcripts\"))\n",
     "transcript dir from env"),

    # --- defect 3: name includes model and VAD; computed after the model is known
    ("    condition_tag = (\n"
     "        f\"prep{int(preprocessing)}_prompt{int(domain_prompt)}\"\n"
     "        f\"_lang{forced_language or 'auto'}\"\n"
     "    )\n",
     "",
     "defect 3: drop early tag without model/vad"),

    ("        transcript_path = _save_transcript(sample.audio_filename, condition_tag, hypothesis)\n",
     "        # Model actually used + VAD are part of the name so runs never collide.\n"
     "        condition_tag = (\n"
     "            f\"{model_used}_prep{int(preprocessing)}_prompt{int(domain_prompt)}\"\n"
     "            f\"_lang{forced_language or 'auto'}_vad{int(vad)}\"\n"
     "        )\n"
     "        transcript_path = _save_transcript(sample.audio_filename, condition_tag, hypothesis)\n",
     "defect 3: tag = model + prep + prompt + lang + vad"),
])

# ============================================================ frontend/index.html
patch("frontend/index.html", [
    ("    function liveStopRecord() {\n"
     "      liveRecording = false;\n",
     "    function liveStopRecord() {\n"
     "      liveRecording = false;\n"
     "      // Ask the server to transcribe whatever is still buffered (last sentence).\n"
     "      if (liveWs && liveWs.readyState === WebSocket.OPEN) { try { liveWs.send('__end__'); } catch {} }\n",
     "defect 2: send __end__ on stop"),

    ("    function liveDisconnect() {\n"
     "      liveStopRecord();\n"
     "      if (liveWs) { liveWs.close(); liveWs = null; }\n"
     "    }\n",
     "    function liveDisconnect() {\n"
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
     "defect 2: wait for flushed ack before close"),
])

# runner.py needs os
p = ROOT / "backend/evaluation/runner.py"
t = p.read_text(encoding="utf-8")
if "\nimport os\n" not in t and not t.startswith("import os\n"):
    t = t.replace("import time\n", "import os\nimport time\n", 1)
    p.write_text(t, encoding="utf-8")
    applied.append("%-32s %s" % ("backend/evaluation/runner.py", "import os"))

print("Correctifs appliques :")
for a in applied:
    print("  -", a)
