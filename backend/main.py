"""
Entry point — CLI + FastAPI HTTP endpoint.
Accepts a lead and triggers the full autonomous qualification agent.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Security, status
from fastapi.responses import StreamingResponse
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, field_validator
from dotenv import load_dotenv

from agent import run_agent
from database import fetch_leads

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
    region: str = Field(default="Philippines", max_length=100, description="Company region or country for search scoping.")

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


@app.get("/leads")
def list_leads(
    limit: int = 50,
    offset: int = 0,
    _: str = Depends(require_api_key),
) -> dict:
    """
    Fetch paginated lead run history from Supabase.

    Requires X-API-Key header.
    """
    if limit < 1 or limit > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="limit must be between 1 and 200.",
        )
    if offset < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="offset must be non-negative.",
        )
    result = fetch_leads(limit=limit, offset=offset)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to fetch leads."),
        )
    return {"leads": result["leads"], "limit": limit, "offset": offset}


# ---------------------------------------------------------------------------
# Batch qualification — Server-Sent Events stream
# ---------------------------------------------------------------------------

MAX_BATCH_LEADS = 10
BATCH_LEAD_DELAY_SECONDS = 2


class BatchLeadItem(BaseModel):
    lead_name: str = Field(..., min_length=1, max_length=255)
    company: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., max_length=320)
    source: str = Field(default="batch", max_length=100)
    service_interest: str | None = Field(default=None, max_length=500)
    region: str = Field(default="Philippines", max_length=100)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not EMAIL_PATTERN.match(v):
            raise ValueError("Invalid email format.")
        return v

    @field_validator("lead_name", "company", "source")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class BatchRequest(BaseModel):
    leads: list[BatchLeadItem] = Field(..., min_length=1)


def _sse_event(data: dict) -> str:
    """Format a dict as an SSE data event."""
    return f"data: {json.dumps(data)}\n\n"


@app.post("/qualify-batch")
def qualify_batch(
    batch: BatchRequest,
    request: Request,
    _: str = Depends(require_api_key),
) -> StreamingResponse:
    """
    Qualify a batch of leads with real-time Server-Sent Events progress streaming.

    Emits one event per pipeline step. Max 10 leads per batch.
    Requires X-API-Key header.
    """
    if len(batch.leads) > MAX_BATCH_LEADS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batch exceeds maximum of {MAX_BATCH_LEADS} leads.",
        )

    async def event_stream():
        yield _sse_event({"type": "batch_start", "total": len(batch.leads)})

        for i, lead_item in enumerate(batch.leads):
            yield _sse_event({
                "type": "lead_start",
                "index": i,
                "lead_name": lead_item.lead_name,
                "company": lead_item.company,
            })

            step_events: list[str] = []

            def on_step(step: str, company: str = lead_item.company, idx: int = i) -> None:
                step_events.append(step)

            try:
                # Yield step events synchronously — generator runs in thread context
                # We flush via a thread trick: collect steps and yield between leads
                import threading

                result_holder: list = []
                error_holder: list = []

                def _run() -> None:
                    try:
                        run = run_agent(
                            lead_name=lead_item.lead_name,
                            company=lead_item.company,
                            email=lead_item.email,
                            source=lead_item.source,
                            service_interest=lead_item.service_interest,
                            region=lead_item.region,
                            on_step=on_step,
                        )
                        result_holder.append(run)
                    except Exception as exc:
                        error_holder.append(exc)

                t = threading.Thread(target=_run, daemon=True)
                t.start()

                # Poll for step events and stream them while the thread runs
                last_sent = 0
                while t.is_alive():
                    if len(step_events) > last_sent:
                        for step in step_events[last_sent:]:
                            yield _sse_event({
                                "type": "step",
                                "index": i,
                                "company": lead_item.company,
                                "step": step,
                            })
                        last_sent = len(step_events)
                    import asyncio
                    await asyncio.sleep(0.1)

                # Drain any remaining steps
                for step in step_events[last_sent:]:
                    yield _sse_event({
                        "type": "step",
                        "index": i,
                        "company": lead_item.company,
                        "step": step,
                    })

                if error_holder:
                    yield _sse_event({
                        "type": "lead_error",
                        "index": i,
                        "company": lead_item.company,
                        "error": str(error_holder[0]),
                    })
                else:
                    run = result_holder[0]
                    score_result = run.tool_results.get("score_lead", {})
                    supabase_result = run.tool_results.get("log_to_supabase", {})
                    email_draft_result = run.tool_results.get("draft_outreach_email", {})
                    yield _sse_event({
                        "type": "lead_done",
                        "index": i,
                        "lead_name": lead_item.lead_name,
                        "company": lead_item.company,
                        "score": score_result.get("score"),
                        "tier": score_result.get("tier"),
                        "reasoning": score_result.get("reasoning", ""),
                        "recommended_action": score_result.get("recommended_action", ""),
                        "email_subject": email_draft_result.get("subject", ""),
                        "email_body": email_draft_result.get("body", ""),
                        "lead_id": supabase_result.get("lead_id"),
                        "agent_steps": run.steps,
                        "error": run.error or None,
                    })

            except Exception as exc:
                logger.error("Batch item %d (%s) failed: %s", i, lead_item.company, exc)
                yield _sse_event({
                    "type": "lead_error",
                    "index": i,
                    "company": lead_item.company,
                    "error": str(exc),
                })

            # Delay between leads to respect Groq rate limits (30 RPM)
            if i < len(batch.leads) - 1:
                time.sleep(BATCH_LEAD_DELAY_SECONDS)

        yield _sse_event({"type": "batch_done", "total": len(batch.leads)})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable Nginx buffering on Render
        },
    )


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
            region=lead.region,
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
