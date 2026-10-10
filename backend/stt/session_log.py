"""Per-session JSONL log for live transcription.

Enabled only when STT_SESSION_LOG_DIR is set, so the historical behaviour of
the server is unchanged. One file per WebSocket session, one JSON object per
line. The first line is a header describing the environment and the model
that is actually loaded (not merely requested).

Clock domains
-------------
- ``wall_iso``: server wall clock, ISO 8601 with timezone. Comparable across
  machines only if their clocks are synchronised; used for ordering and audit.
- ``mono``: ``time.monotonic()`` on the server. Only differences between two
  ``mono`` values from the SAME session are meaningful. All latencies in this
  log are differences of ``mono`` values.
- Nothing here measures the browser: receipt and rendering happen after the
  last event a server can observe (``send_json``).
"""
from __future__ import annotations

import json
import os
import platform
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _versions() -> dict:
    out = {"python": sys.version.split()[0]}
    for mod in ("faster_whisper", "ctranslate2", "torch", "pyannote.audio", "numpy"):
        try:
            m = __import__(mod, fromlist=["__version__"])
            out[mod] = getattr(m, "__version__", "?")
        except Exception:
            out[mod] = None
    return out


class SessionLog:
    """Append-only JSONL writer. Every method is a no-op when disabled."""

    def __init__(self, kind: str, options: dict | None = None):
        self.session_id = f"{datetime.now().strftime('%Y%m%dT%H%M%S')}_{uuid.uuid4().hex[:6]}"
        self.kind = kind
        d = os.environ.get("STT_SESSION_LOG_DIR")
        self.path: Path | None = None
        if d:
            self.path = Path(d) / f"{kind}_{self.session_id}.jsonl"
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self.t0_mono = time.monotonic()
        self.n = 0
        self._write_header(options or {})

    @property
    def enabled(self) -> bool:
        return self.path is not None

    # ------------------------------------------------------------ writing
    def _write(self, obj: dict) -> None:
        if not self.path:
            return
        obj = {"seq": self.n, "wall_iso": datetime.now(timezone.utc).astimezone().isoformat(),
               "mono": round(time.monotonic(), 6), **obj}
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
        self.n += 1

    def _write_header(self, options: dict) -> None:
        try:
            from backend.stt.engine import get_model_info
            model = get_model_info()
        except Exception as e:  # engine not importable in some test setups
            model = {"error": repr(e)}
        self._write({
            "event": "session_start",
            "session_id": self.session_id,
            "kind": self.kind,
            "model_loaded": model,
            "options": options,
            "versions": _versions(),
            "platform": {"system": platform.system(), "release": platform.release(),
                         "machine": platform.machine(), "processor": platform.processor()},
            "clock_domains": {
                "wall_iso": "server wall clock, ISO 8601 with tz",
                "mono": "time.monotonic() on the server; only same-session differences are meaningful",
                "latency_seconds": "mono difference: end-of-speech decision (or flush trigger) -> just before send_json; excludes network and browser rendering",
            },
        })

    def event(self, name: str, **fields: Any) -> None:
        self._write({"event": name, **fields})

    def close(self, **fields: Any) -> None:
        self._write({"event": "session_end",
                     "elapsed_mono": round(time.monotonic() - self.t0_mono, 3), **fields})
