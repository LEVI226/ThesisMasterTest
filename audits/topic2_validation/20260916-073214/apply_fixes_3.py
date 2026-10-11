"""Wire SessionLog into RealTimeSTTHandler. LF-normalised edit; endings restored after."""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[3]
p = ROOT / "backend/main.py"
t = p.read_bytes().decode("utf-8").replace("\r\n", "\n")
n = 0


def sub(old, new):
    global t, n
    assert t.count(old) == 1, "%d match: %s" % (t.count(old), old[:70])
    t = t.replace(old, new); n += 1


sub("        self._utterance_id = 0\n"
    "        self._t_silence_end: float = 0.0\n",
    "        self._utterance_id = 0\n"
    "        self._t_silence_end: float = 0.0\n"
    "        self._flush_reason = \"silence\"\n"
    "        self._chunks = {\"count\": 0, \"bytes\": 0, \"min\": None, \"max\": 0}\n"
    "        from backend.stt.session_log import SessionLog\n"
    "        self.slog = SessionLog(\"live\", options={\n"
    "            \"language\": language, \"sample_rate\": self.sample_rate,\n"
    "            \"silence_threshold_s\": 0.6, \"vad_speech_prob\": 0.5,\n"
    "            \"min_utterance_bytes\": 1600, \"min_rms\": 0.01,\n"
    "            \"no_speech_threshold\": 0.6, \"log_prob_threshold\": -1.0,\n"
    "            \"compression_ratio_threshold\": 2.4,\n"
    "            \"latency_csv\": str(self.latency_csv),\n"
    "        })\n")

sub("                chunk = msg.get(\"bytes\")\n"
    "                if not chunk:\n"
    "                    continue\n",
    "                chunk = msg.get(\"bytes\")\n"
    "                if not chunk:\n"
    "                    continue\n"
    "                c = self._chunks\n"
    "                c[\"count\"] += 1; c[\"bytes\"] += len(chunk)\n"
    "                c[\"min\"] = len(chunk) if c[\"min\"] is None else min(c[\"min\"], len(chunk))\n"
    "                c[\"max\"] = max(c[\"max\"], len(chunk))\n")

sub("            await self._flush_pending(_model, _diarization_pipeline, _vad_model, reason=\"disconnect\")\n"
    "            logger.info(\"WebSocket STT client disconnected.\")\n",
    "            await self._flush_pending(_model, _diarization_pipeline, _vad_model, reason=\"disconnect\")\n"
    "            self.slog.close(utterances=self._utterance_id, chunks=self._chunks)\n"
    "            logger.info(\"WebSocket STT client disconnected.\")\n")

sub("        logger.info(\"Flushing pending audio (%d bytes, reason=%s)\", len(self.audio_buffer), reason)\n"
    "        self.is_speaking = False\n",
    "        logger.info(\"Flushing pending audio (%d bytes, reason=%s)\", len(self.audio_buffer), reason)\n"
    "        self._flush_reason = reason\n"
    "        self.is_speaking = False\n")

sub("        await self._transcribe_and_diarize(model, diarizer)\n"
    "        self.audio_buffer = bytearray()\n"
    "        self.silence_frames = 0\n",
    "        await self._transcribe_and_diarize(model, diarizer)\n"
    "        self._flush_reason = \"silence\"\n"
    "        self.audio_buffer = bytearray()\n"
    "        self.silence_frames = 0\n")

# --- skips and errors become log events
sub("        if len(self.audio_buffer) < 1600: # Ignore very short artifacts (<0.1s)\n"
    "            return\n",
    "        if len(self.audio_buffer) < 1600: # Ignore very short artifacts (<0.1s)\n"
    "            self.slog.event(\"skipped\", reason=\"too_short\", buffer_bytes=len(self.audio_buffer),\n"
    "                            trigger=self._flush_reason)\n"
    "            return\n")

sub("        if rms < 0.01:\n"
    "            logger.debug(\"Skipping utterance: RMS %.4f below threshold\", rms)\n"
    "            return\n",
    "        if rms < 0.01:\n"
    "            logger.debug(\"Skipping utterance: RMS %.4f below threshold\", rms)\n"
    "            self.slog.event(\"skipped\", reason=\"low_rms\", rms=round(rms, 5),\n"
    "                            buffer_bytes=len(self.audio_buffer), trigger=self._flush_reason)\n"
    "            return\n")

sub("            text = \" \".join([s.text for s in segments_gen]).strip()\n"
    "            if not text:\n"
    "                return\n",
    "            text = \" \".join([s.text for s in segments_gen]).strip()\n"
    "            if not text:\n"
    "                self.slog.event(\"skipped\", reason=\"empty_text\",\n"
    "                                buffer_bytes=len(self.audio_buffer), trigger=self._flush_reason)\n"
    "                return\n")

sub("                if text.count(chunk) > 2:\n"
    "                    logger.debug(\"Skipping hallucinated repetition: %r\", text[:60])\n"
    "                    return\n",
    "                if text.count(chunk) > 2:\n"
    "                    logger.debug(\"Skipping hallucinated repetition: %r\", text[:60])\n"
    "                    self.slog.event(\"skipped\", reason=\"repetition\", text=text,\n"
    "                                    buffer_bytes=len(self.audio_buffer), trigger=self._flush_reason)\n"
    "                    return\n")

sub("            logger.info(\"Utterance %d | audio=%.1fs | latency=%.3fs | %s | %r\",\n"
    "                        self._utterance_id, duration_audio, latency, speaker, text)\n",
    "            logger.info(\"Utterance %d | audio=%.1fs | latency=%.3fs | %s | %r\",\n"
    "                        self._utterance_id, duration_audio, latency, speaker, text)\n"
    "            self.slog.event(\"utterance\", utterance_id=self._utterance_id,\n"
    "                            trigger=self._flush_reason, buffer_bytes=len(self.audio_buffer),\n"
    "                            duration_audio_s=duration_audio, latency_seconds=latency,\n"
    "                            speaker=speaker, text=text,\n"
    "                            start_s=round(start_sec, 2), end_s=round(end_sec, 2))\n")

sub("        except Exception as e:\n"
    "            logger.error(f\"WS Transcription/Diarization failed: {e}\")\n",
    "        except Exception as e:\n"
    "            logger.error(f\"WS Transcription/Diarization failed: {e}\")\n"
    "            self.slog.event(\"error\", where=\"transcribe_and_diarize\", error=repr(e),\n"
    "                            buffer_bytes=len(self.audio_buffer), trigger=self._flush_reason)\n")

p.write_bytes(t.encode("utf-8"))
print("main.py session-log wiring:", n, "edits")
