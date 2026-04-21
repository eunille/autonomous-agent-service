"""
Entry point — CLI + FastAPI HTTP endpoint.
Accepts a lead and triggers the full autonomous qualification agent.
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, field_validator
from dotenv import load_dotenv

from agent import run_agent

load_dotenv()

logger = logging.getLogger(__name__)

API_SECRET_KEY = os.getenv("API_SECRET_KEY", "")
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Autonomous Lead Qualification Agent",
    description="AI agent that researches, scores, and logs leads with zero human input.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------

def require_api_key(api_key: str | None = Security(API_KEY_HEADER)) -> str:
    if not API_SECRET_KEY:
        raise RuntimeError("API_SECRET_KEY env var is not set.")
    if not api_key or api_key != API_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key. Send X-API-Key header.",
        )
    return api_key


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


class LeadRequest(BaseModel):
    lead_name: str = Field(..., min_length=1, max_length=255, description="Full name of the lead contact.")
    company: str = Field(..., min_length=1, max_length=255, description="Company name.")
    email: str = Field(..., description="Lead's email address.")
    source: str = Field(default="api", max_length=100, description="Traffic source (optional).")
    service_interest: str | None = Field(default=None, max_length=500, description="Which service(s) the lead is interested in.")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not EMAIL_PATTERN.match(v):
            raise ValueError("Invalid email format.")
        if len(v) > 320:
            raise ValueError("Email exceeds maximum length.")
        return v

    @field_validator("lead_name", "company", "source")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()

    @field_validator("service_interest", mode="before")
    @classmethod
    def strip_optional(cls, v: str | None) -> str | None:
        return v.strip() if isinstance(v, str) else v


class LeadResponse(BaseModel):
    success: bool
    lead_name: str
    company: str
    score: int | None = None
    tier: str | None = None
    agent_steps: int
    lead_id: str | None = None
    telegram_sent: bool = False
    email_sent: bool = False
    summary: str
    error: str | None = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": "lead-qualification-agent"}


@app.post("/qualify-lead", response_model=LeadResponse)
def qualify_lead(
    lead: LeadRequest,
    _: str = Depends(require_api_key),
) -> LeadResponse:
    """
    Trigger the autonomous lead qualification agent.

    Requires X-API-Key header matching API_SECRET_KEY env var.
    """
    logger.info("Received lead: %s @ %s (source: %s)", lead.lead_name, lead.company, lead.source)

    try:
        run = run_agent(
            lead_name=lead.lead_name,
            company=lead.company,
            email=lead.email,
            source=lead.source,
            service_interest=lead.service_interest,
        )
    except Exception as exc:
        logger.error("Agent run failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent failed to run: {exc}",
        )

    score_result = run.tool_results.get("score_lead", {})
    supabase_result = run.tool_results.get("log_to_supabase", {})
    telegram_result = run.tool_results.get("send_telegram_alert", {})
    email_result = run.tool_results.get("send_email", {})

    return LeadResponse(
        success=not bool(run.error),
        lead_name=run.lead_name,
        company=run.company,
        score=score_result.get("score"),
        tier=score_result.get("tier"),
        agent_steps=run.steps,
        lead_id=supabase_result.get("lead_id"),
        telegram_sent=bool(telegram_result.get("success")),
        email_sent=bool(email_result.get("success")),
        summary=run.final_summary or "Agent completed.",
        error=run.error or None,
    )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Autonomous Lead Qualification Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python main.py --name 'Maria Santos' --company 'TechCorp PH' --email 'maria@techcorph.com'\n"
            "  python main.py --serve   # Start the FastAPI server\n"
        ),
    )
    parser.add_argument("--name", help="Lead full name")
    parser.add_argument("--company", help="Company name")
    parser.add_argument("--email", help="Lead email address")
    parser.add_argument("--source", default="cli", help="Lead source (default: cli)")
    parser.add_argument("--serve", action="store_true", help="Start the FastAPI HTTP server")
    parser.add_argument("--port", type=int, default=8000, help="Port for HTTP server (default: 8000)")
    return parser.parse_args()


def _run_cli(args: argparse.Namespace) -> None:
    """Run the agent from the command line."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if not all([args.name, args.company, args.email]):
        print("Error: --name, --company, and --email are required for CLI mode.")
        print("Use --serve to start the HTTP server instead.")
        sys.exit(1)

    # Basic email validation for CLI
    if not EMAIL_PATTERN.match(args.email.strip().lower()):
        print(f"Error: '{args.email}' is not a valid email address.")
        sys.exit(1)

    print(f"\n🤖 Starting agent for: {args.name} @ {args.company}")
    print("━" * 40)

    run = run_agent(
        lead_name=args.name.strip(),
        company=args.company.strip(),
        email=args.email.strip().lower(),
        source=args.source,
    )

    score_result = run.tool_results.get("score_lead", {})
    supabase_result = run.tool_results.get("log_to_supabase", {})
    telegram_result = run.tool_results.get("send_telegram_alert", {})

    print(f"\n✅ Completed in {run.steps} agent steps")
    print(f"Score:  {score_result.get('score', 'N/A')}/100 — {score_result.get('tier', 'N/A')}")
    print(f"Action: {score_result.get('recommended_action', 'N/A')}")
    print(f"Logged: {'✅' if supabase_result.get('success') else '❌'} (ID: {supabase_result.get('lead_id', 'N/A')})")
    print(f"Alert:  {'✅ Telegram sent' if telegram_result.get('success') else '❌ Telegram failed'}")

    if run.error:
        print(f"\n⚠️  Agent error: {run.error}")

    print(f"\nSummary:\n{run.final_summary}")


if __name__ == "__main__":
    args = _parse_args()

    if args.serve:
        logging.basicConfig(level=logging.INFO)
        uvicorn.run("main:app", host="0.0.0.0", port=args.port, reload=False)
    else:
        _run_cli(args)
