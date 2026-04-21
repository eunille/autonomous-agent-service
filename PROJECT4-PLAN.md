# Project 4 — Autonomous Lead Qualification Agent
## Implementation Plan & Phase Tracker

> **Status:** 🔴 Not Started  
> **Stack:** Python (backend) · Groq · Serper · Supabase · Telegram · Next.js (frontend)  
> **Target Role:** NightOwl AI Agent Developer

---

## Senior Dev Review Notes

### ✅ Architecture Strengths
- **ReAct pattern** (Reason → Act → Observe) — industry standard for agentic AI
- **Tool calling over hardcoded logic** — real agent behavior, not a script
- **Free-tier stack** — Groq + Serper + Supabase + Telegram = zero cost to demo
- **Clean file separation** — agent.py / tools.py / llm.py = maintainable + testable
- **Tiered scoring (HOT/WARM/COLD/DISQUALIFY)** — real CRM logic, shows business context

### ⚠️ Production Gaps to Address
| Issue | Fix |
|---|---|
| No max-step guard on ReAct loop | Add `max_iterations=10` to agent.py |
| No webhook auth on `/qualify-lead` | Add API key header validation in main.py |
| No retry logic on Serper/Groq | Use `tenacity` for exponential backoff |
| Input not validated before DB write | Sanitize all lead fields at entry point |
| Static CHAT_ID for Telegram | Route notifications per lead tier |
| No job queue for concurrent leads | Use Redis or simple queue |

---

## Phase Tracker

### Phase 1 — Python Backend Core
> **Status:** ✅ Done  
> **Files:** `backend/search.py` · `backend/tools.py` · `backend/llm.py` · `backend/requirements.txt` · `backend/.env.example`

**Goals:**
- [x] Build Serper API wrapper (`search_company` + `search_recent_activity`)
- [x] Define all 6 Groq tool schemas (OpenAI-compatible function calling format)
- [x] Build `score_lead()` — Groq LLM with structured JSON output
- [x] Build `draft_email()` — personalized email generator
- [x] Input sanitization, timeout handling, structured error returns
- [ ] Live test with real API keys (requires .env)

**Test Commands:**
```bash
python search.py "Grab Philippines"   # should return company data
python llm.py                         # test score + email draft with mock data
```

**Definition of Done:**
- `search.py` returns structured company + news data for any company name
- `llm.py` returns valid score JSON (0-100, tier, reasoning, talking points)
- `llm.py` returns valid personalized email draft
- All 6 tool schemas accepted by Groq's function calling API

---

### Phase 2 — Agent ReAct Loop
> **Status:** ✅ Done  
> **Files:** `backend/agent.py`

**Goals:**
- [x] ReAct loop (Reason → Act → Observe → repeat) via Groq tool calling
- [x] `max_iterations=10` guard (configurable via `AGENT_MAX_ITERATIONS` env var)
- [x] `agent_steps` counter tracking every tool call
- [x] Context injection — auto-fills tool args from previously collected results
- [x] Graceful error handling — tool failures return structured dicts, agent continues
- [x] `AgentRun` dataclass captures full state: messages, tool_results, steps, errors
- [x] `_build_lead_profile()` assembles full Supabase record from all tool outputs
- [x] `_build_telegram_summary()` assembles alert dict from all tool outputs

**Goals:**
- [ ] Implement the ReAct loop (Reason → Act → Observe → repeat)
- [ ] Add `max_iterations=10` guard
- [ ] Track `agent_steps` count
- [ ] Handle tool call errors gracefully (catch + log, don't crash)
- [ ] Wire all tools from tools.py into the agent

**Definition of Done:**
- Agent runs end-to-end on a real company name
- Agent calls tools in adaptive order (not hardcoded sequence)
- Agent stops gracefully at max_iterations or task completion

---

### Phase 3 — Integrations (Supabase + Telegram)
> **Status:** ✅ Done  
> **Files:** `backend/database.py` · `backend/notifier.py`

**Goals:**
- [x] `database.py` → `log_lead()` with full schema insert, input sanitization, safe type coercion
- [x] `notifier.py` → `send_alert()` with tier-based emoji, HTML formatting, Telegram HTML parse mode
- [x] All fields capped to max DB column lengths before insert
- [x] Both modules return structured `{success, error}` dicts — never crash the agent
- [ ] Live test with real Supabase + Telegram keys

**Goals:**
- [ ] Create `leads` table in Supabase (SQL schema from docs)
- [ ] Build `log_lead()` — full profile insert
- [ ] Build `send_alert()` — tier-formatted Telegram message
- [ ] Test both independently with mock data

**Supabase Schema:**
```sql
CREATE TABLE leads (
  id                uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at        timestamptz DEFAULT now(),
  lead_name         text NOT NULL,
  company           text NOT NULL,
  email             text,
  source            text,
  company_size      text,
  industry          text,
  description       text,
  recent_news       text[],
  hiring_signals    text,
  website           text,
  score             integer,
  tier              text CHECK (tier IN ('HOT', 'WARM', 'COLD', 'DISQUALIFY')),
  score_reasoning   text,
  key_talking_points text[],
  risk_flags        text[],
  recommended_action text,
  email_draft       text,
  email_subject     text,
  status            text DEFAULT 'new',
  agent_steps       integer
);
```

**Definition of Done:**
- Mock lead appears in Supabase table after `log_lead()` call
- Telegram receives formatted alert with correct tier emoji
- Errors don't crash — they log and continue

---

### Phase 4 — Entry Point + API
> **Status:** ✅ Done  
> **Files:** `backend/main.py`

**Goals:**
- [x] CLI interface: `python main.py --name "X" --company "Y" --email "z@z.com"`
- [x] HTTP POST endpoint: `POST /qualify-lead` (FastAPI)
- [x] Input validation (email format, required fields, max length via Pydantic)
- [x] API key auth header check (`X-API-Key` → `API_SECRET_KEY`)
- [x] CORS middleware configured
- [x] `GET /health` endpoint for uptime checks
- [x] `--serve` flag to start the FastAPI server
- [x] Structured `LeadResponse` schema with score, tier, lead_id, telegram_sent

**Goals:**
- [ ] CLI interface: `python main.py --name "X" --company "Y" --email "z@z.com"`
- [ ] HTTP POST endpoint: `POST /qualify-lead` (FastAPI)
- [ ] Input validation (email format, required fields, max length)
- [ ] API key auth header check
- [ ] Rate limiting (max 10 req/min)
- [ ] `requirements.txt` locked versions

**Definition of Done:**
- CLI triggers full agent run end-to-end
- HTTP endpoint rejects malformed input with 422
- Unauthorized requests rejected with 401
- Full qualifying run completes in < 30 seconds

---

### Phase 5 — Frontend Landing Page (Next.js)
> **Status:** ✅ Done  
> **Files:** `app/page.tsx` · `components/landing/` (10 components)

**Sections built:**
- [x] `nav.tsx` — Fixed sticky nav with logo, section links, GitHub CTA
- [x] `hero.tsx` — Headline, terminal preview showing real agent output
- [x] `stats.tsx` — 4 key metrics (0 human input, 6 tools, 30s, 100pts)
- [x] `how-it-works.tsx` — 6-step ReAct timeline with color-coded stages
- [x] `tools.tsx` — 6 agent tool cards with icons, descriptions, API labels
- [x] `scoring.tsx` — HOT/WARM/COLD/DISQUALIFY tiers + scoring criteria
- [x] `demo.tsx` — Interactive demo form with animated agent steps + mock output
- [x] `architecture.tsx` — Visual flow diagram (CSS-only, no external lib)
- [x] `stack.tsx` — 4 free tools with details
- [x] `cta.tsx` — Final CTA + GitHub link
- [x] `footer.tsx` — Minimal footer

**Planned Sections:**
- [ ] **Hero** — value prop headline, "Zero human input" badge, CTA buttons
- [ ] **How It Works** — ReAct loop (5 steps) with animated timeline
- [ ] **Tools** — 6 agent tools with icons and descriptions
- [ ] **Architecture** — visual flow diagram (React-based, no external lib)
- [ ] **Scoring** — HOT / WARM / COLD / DISQUALIFY tier breakdown with examples
- [ ] **CTA** — GitHub link + demo badge

**Definition of Done:**
- Page is pixel-polished, dark mode by default
- All sections mobile-responsive
- Loads < 1.5s (no heavy deps)

---

### Phase 6 — Testing + Demo Prep
> **Status:** ⬜ Not Started

**Test Cases:**
```
Test 1 — Known company (score HIGH)
  Input: name="John", company="Shopify", email="john@shopify.com"
  Expected: Score 70+, HOT/WARM, Telegram alert, Supabase row

Test 2 — Unknown small company (more research)
  Input: name="Ana", company="LocalPH Startup XYZ", email="ana@local.ph"
  Expected: 2 searches, lower score, COLD/WARM

Test 3 — Disqualify
  Input: name="Bob", company="Bankrupt Corp", email="bob@test.com"
  Expected: Score < 40, DISQUALIFY, no email drafted

Test 4 — Supabase check
  All 3 leads in table with correct tier

Test 5 — Agent steps
  agent_steps column shows correct tool call count per lead
```

**Demo Assets to Capture:**
- [ ] Telegram alert screenshot
- [ ] Supabase table screenshot
- [ ] Email draft output example
- [ ] Agent log showing ReAct steps

---

## File Structure Reference

```
project4-lead-agent/          ← Python backend (new folder)
├── .env
├── .gitignore
├── requirements.txt
├── agent.py
├── tools.py
├── llm.py
├── search.py
├── database.py
├── notifier.py
└── main.py

autonomousagent/              ← Next.js frontend (current workspace)
├── app/
│   ├── page.tsx              ← Landing page (Phase 5)
│   └── globals.css
└── components/
```

---

## Environment Variables Checklist

```bash
# .env — never commit
GROQ_API_KEY=          # console.groq.com → API Keys
GROQ_MODEL=llama-3.1-8b-instant
SERPER_API_KEY=        # serper.dev → Dashboard → API Key
SUPABASE_URL=          # supabase.com → Project → Settings → API
SUPABASE_KEY=          # supabase.com → Project → Settings → API
TELEGRAM_BOT_TOKEN=    # Telegram → @BotFather → /newbot
TELEGRAM_CHAT_ID=      # api.telegram.org/bot{TOKEN}/getUpdates
HOT_THRESHOLD=80
WARM_THRESHOLD=60
COLD_THRESHOLD=40
```

---

*Last updated: 2026-04-21*
