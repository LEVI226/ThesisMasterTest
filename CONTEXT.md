# Context for Next Codex Window

Project root: `C:\Users\ulric\Documents\ThesisMasterTest`

Current date of this handoff: 2026-08-28

## User Goal

The user is working on Topic 2 of a BIT/Nestle master thesis: an AI-driven multimodal accessibility platform focused on advanced speech-to-text for noisy, multilingual meeting-like audio.

The requested working style is code-first, academically strict, and supervisor-like: act as senior AI expert, academic supervisor, scientific director, co-writer, and tutor. The work should stay aligned with the thesis expectations and avoid overstating results.

Important: the user previously pasted API keys/secrets in chat. Do not repeat them. Remind the user to rotate/regenerate those keys after the work.

## Academic Scope

Topic 2 is not a generic RAG chatbot topic. The core thesis contribution is speech-to-text evaluation/adaptation for accessibility:

- multilingual STT: French, English, German, plus automatic language detection
- robustness under noisy audio
- comparison of architectures/models such as Whisper, MMS/wav2vec 2.0, Conformer
- adaptation/fine-tuning such as LoRA where supported
- real-time or near-real-time transcription behavior
- accessibility relevance for meetings and hearing-impaired users

Academic truth constraints:

- This is an academic prototype, not a production Nestle system.
- MInDS-14 is a telephone banking dataset, not a representative corporate meeting benchmark.
- The current streaming path is VAD-segmented batch processing, not true frame-synchronous streaming.
- Diarization is experimental.
- There is no completed end-user study with hearing-impaired participants.
- OCR/RAG is secondary to Topic 2, not the central thesis contribution.

## Implemented Research Dashboard

The approved UI shape was an English `/research` page using the "RQ Evidence Spine" concept:

- one dashboard page at `/research`
- synthesis organized by research question
- expandable details and claim-to-evidence traceability
- English UI
- academic tone, evidence-first, no inflated claims

Main implemented files:

- `backend/evaluation/research_dashboard.py`
- `frontend/research.html`
- `backend/main.py`
- `tests/test_research_dashboard.py`
- `tests/test_statistics.py`
- `frontend/index.html`
- `README.md`
- `DESIGN.md`
- `.impeccable/design.json`
- `.impeccable/surfaces/frontend-research-html.md`

Key backend routes added:

- `GET /research`
- `GET /api/research/evidence`

Dashboard content:

- RQ1 robustness:
  - noise penalty around 35.3 WER points with confidence interval
  - model-size comparison
  - MMS vs Conformer comparison
- RQ2 adaptation:
  - LoRA improvement around 1.0 WER point
  - confidence interval crosses zero, so it must be presented cautiously
  - model-size ladder
- RQ3 real-time:
  - live latency summary from `results/live_latency.csv`
  - diarization DER descriptive summary
  - explicit 0.6s VAD endpointing caveat

The dashboard includes:

- sticky research-question rail
- accessible evidence modal/dialog
- focus trap
- Escape close
- focus restoration
- inert background and body scroll lock while dialog is open
- `aria-current="location"` on active nav
- loading/error/retry states
- accessible charts and data tables
- themed scrollbars
- responsive desktop/mobile CSS
- reduced motion support

## Verification Already Done

Tests:

- full test suite passed: `45 passed`
- JavaScript syntax check passed via `new Function(script)`
- `git diff --check` clean except expected Windows LF/CRLF warnings

HTTP/API verification:

- `/research` returned 200 when server was running
- `/api/research/evidence` returned 3 research questions
- current evidence data loaded from canonical CSVs

Known warning:

- `results/live_latency.csv` is newer than `results/statistical_audit_revised.md`
- dashboard intentionally surfaces a staleness/configuration warning instead of hiding it

Visual/browser verification:

- A visual screenshot pass was not completed yet.
- Browser runtime reported `No browser is available`.
- `agent.browsers.list()` returned `[]`.

## Current Server State

A lightweight uvicorn server was started on port `8012`:

```powershell
Start-Process -FilePath '.venv\Scripts\python.exe' -ArgumentList '-m','uvicorn','backend.main:app','--host','127.0.0.1','--port','8012','--lifespan','off' -WorkingDirectory 'C:\Users\ulric\Documents\ThesisMasterTest' -WindowStyle Hidden -PassThru
```

Dashboard URL:

```text
http://127.0.0.1:8012/research
```

API URL:

```text
http://127.0.0.1:8012/api/research/evidence
```

Port `8001` had older/stale Python processes in earlier work. Do not kill unknown Python processes unless the user explicitly approves the exact scope.

## Playwright MCP Status

The user installed Microsoft Playwright MCP using:

```powershell
& "C:\Users\ulric\.antigravity-ide\extensions\openai.chatgpt-26.721.30844-win32-x64\bin\windows-x86_64\codex.exe" mcp add playwright -- npx "@playwright/mcp@latest"
```

The file `C:\Users\ulric\.codex\config.toml` contains:

```toml
[mcp_servers.playwright]
command = "npx"
args = ["@playwright/mcp@latest"]
```

However, in the prior session, `codex mcp list` only saw Playwright when `CODEX_HOME` was forced:

```powershell
$env:CODEX_HOME='C:\Users\ulric\.codex'
& "C:\Users\ulric\.antigravity-ide\extensions\openai.chatgpt-26.721.30844-win32-x64\bin\windows-x86_64\codex.exe" mcp list
```

Recommended persistent fix:

```powershell
[Environment]::SetEnvironmentVariable("CODEX_HOME", "C:\Users\ulric\.codex", "User")
```

Then fully restart Antigravity/Codex and open a new project session.

In the new window, check whether tools named like `mcp__playwright__...` are available. If not, search tool discovery for Playwright MCP. If still unavailable, use the Browser plugin diagnostic path or ask the user to confirm the new session inherited `CODEX_HOME`.

## Impeccable Skill Work

The `impeccable` skill was used for the research UI. It produced and validated:

- `.impeccable/surfaces/frontend-research-html.md`
- `DESIGN.md`
- `.impeccable/design.json`

Reviewer disposition was `ship`, with the caveat that visual rendering remained unverified because no browser runtime was available.

If doing further frontend/UI polish, use the `impeccable` skill again and follow its workflow.

## Suggested Next Steps

High-priority next actions:

1. Use Playwright MCP or Browser plugin to visually test `http://127.0.0.1:8012/research`.
2. Capture desktop and mobile screenshots.
3. Verify modal accessibility:
   - open Evidence Trail
   - focus stays inside dialog
   - Escape closes
   - focus returns to trigger
   - background is inert
4. Verify responsive layout:
   - no overlapping text
   - no horizontal overflow
   - sticky RQ rail works or degrades cleanly on mobile
5. If screenshots reveal issues, patch `frontend/research.html`, rerun tests, and update `DESIGN.md` if design materially changes.

Academic next actions:

1. Align thesis Results and Discussion chapters with the dashboard evidence.
2. Decide whether to update `results/statistical_audit_revised.md` from the current live latency CSV or preserve the warning intentionally.
3. Add a short "limitations and validity threats" section emphasizing dataset mismatch, pilot sample size, segmented streaming, and lack of user study.
4. Prepare a concise supervisor-facing narrative: what was tested, what was supported, what remains preliminary.

## Useful Commands

Run tests:

```powershell
.venv\Scripts\python.exe -m pytest
```

Start lightweight server:

```powershell
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8012 --lifespan off
```

Check dashboard:

```powershell
Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8012/research'
```

Check evidence API:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8012/api/research/evidence'
```

Check Codex MCP servers with forced home:

```powershell
$env:CODEX_HOME='C:\Users\ulric\.codex'
& "C:\Users\ulric\.antigravity-ide\extensions\openai.chatgpt-26.721.30844-win32-x64\bin\windows-x86_64\codex.exe" mcp list
```

## Handoff Prompt for New Window

Use this as the first message in the new Codex window:

```text
Lis CONTEXT.md et reprends exactement depuis là. Mon projet est C:\Users\ulric\Documents\ThesisMasterTest. Je veux que tu testes /research avec Playwright MCP si disponible, sinon diagnostique pourquoi il n'est pas exposé. Ensuite corrige les problèmes visuels ou d'accessibilité trouvés, puis rerun les tests.
```
