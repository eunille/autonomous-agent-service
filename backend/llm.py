"""
Groq LLM interface for lead scoring and email drafting.
Uses OpenAI-compatible Groq SDK with structured JSON output.
Email drafting uses Gemini 1.5 Flash (higher token limits on free tier).
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

_groq_client: Groq | None = None
_gemini_client = None


def _get_groq() -> Groq:
    global _groq_client
    if _groq_client is None:
        if not GROQ_API_KEY:
            raise EnvironmentError("GROQ_API_KEY is not set.")
        _groq_client = Groq(api_key=GROQ_API_KEY)
    return _groq_client


def _get_gemini():
    global _gemini_client
    if _gemini_client is None:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise EnvironmentError("GEMINI_API_KEY is not set.")
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        _gemini_client = genai.GenerativeModel("gemini-1.5-flash")
    return _gemini_client


# Keep old name for backwards compatibility
def _get_client() -> Groq:
    return _get_groq()


def _extract_json(content: str) -> dict:
    """
    Robustly extract the first JSON object from an LLM response.
    Handles markdown code fences and extra surrounding text.
    """
    # Strip markdown code fences
    clean = re.sub(r"```(?:json)?", "", content).strip("` \n")

    # Find first JSON object
    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in LLM response:\n{content}")

    return json.loads(match.group())


# ---------------------------------------------------------------------------
# Lead scoring
# ---------------------------------------------------------------------------

SCORE_SYSTEM_PROMPT = """You are a B2B lead qualification specialist scoring inbound leads for AutoSystems — an AI sales automation agency. AutoSystems sells to companies with 10–500 employees that have active sales operations and could benefit from automating lead handling and outreach.

Score this lead 0–100 using the 4-criterion rubric below. Sum all criterion scores for the final score.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITERION 1: FIRMOGRAPHIC FIT (max 30 pts)
Is this company the right SIZE for AutoSystems?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
30 pts — 10–150 employees (sweet spot: agile, has budget, needs automation)
24 pts — 150–350 employees (good fit, slightly larger procurement)
16 pts — 350–500 employees (marginal fit, possible sales ops team already)
 8 pts — fewer than 10 employees (too early-stage, likely no budget)
 5 pts — 500–1000 employees (too large, complex procurement cycles)
 0 pts — more than 1000 employees (enterprise → HARD DISQUALIFY, cap total at 30)
If company size is unknown or unverifiable → award 13 pts

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITERION 2: SALES AUTOMATION NEED (max 25 pts)
Does this company have a sales function that would benefit from AI automation?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
25 pts — Clear sales-driven model: B2B sales team, outbound campaigns, high lead volume, or sales-critical operations (e.g. real estate, SaaS, fintech, distribution, logistics, recruitment)
20 pts — Moderate sales function: some outbound effort, growing sales team, enrollment-driven or client-acquisition model
14 pts — Limited sales: mostly inbound, owner-led sales, or early-stage
 5 pts — No identifiable sales function (e.g. pure NGO, government, content-only)
If sales operations cannot be assessed from research → award 11 pts

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITERION 3: GROWTH MOMENTUM (max 25 pts)
Is this company actively growing? Growth = budget availability + urgency to scale.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
25 pts — Raised funding (any round, any date) AND actively hiring
22 pts — Raised funding OR actively hiring sales/marketing roles
18 pts — New product launch, major partnership, market expansion, or significant press
12 pts — Some online activity, moderate news presence, but no clear growth signal
 6 pts — Minimal online presence, no growth signals found
 2 pts — Declining signals (layoffs mentioned, funding dried up, pivoting away)
If no activity data available at all → award 9 pts

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITERION 4: RISK & CREDIBILITY (max 20 pts)
Is this a legitimate, stable company to do business with?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
20 pts — Established company, no negative signals, verifiable online presence
16 pts — Legitimate but limited public info or minor old negative press
 8 pts — Active concerns: recent bad press, unclear leadership, unverified claims
 0 pts — Major red flags: mass layoffs, fraud allegations, legal action, shutdown imminent
If credibility/risk cannot be assessed → award 14 pts

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCORING TIERS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
80–100: HOT   — Strong ICP match + growth signals. Immediate personal outreach.
60–79:  WARM  — Good fit, some gaps. Personalized email + follow-up in 3 days.
40–59:  COLD  — Possible fit but insufficient signals. Add to nurture sequence.
0–39:   DISQUALIFY — Clear mismatch (enterprise, no need, major red flags).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CALIBRATION EXAMPLES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PH fintech startup, 80 employees, Series A funded, hiring sales reps, no red flags → ~92 HOT
PH edtech, 60 employees, active partnerships, no hiring signals, no red flags → ~80 HOT
PH logistics firm, 300 employees, no recent news, stable → ~61 WARM
Unknown company, no verifiable data → ~47 COLD (13+11+9+14)
Apple Inc (166,000 employees) → ~5 DISQUALIFY (0+5+22+20, hard cap)

Return ONLY a valid JSON object (no markdown, no extra text):
{
  "score": <integer 0-100>,
  "tier": "<HOT|WARM|COLD|DISQUALIFY>",
  "reasoning": "<2-3 sentence explanation referencing specific research findings>",
  "key_talking_points": ["<specific data point from research>", "<specific data point>", "<specific data point>"],
  "risk_flags": ["<specific flag>"] or [],
  "recommended_action": "<immediate outreach|personalized email|nurture sequence|disqualify>"
}"""


def score_lead(
    lead_name: str,
    company: str,
    company_info: dict[str, Any],
    recent_activity: dict[str, Any],
) -> dict[str, Any]:
    """
    Score a lead 0-100 using Groq LLM reasoning.

    Args:
        lead_name: Full name of the lead contact.
        company: Company name.
        company_info: Output from search.search_company().
        recent_activity: Output from search.search_recent_activity().

    Returns:
        dict with: score, tier, reasoning, key_talking_points, risk_flags, recommended_action
    """
    research_summary = (
        f"Lead: {lead_name} at {company}\n\n"
        f"Company Overview:\n{json.dumps(company_info, indent=2)}\n\n"
        f"Recent Activity:\n{json.dumps(recent_activity, indent=2)}"
    )

    def _parse_score(content: str) -> dict:
        result = _extract_json(content)
        score = int(result.get("score", 0))
        result["score"] = max(0, min(100, score))
        tier = result.get("tier", "COLD").upper()
        if tier not in {"HOT", "WARM", "COLD", "DISQUALIFY"}:
            tier = _score_to_tier(result["score"])
        result["tier"] = tier
        return result

    # Try Groq first, fall back to Gemini on rate limit
    groq_exc = None
    try:
        response = _get_groq().chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SCORE_SYSTEM_PROMPT},
                {"role": "user", "content": research_summary},
            ],
            temperature=0.2,
            max_tokens=512,
        )
        return _parse_score(response.choices[0].message.content or "")
    except Exception as exc:
        groq_exc = exc
        logger.warning("score_lead Groq failed (%s) — falling back to Gemini.", exc)

    # Gemini fallback for scoring
    try:
        gemini = _get_gemini()
        prompt = SCORE_SYSTEM_PROMPT + "\n\n" + research_summary
        response = gemini.generate_content(prompt)
        result = _parse_score(response.text or "")
        logger.info("score_lead used Gemini fallback — score=%s tier=%s", result.get("score"), result.get("tier"))
        return result
    except Exception as gem_exc:
        logger.error("score_lead Gemini fallback also failed: %s", gem_exc)

    return {
        "score": 0,
        "tier": "DISQUALIFY",
        "reasoning": f"Scoring failed: Groq={groq_exc}",
        "key_talking_points": [],
        "risk_flags": ["Scoring error — manual review required"],
        "recommended_action": "manual review",
    }


def _score_to_tier(score: int) -> str:
    if score >= 80:
        return "HOT"
    if score >= 60:
        return "WARM"
    if score >= 40:
        return "COLD"
    return "DISQUALIFY"


# ---------------------------------------------------------------------------
# Email drafting
# ---------------------------------------------------------------------------

EMAIL_SYSTEM_PROMPT = """You are an expert B2B outreach copywriter.

Write a personalized outreach email for the lead based on the research findings provided.
The email MUST reference specific details discovered during research (not generic boilerplate).

RULES:
- Subject line: compelling, personalized, references something specific
- Opening: acknowledge something specific about their company (news, growth, expansion)
- Value pitch: 2-3 sentences max — connect their pain point to a solution
- CTA: one clear, low-friction ask (15-20 min call)
- Tone: professional, direct, human — not salesy
- Length: under 150 words for the body

Return ONLY a valid JSON object (no markdown, no extra text):
{
  "subject": "<email subject line>",
  "body": "<full email body with \\n for line breaks>",
  "key_personalization": ["<what you referenced>", "<why it's relevant>"]
}"""


def draft_email(
    lead_name: str,
    company: str,
    email: str,
    company_info: dict[str, Any],
    recent_activity: dict[str, Any],
    score_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Draft a personalized outreach email for a lead.

    Args:
        lead_name: Full name of the lead contact.
        company: Company name.
        email: Lead's email address.
        company_info: Output from search.search_company().
        recent_activity: Output from search.search_recent_activity().
        score_result: Output from score_lead().

    Returns:
        dict with: subject, body, key_personalization
    """
    context = (
        f"Lead: {lead_name} at {company} ({email})\n\n"
        f"Company Overview:\n{json.dumps(company_info, indent=2)}\n\n"
        f"Recent Activity:\n{json.dumps(recent_activity, indent=2)}\n\n"
        f"Score: {score_result.get('score')}/100 ({score_result.get('tier')})\n"
        f"Key Talking Points:\n"
        + "\n".join(f"- {p}" for p in score_result.get("key_talking_points", []))
    )

    try:
        gemini = _get_gemini()
        prompt = EMAIL_SYSTEM_PROMPT + "\n\n" + context
        response = gemini.generate_content(prompt)
        content = response.text or ""
        return _extract_json(content)

    except Exception as exc:
        logger.error("draft_email (Gemini) failed: %s. Falling back to Groq.", exc)
        # Fallback to Groq if Gemini fails
        try:
            response = _get_groq().chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": EMAIL_SYSTEM_PROMPT},
                    {"role": "user", "content": context},
                ],
                temperature=0.5,
                max_tokens=512,
            )
            content = response.choices[0].message.content or ""
            return _extract_json(content)
        except Exception as fallback_exc:
            logger.error("draft_email Groq fallback also failed: %s", fallback_exc)
        return {
            "subject": f"Quick question about {company}",
            "body": (
                f"Hi {lead_name.split()[0]},\n\n"
                f"I came across {company} and was impressed by what you're building.\n\n"
                "Would a 15-minute call this week make sense?\n\nBest,"
            ),
            "key_personalization": ["Fallback email — scoring context unavailable"],
        }


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import pprint
    import sys

    logging.basicConfig(level=logging.INFO)

    mock_company_info = {
        "company": "TechCorp PH",
        "description": "HR software for SMEs in Southeast Asia",
        "industry": "HR Tech",
        "size_signals": "50-100 employees",
        "website": "techcorph.com",
        "founded": "2021",
        "recent_news": ["Raised $2M seed round", "Expanding to Singapore"],
    }

    mock_activity = {
        "hiring": "3 open roles on LinkedIn (Sales, Marketing, Backend)",
        "news": ["TechCorp PH opens Singapore office — Jan 2026"],
        "social": "Active on LinkedIn, posting 2-3x/week",
        "funding": "Raised $2M seed round",
    }

    print("\n=== Scoring Lead ===")
    score = score_lead("Maria Santos", "TechCorp PH", mock_company_info, mock_activity)
    pprint.pprint(score)

    if score["tier"] not in ("DISQUALIFY",):
        print("\n=== Drafting Email ===")
        email_result = draft_email(
            "Maria Santos", "TechCorp PH", "maria@techcorph.com",
            mock_company_info, mock_activity, score,
        )
        pprint.pprint(email_result)
