## AutoSystems — Autonomous B2B Lead Qualification Agent

**Stack:** Next.js, Python (FastAPI), Groq AI, Gemini 1.5 Flash, Serper API, Supabase, Telegram Bot, SMTP / Gmail, Typebot, Vercel, Render

- Engineered a fully autonomous lead qualification agent that researches companies in real-time via web search, scores leads 0–100 using a dual-model LLM pipeline (Groq primary, Gemini fallback), and delivers tier-specific Telegram alerts with talking points and recommended actions — zero manual effort required.
- **Parallel research pipeline:** simultaneously queries company overview and recent activity (funding, hiring signals, news coverage) using concurrent execution — reducing total qualification time per lead.
- **Dual-model scoring with automatic fallback:** lead scoring runs on Groq (llama-3.3-70b-versatile); if Groq rate limits are exceeded, the system transparently switches to Gemini 1.5 Flash with no downtime or degradation in output quality.
- **HOT lead automation:** leads scoring ≥ 80/100 automatically trigger a personalized Gmail outreach email (HTML template, Gemini-drafted) and an urgent Telegram alert with research-backed talking points — enabling same-minute response to high-intent prospects.
- **70% token reduction** achieved by replacing a ReAct agent loop with a direct sequential pipeline — cutting per-run token usage from ~2,500 to ~700 tokens while maintaining full research depth.
- Next.js landing page captures inbound leads via a Typebot conversational form, feeds the FastAPI qualification pipeline via webhook, and logs every result to Supabase CRM — fully hands-off from capture to CRM entry.
- Deployed on Vercel (frontend) and Render (backend) with API key authentication on all endpoints and environment-isolated secrets management.
