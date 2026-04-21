# Project 4 — Autonomous Lead Qualification Agent

> **Target:** NightOwl & any sales/marketing automation role  
> **Why it lands jobs:** Hits every keyword in NightOwl's JD — lead generation, autonomous multi-step, CRM integration, minimal human intervention  
> **You already built:** PropFlow — same logic, just adding the agent brain (tool calling) on top

---

## What This Builds

A fully autonomous AI agent that takes a lead (name + company) and without any human input:

1. Researches the company via web search
2. Scores lead quality 0–100 based on company size, fit, and intent signals
3. Drafts a personalized outreach email based on research findings
4. Logs the full lead profile to Supabase
5. Sends a Telegram notification with score and summary

Zero human input after the lead arrives.

---

## Free Tools Used

| Tool | Purpose | Cost | Sign Up |
|---|---|---|---|
| **Groq API** | LLM for reasoning + email drafting | Free tier | console.groq.com |
| **Serper API** | Web search for company research | 2,500 free searches/month | serper.dev |
| **Supabase** | Store lead profiles + interaction logs | Free tier (500MB) | supabase.com |
| **Telegram Bot API** | Instant alerts to your phone | Free, no limits | @BotFather on Telegram |
| **Python-dotenv** | Load env variables from .env | Free | pip install |

> **No OpenAI required.** Groq is free and OpenAI-compatible. Serper gives 2,500 free searches/month — more than enough to build and demo this project.

---

## Architecture Overview

```
Lead arrives (name + company)
        │
        ▼
┌─────────────────────┐
│   Agent Core        │  ← Groq LLM + tool calling
│   (agent.py)        │    decides which tools to call
└─────────┬───────────┘
          │
    ┌─────┴──────┐
    │            │
    ▼            ▼
┌────────┐  ┌──────────┐
│ Serper │  │ Groq LLM │
│Web     │  │Reasoning │
│Search  │  │+ Scoring │
└────┬───┘  └────┬─────┘
     │           │
     └─────┬─────┘
           │
           ▼
┌─────────────────────┐
│  Score + Draft      │  ← Lead score 0-100
│  Email Generator    │     Personalized email draft
└─────────┬───────────┘
          │
    ┌─────┴──────┐
    │            │
    ▼            ▼
┌──────────┐ ┌──────────┐
│Supabase  │ │Telegram  │
│Log lead  │ │Alert you │
│profile   │ │instantly │
└──────────┘ └──────────┘
```

---

## How Tool Calling Powers This

This is NOT hardcoded logic. The Groq LLM **decides** which tools to call and in what order based on the lead data. This is what makes it an agent, not just a script.

### Tools the agent can call

```
Tool 1: search_company(company_name)
→ Calls Serper API
→ Returns: website, description, industry, size signals, recent news

Tool 2: search_recent_activity(company_name)
→ Calls Serper API with a recency filter
→ Returns: recent funding, hiring activity, product launches, press mentions

Tool 3: score_lead(research_data)
→ LLM analyzes all research
→ Returns: score 0-100, reasoning, fit assessment, risk flags

Tool 4: draft_outreach_email(lead_data, research, score)
→ LLM drafts personalized email
→ Returns: subject line, email body, key talking points

Tool 5: log_to_supabase(full_lead_profile)
→ Saves everything to DB
→ Returns: confirmation + lead ID

Tool 6: send_telegram_alert(lead_summary)
→ Sends notification to analyst
→ Returns: message sent confirmation
```

### Why this is better than hardcoded logic

Hardcoded (old way):
```
step 1 → always search company
step 2 → always search news  
step 3 → always score
step 4 → always email
```

Agent with tool calling (new way):
```
Agent sees lead → decides:
"This is a well-known company, I already have enough context,
 skip extra research and go straight to scoring."

Or:

"This company name is ambiguous, I need to search more
 before I can score accurately."
```

The AI adapts the research depth based on what it finds. That is agent behavior.

---

## Full Agent Flow — Step by Step

### Step 1 — Lead arrives

Input format (from webhook, form, or CLI):
```json
{
  "lead_name": "Maria Santos",
  "company": "TechCorp PH",
  "email": "maria@techcorph.com",
  "source": "website_form"
}
```

Trigger: HTTP POST to `/qualify-lead` endpoint, n8n webhook, or direct Python call.

---

### Step 2 — Agent starts tool calling loop

The agent receives the lead data and begins the ReAct loop:

```
REASON: I need to research TechCorp PH before I can score this lead.
ACT: call search_company("TechCorp PH")
OBSERVE: Company is a 50-person SaaS startup in Manila, raised $2M in 2024, 
         builds HR software for SMEs.

REASON: I should check for recent activity to see if they're growing.
ACT: call search_recent_activity("TechCorp PH")
OBSERVE: They posted 3 job openings last month, recently expanded to Singapore.

REASON: Enough data to score. Growing company, relevant industry, expansion phase.
ACT: call score_lead(all research data)
OBSERVE: Score = 78. Good fit. Active growth signals. No red flags.

REASON: Score is above 60. Draft personalized outreach email.
ACT: call draft_outreach_email(lead data + research + score)
OBSERVE: Email drafted referencing their Singapore expansion.

REASON: Log everything and notify analyst.
ACT: call log_to_supabase(full profile)
ACT: call send_telegram_alert(summary)
OBSERVE: Both done. Task complete.
```

---

### Step 3 — Serper API web search

Serper is a Google Search API wrapper. Each tool call sends a query to Serper and gets back structured results.

**What search_company returns:**
```json
{
  "company": "TechCorp PH",
  "description": "HR software for SMEs in Southeast Asia",
  "industry": "SaaS / HR Tech",
  "size_signals": "50-100 employees based on LinkedIn",
  "website": "techcorph.com",
  "founded": "2021",
  "recent_news": ["Raised $2M seed round, expanded to Singapore"]
}
```

**What search_recent_activity returns:**
```json
{
  "hiring": "3 open roles on LinkedIn (Sales, Marketing, Backend)",
  "news": "TechCorp PH opens Singapore office — Jan 2026",
  "social": "Active on LinkedIn, posting 2-3x/week"
}
```

Serper free tier: **2,500 searches/month**. Each lead qualification uses 2 searches. That's **1,250 leads/month for free**.

---

### Step 4 — Lead scoring logic (done by LLM)

The agent does NOT use hardcoded scoring rules. The Groq LLM reasons about the research and assigns a score with explanation.

**System prompt for scoring:**
```
You are a lead qualification specialist.

Analyze this research about a company and score the lead 0-100.

Scoring criteria:
- Company size fit (10-500 employees = good fit): +20 points
- Industry relevance: +20 points  
- Growth signals (hiring, funding, expansion): +20 points
- Recent activity (active online, news): +15 points
- Decision maker seniority (title of lead): +15 points
- No red flags (no layoffs, no bad press): +10 points

Return JSON:
{
  "score": 78,
  "tier": "HOT | WARM | COLD",
  "reasoning": "explanation of score",
  "key_talking_points": ["point 1", "point 2"],
  "risk_flags": ["any concerns"],
  "recommended_action": "immediate outreach | nurture | disqualify"
}
```

**Score tiers:**
- **80–100 = HOT** — immediate outreach, personal call
- **60–79 = WARM** — personalized email, follow up in 3 days
- **40–59 = COLD** — add to nurture sequence
- **0–39 = DISQUALIFY** — not a fit, log and skip

---

### Step 5 — Email drafting (done by LLM)

The LLM uses the research findings to write a personalized outreach email. Not a template — an actual email referencing specific things found during research.

**What the drafted email looks like:**
```
Subject: Congrats on the Singapore expansion, Maria

Hi Maria,

I came across TechCorp PH while researching growing HR tech 
companies in Southeast Asia — the Singapore expansion caught 
my attention.

Companies in your growth phase (and with 3 open roles to fill) 
often run into the same challenge: scaling people operations 
without scaling headcount proportionally.

[Your product/service value proposition here]

Would a 20-minute call this week make sense?

Best,
[Your name]
```

The email references:
- The Singapore expansion (from search results)
- Their hiring activity (from recent activity search)
- Their specific growth stage

This is why the email is personalized — the agent found these specifics during research.

---

### Step 6 — Supabase logging

Every lead is logged to the `leads` table with the full research profile.

#### `leads` table schema

```sql
CREATE TABLE leads (
  id                uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at        timestamptz DEFAULT now(),

  -- Lead info
  lead_name         text NOT NULL,
  company           text NOT NULL,
  email             text,
  source            text,

  -- Research results  
  company_size      text,
  industry          text,
  description       text,
  recent_news       text[],
  hiring_signals    text,
  website           text,

  -- Agent output
  score             integer,
  tier              text CHECK (tier IN ('HOT', 'WARM', 'COLD', 'DISQUALIFY')),
  score_reasoning   text,
  key_talking_points text[],
  risk_flags        text[],
  recommended_action text,
  email_draft       text,
  email_subject     text,

  -- Status
  status            text DEFAULT 'new',
  agent_steps       integer
);
```

**Create in Supabase:**
Go to SQL Editor → paste the above → Run.

---

### Step 7 — Telegram alert

When the agent finishes, it sends a Telegram message immediately.

**Format of the alert:**
```
🎯 NEW LEAD QUALIFIED
━━━━━━━━━━━━━━━━━━━━
Lead: Maria Santos
Company: TechCorp PH
Email: maria@techcorph.com

Score: 78/100 🔥 WARM

Key findings:
• 50-person SaaS startup in HR Tech
• Raised $2M seed, expanding to Singapore
• 3 open roles on LinkedIn (active growth)
• Founded 2021 — right growth stage

Talking points:
• Singapore expansion timing
• Scaling ops without headcount growth

Recommended: Personalized email → follow up in 3 days

Email draft saved to Supabase.
━━━━━━━━━━━━━━━━━━━━
```

You get this on your phone within seconds of a lead arriving.

---

## File Structure

```
project4-lead-agent/
│
├── .env                    # secrets — never commit
├── .gitignore              # include: .env, __pycache__, *.pyc
├── requirements.txt
├── README.md
│
├── agent.py                # main agent loop — tool calling orchestration
├── tools.py                # all 6 tool functions
├── llm.py                  # Groq API calls — scoring + email drafting  
├── search.py               # Serper API wrapper — company + news search
├── database.py             # Supabase client — log_lead()
├── notifier.py             # Telegram bot — send_alert()
└── main.py                 # entry point — accepts lead input, runs agent
```

---

## Environment Variables

Create a `.env` file in your project root:

```bash
# LLM — Groq (free, no credit card)
# Get from: console.groq.com → API Keys → Create Key
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
GROQ_MODEL=llama-3.1-8b-instant

# Web Search — Serper (2,500 free searches/month)
# Get from: serper.dev → Sign up → Dashboard → API Key
SERPER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Database — Supabase (free 500MB)
# Get from: supabase.com → Project → Settings → API
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Notifications — Telegram (free, no limits)
# BOT_TOKEN: Telegram → @BotFather → /newbot
# CHAT_ID: message your bot → api.telegram.org/bot{TOKEN}/getUpdates → chat.id
TELEGRAM_BOT_TOKEN=7234567890:AAHxxxxxxxxxxxxxxxxxxxxx
TELEGRAM_CHAT_ID=123456789

# Scoring thresholds (optional — these are defaults)
HOT_THRESHOLD=80
WARM_THRESHOLD=60
COLD_THRESHOLD=40
```

---

## Install Commands

```bash
# 1. Create project and virtual environment
mkdir project4-lead-agent
cd project4-lead-agent
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install groq               # LLM client (free, OpenAI-compatible)
pip install requests           # Serper + Telegram API calls
pip install supabase           # database client
pip install python-dotenv      # load .env file

# 3. Save requirements
pip freeze > requirements.txt

# 4. Test Serper (check your key works)
curl "https://google.serper.dev/search" \
  -H "X-API-KEY: your_serper_key" \
  -H "Content-Type: application/json" \
  -d '{"q": "TechCorp PH company"}' 

# 5. Run the agent with a test lead
python main.py --name "Maria Santos" --company "TechCorp PH" --email "maria@techcorph.com"
```

---

## Build Phases

### Phase 1 — Serper web search wrapper
Build `search.py`. Test that searching a company name returns useful results. This is your data source — everything else depends on it working.

**Test:** `python search.py "Grab Philippines"` → should return company description, size, recent news.

---

### Phase 2 — Tool definitions
Build `tools.py`. Define all 6 tools as Groq-compatible function definitions (same format as OpenAI function calling). Each tool has: name, description, parameters.

**Key point:** The description field is what the LLM reads to decide whether to call this tool. Write it clearly — "Search the web for company information including size, industry, and recent news."

---

### Phase 3 — LLM scoring + email drafting
Build `llm.py`. Two functions: `score_lead()` and `draft_email()`. Both call Groq with structured system prompts and return JSON output.

**Test score_lead():** Pass fake research data → should return a score + reasoning.  
**Test draft_email():** Pass fake lead + research → should return personalized email.

---

### Phase 4 — Supabase logging
Build `database.py`. One function: `log_lead(lead_profile)`. Creates a row in the `leads` table with all research and agent output.

**Test:** Run the function with mock data → check Supabase table editor to see the row.

---

### Phase 5 — Telegram alerts
Build `notifier.py`. One function: `send_alert(lead_summary)`. Formats and sends the Telegram message.

**Test:** Call `send_alert()` with mock data → check your Telegram for the message.

---

### Phase 6 — Agent core (tool calling loop)
Build `agent.py`. This is the ReAct loop that orchestrates all tools. The LLM decides which tool to call next based on what each tool returns.

**Test:** Run with a real company name → watch the agent call tools in sequence → check Supabase for the logged lead → check Telegram for the alert.

---

### Phase 7 — Wire up entry point
Build `main.py`. Accepts lead input (CLI args or HTTP POST) and calls the agent. This is what n8n or a webhook will call in production.

---

## Testing Checklist

Run these test cases before calling the project done:

```
✅ Test 1 — Known company (should score HIGH)
   Input: name="John", company="Shopify", email="john@shopify.com"
   Expected: Score 70+, HOT/WARM tier, Telegram alert received, row in Supabase

✅ Test 2 — Unknown small company (agent should do more research)
   Input: name="Ana", company="LocalPH Startup XYZ", email="ana@local.ph"
   Expected: Agent runs 2 searches, lower score, COLD/WARM tier

✅ Test 3 — Disqualify case
   Input: name="Bob", company="Bankrupt Corp", email="bob@test.com"
   Expected: Score below 40, DISQUALIFY tier, no email drafted

✅ Test 4 — Check Supabase
   All 3 test leads should appear in the leads table with correct tier

✅ Test 5 — Check agent steps count
   agent_steps column should show how many tool calls the agent made per lead
```

---

## How to Present This on GitHub

**README should highlight:**
- "Fully autonomous — zero human input after lead arrives"
- "Multi-step AI agent using function calling — not hardcoded logic"
- "Integrates with: Serper (web research), Supabase (CRM logging), Telegram (real-time alerts)"
- "Scores leads 0–100 using AI reasoning across company size, growth signals, and industry fit"
- "Drafts personalized outreach emails referencing specific research findings"

**Add to README:**
- Architecture diagram (the ASCII one from this doc)
- Example Telegram alert screenshot
- Example email output
- Supabase table screenshot showing logged leads

---

## Connection to Your Existing Work

| What you built in PropFlow | What this adds |
|---|---|
| Typebot conversational intake | Replaced by: lead arrives via webhook |
| n8n webhook trigger | Same concept — agent is triggered the same way |
| Supabase lead storage | Same — just more fields |
| Telegram agent notifications | Same exact pattern |
| Lead scoring via conditional logic | Upgraded to: LLM reasoning-based scoring |
| Static email templates | Upgraded to: AI-generated personalized drafts |
| Hardcoded pipeline steps | Upgraded to: agent decides steps via tool calling |

PropFlow was the foundation. This is PropFlow with an agent brain.

---

## How This Connects to Cybersecurity Later

| This agent skill | Security equivalent |
|---|---|
| Web search to research company | OSINT — gathering intel on threat actors |
| Multi-step tool calling | SOAR playbook — agent calls enrichment APIs in sequence |
| Scoring leads with reasoning | Alert triage — scoring threat severity with context |
| Logging to Supabase | Incident log — every alert action recorded |
| Telegram escalation | SOC notification — alert analyst when threshold exceeded |

The patterns are identical. You're learning SOAR architecture by building this lead agent.

---

*Project 4 of 4 — Autonomous Lead Qualification Agent*  
*Stack: Groq (free) · Serper (free) · Supabase (free) · Telegram (free)*  
*Target: NightOwl AI Agent Developer role*
