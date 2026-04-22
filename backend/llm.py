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

SCORE_SYSTEM_PROMPT = """You are a senior B2B sales qualification specialist. You qualify leads for an AI sales automation agency (AutoSystems) that sells to businesses with 10–500 employees.

Analyze the research data and score the lead 0–100. Award points generously when signals are present. CRITICAL RULE: If data for a criterion is unavailable, award the NEUTRAL midpoint for that criterion — never penalize for missing data.

SCORING RUBRIC (total = 100 points):

1. COMPANY SIZE FIT — 25 pts
   - 25 pts: 10–200 employees (ideal — small enough to move fast, big enough to have budget)
   - 18 pts: 200–500 employees (still a good fit)
   - 10 pts: <10 or 500–1000 employees (stretch, possible)
   - 0 pts: >1000 employees (enterprise, not a fit)
   - Unknown size → award 15 pts (neutral)

2. BUSINESS AUTOMATION NEED — 25 pts
   Assess whether this company likely has pain points that AI sales automation solves (manual lead handling, repetitive outreach, high sales volume, growing sales team).
   - 25 pts: Strong fit — sales-driven, SME, high transaction volume, growing team
   - 18 pts: Good fit — moderate sales operations, some manual processes
   - 10 pts: Weak fit — early-stage or very niche
   - 0 pts: No fit — fully automated already or no sales function
   - Unknown → award 15 pts (neutral)

3. GROWTH SIGNALS — 25 pts
   Any ONE of these signals = strong growth. Multiple = maximum.
   - 25 pts: Recently funded (any round) OR actively hiring sales/marketing roles OR announced expansion
   - 18 pts: Product launches, press coverage, new partnerships
   - 10 pts: Some online activity but no clear growth signals
   - 0 pts: Stagnant, declining, or negative signals
   - No signals found → award 12 pts (neutral — absence of data ≠ absence of growth)

4. RED FLAG CHECK — 25 pts
   - 25 pts: No red flags found (layoffs, lawsuits, bad press, shutdown rumors)
   - 15 pts: Minor concerns (old negative press, small controversy)
   - 0 pts: Major red flags (recent mass layoffs, legal action, fraud allegations)
   - No information → award 20 pts (neutral — assume clean)

TIERS:
- 80–100: HOT — strong fit across all criteria, immediate personal outreach
- 60–79:  WARM — good fit, personalized email campaign
- 40–59:  COLD — possible fit, add to nurture sequence
- 0–39:   DISQUALIFY — not a fit for AutoSystems

Return ONLY a valid JSON object (no markdown, no extra text):
{
  "score": <integer 0-100>,
  "tier": "<HOT|WARM|COLD|DISQUALIFY>",
  "reasoning": "<2-3 sentence explanation of the score>",
  "key_talking_points": ["<specific point 1>", "<specific point 2>", "<specific point 3>"],
  "risk_flags": ["<flag>"] or [],
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
