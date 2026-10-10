import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[3]
p = ROOT / "backend/main.py"
t = p.read_text(encoding="utf-8")
n = 0


def sub(old, new):
    global t, n
    assert t.count(old) == 1, old[:80]
    t = t.replace(old, new); n += 1


sub("                        await self._flush_pending(_model, _diarization_pipeline, reason=\"end_signal\")\n",
    "                        await self._flush_pending(_model, _diarization_pipeline, _vad_model, reason=\"end_signal\")\n")
sub("            await self._flush_pending(_model, _diarization_pipeline, reason=\"disconnect\")\n",
    "            await self._flush_pending(_model, _diarization_pipeline, _vad_model, reason=\"disconnect\")\n")
sub("    async def _flush_pending(self, model, diarizer, reason: str):\n",
    "    async def _flush_pending(self, model, diarizer, vad_model, reason: str):\n")
sub("        try:\n"
    "            _vad_model = __import__(\"backend.stt.engine\", fromlist=[\"_vad_model\"])._vad_model\n"
    "            if _vad_model is not None:\n"
    "                _vad_model.reset_states()\n"
    "        except Exception:\n"
    "            pass\n",
    "        if vad_model is not None:\n"
    "            try:\n"
    "                vad_model.reset_states()\n"
    "            except Exception:\n"
    "                pass\n")
# log the text before the send so a failed delivery never loses it
sub("            logger.info(\"Utterance %d | audio=%.1fs | latency=%.3fs\", self._utterance_id, duration_audio, latency)\n",
    "            logger.info(\"Utterance %d | audio=%.1fs | latency=%.3fs | %s | %r\",\n"
    "                        self._utterance_id, duration_audio, latency, speaker, text)\n")
p.write_text(t, encoding="utf-8")
print("raffinements appliques:", n)
