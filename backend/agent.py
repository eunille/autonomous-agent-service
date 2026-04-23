"""
Agent core — Direct sequential pipeline.

Industry-standard pattern: deterministic tool sequence called directly in Python.
Only the LLM-required steps (scoring, email drafting) use API calls.
This saves ~70% tokens vs a ReAct loop for a fixed-order workflow.

Pipeline: search_company → search_recent_activity → score_lead
          → draft_outreach_email (if score ≥ 40) → log_to_supabase
          → send_telegram_alert → [HOT] send_email → [HOT] send_telegram_alert
"""

from __future__ import annotations

import concurrent.futures
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Callable

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class AgentRun:
    """Tracks the state of a single agent qualification run."""

    lead_name: str
    company: str
    email: str
    source: str = "unknown"
    service_interest: str | None = None
    region: str = "Philippines"

    steps: int = 0
    tool_results: dict[str, Any] = field(default_factory=dict)
    messages: list[dict] = field(default_factory=list)  # kept for API compatibility
    final_summary: str = ""
    error: str = ""


def run_agent(
    lead_name: str,
    company: str,
    email: str,
    source: str = "unknown",
    service_interest: str | None = None,
    region: str = "Philippines",
    on_step: Callable[[str], None] | None = None,
) -> AgentRun:
    """
    Run the full lead qualification pipeline — direct sequential execution.

    Args:
        on_step: Optional callback called with a status string at each pipeline step.
                 Used by the batch SSE endpoint to stream progress to the client.
      1. search_company + search_recent_activity  (parallel)
      2. score_lead                               (Groq LLM, Gemini fallback)
      3. draft_outreach_email                     (Gemini, only if score >= 40)
      4. log_to_supabase                          (persist all results)
      5. send_telegram_alert                      (standard qualification summary)
      6. send_email (HOT only)                    (Gmail SMTP auto-send)
      7. send_telegram_alert (HOT only)           (urgent HOT alert with email status)
    """
    from search import search_company, search_recent_activity
    from llm import score_lead, draft_email
    from database import log_lead
    from notifier import send_alert

    run = AgentRun(
        lead_name=lead_name,
        company=company,
        email=email,
        source=source,
        service_interest=service_interest,
        region=region,
    )

    # ── Step 1: Parallel web research ─────────────────────────────────────
    logger.info("Pipeline starting for lead: %s @ %s", lead_name, company)
    if on_step:
        on_step("researching")
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            f_company = executor.submit(search_company, company, run.region)
            f_activity = executor.submit(search_recent_activity, company, run.region)
            company_info = f_company.result(timeout=30)
            recent_activity = f_activity.result(timeout=30)
    except Exception as exc:
        logger.warning("Research step failed: %s — using empty results", exc)
        company_info = {}
        recent_activity = {}

    run.tool_results["search_company"] = company_info
    run.tool_results["search_recent_activity"] = recent_activity
    run.steps += 2
    logger.info("Research complete — company=%s, activity=%s",
                bool(company_info), bool(recent_activity))

    # ── Step 2: Score lead ────────────────────────────────────────────────
    if on_step:
        on_step("scoring")
    try:
        score_result = score_lead(
            lead_name=lead_name,
            company=company,
            company_info=company_info,
            recent_activity=recent_activity,
        )
    except Exception as exc:
        logger.error("score_lead failed: %s", exc)
        score_result = {
            "score": 50,
            "tier": "WARM",
            "reasoning": "Scoring unavailable — defaulting to WARM.",
            "key_talking_points": [],
            "risk_flags": [],
            "recommended_action": "manual review",
        }
        run.error = str(exc)

    run.tool_results["score_lead"] = score_result
    run.steps += 1
    tier = score_result.get("tier", "UNKNOWN")
    score = score_result.get("score", 0)
    logger.info("Lead scored: %s/100 — %s", score, tier)

    # ── Step 3: Draft outreach email (score >= 40 only) ───────────────────
    email_result: dict[str, Any] = {}
    if score >= 40:
        if on_step:
            on_step("drafting_email")
        try:
            email_result = draft_email(
                lead_name=lead_name,
                company=company,
                email=email,
                company_info=company_info,
                recent_activity=recent_activity,
                score_result=score_result,
            )
        except Exception as exc:
            logger.error("draft_email failed: %s", exc)
            email_result = {
                "subject": f"Quick question about {company}",
                "body": (
                    f"Hi {lead_name.split()[0]},\n\n"
                    f"I came across {company} and was impressed by what you're building.\n\n"
                    "Would a 15-minute call this week make sense?\n\nBest,"
                ),
                "key_personalization": [],
            }
        run.steps += 1

    run.tool_results["draft_outreach_email"] = email_result

    # ── Step 4: Log to Supabase ───────────────────────────────────────────
    lead_id = None
    if on_step:
        on_step("logging")
    try:
        lead_profile = _build_lead_profile(run)
        log_result = log_lead(lead_profile)
        run.tool_results["log_to_supabase"] = log_result
        lead_id = log_result.get("id")
        run.steps += 1
        logger.info("Logged to Supabase — id=%s", lead_id)
    except Exception as exc:
        logger.error("log_to_supabase failed: %s", exc)
        run.tool_results["log_to_supabase"] = {"error": str(exc)}

    # ── Step 5: Send Telegram alert (standard) ────────────────────────────
    try:
        telegram_summary = _build_telegram_summary(run)
        send_alert(telegram_summary)
        run.tool_results["send_telegram_alert"] = {"success": True}
        run.steps += 1
        logger.info("Telegram alert sent")
    except Exception as exc:
        logger.error("send_telegram_alert failed: %s", exc)
        run.tool_results["send_telegram_alert"] = {"error": str(exc)}

    # ── Step 6+7: HOT lead — auto-send email + urgent Telegram ───────────
    if tier == "HOT" and email_result.get("subject") and email_result.get("body"):
        from emailer import send_email as smtp_send
        try:
            send_result = smtp_send(
                to_email=email,
                subject=email_result["subject"],
                body=email_result["body"],
                lead_name=lead_name,
                company=company,
            )
            run.tool_results["send_email"] = send_result
            run.steps += 1
            if send_result.get("success"):
                logger.info("HOT lead — email auto-sent to %s", email)
                # Urgent HOT Telegram with email_sent=True
                send_alert({**_build_telegram_summary(run), "email_sent": True})
            else:
                logger.warning("HOT email failed: %s", send_result.get("error"))
                send_alert({**_build_telegram_summary(run), "email_sent": False})
        except Exception as exc:
            logger.error("HOT email send failed: %s", exc)

    run.final_summary = (
        f"Lead qualified: {lead_name} @ {company} — "
        f"Score {score}/100 ({tier}). "
        f"{run.steps} steps completed."
    )
    if on_step:
        on_step("done")
    logger.info(run.final_summary)
    return run


def _build_lead_profile(run: AgentRun) -> dict:
    """Build the full lead profile dict for Supabase logging."""
    company_info = run.tool_results.get("search_company", {})
    recent_activity = run.tool_results.get("search_recent_activity", {})
    score_result = run.tool_results.get("score_lead", {})
    email_result = run.tool_results.get("draft_outreach_email", {})

    return {
        "lead_name": run.lead_name,
        "company": run.company,
        "email": run.email,
        "source": run.source,
        "service_interest": run.service_interest or "",
        "company_size": company_info.get("size_signals", ""),
        "industry": company_info.get("industry", ""),
        "description": company_info.get("description", ""),
        "recent_news": company_info.get("recent_news", []),
        "hiring_signals": recent_activity.get("hiring", ""),
        "website": company_info.get("website", ""),
        "score": score_result.get("score"),
        "tier": score_result.get("tier"),
        "score_reasoning": score_result.get("reasoning", ""),
        "key_talking_points": score_result.get("key_talking_points", []),
        "risk_flags": score_result.get("risk_flags", []),
        "recommended_action": score_result.get("recommended_action", ""),
        "email_draft": email_result.get("body", ""),
        "email_subject": email_result.get("subject", ""),
        "status": "new",
        "agent_steps": run.steps,
        "region": run.region,
    }


def _build_telegram_summary(run: AgentRun) -> dict:
    """Build the summary dict for the Telegram alert."""
    score_result = run.tool_results.get("score_lead", {})
    company_info = run.tool_results.get("search_company", {})
    recent_activity = run.tool_results.get("search_recent_activity", {})

    key_findings = [
        company_info.get("description", ""),
        company_info.get("size_signals", ""),
        recent_activity.get("hiring", ""),
        recent_activity.get("funding", ""),
    ]
    key_findings = [f for f in key_findings if f and f != "Unknown"]

    return {
        "lead_name": run.lead_name,
        "company": run.company,
        "email": run.email,
        "score": score_result.get("score", 0),
        "tier": score_result.get("tier", "UNKNOWN"),
        "key_findings": key_findings[:4],
        "talking_points": score_result.get("key_talking_points", []),
        "recommended_action": score_result.get("recommended_action", "manual review"),
        "email_sent": bool(run.tool_results.get("send_email", {}).get("success")),
    }


if __name__ == "__main__":
    import sys
    import pprint

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    name = sys.argv[1] if len(sys.argv) > 1 else "Maria Santos"
    company = sys.argv[2] if len(sys.argv) > 2 else "TechCorp PH"
    email = sys.argv[3] if len(sys.argv) > 3 else "maria@techcorph.com"

    print(f"\n🤖 Running agent for: {name} @ {company}")
    result = run_agent(name, company, email, source="cli_test")

    print(f"\n✅ Completed in {result.steps} steps")
    print(f"Summary:\n{result.final_summary}")
    if result.error:
        print(f"\n❌ Error: {result.error}")
    if "score_lead" in result.tool_results:
        score = result.tool_results["score_lead"]
        print(f"\nScore: {score.get('score')}/100 — {score.get('tier')}")
        print(f"Reasoning: {score.get('reasoning')}")
