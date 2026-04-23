"""
Supabase database client — lead logging.
Inserts the full lead qualification profile into the `leads` table.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

_client: Client | None = None


def _get_client() -> Client:
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise EnvironmentError("SUPABASE_URL and SUPABASE_KEY must be set.")
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


def log_lead(lead_profile: dict[str, Any]) -> dict[str, Any]:
    """
    Insert a complete lead qualification profile into the `leads` table.

    Args:
        lead_profile: Dict matching the leads table schema.

    Returns:
        dict with: success (bool), lead_id (str or None), error (str or None)
    """
    if not lead_profile:
        return {"success": False, "lead_id": None, "error": "Empty lead profile."}

    # Map to exact column names, with safe defaults
    row = {
        "lead_name":          _safe_str(lead_profile.get("lead_name"), 255),
        "company":            _safe_str(lead_profile.get("company"), 255),
        "email":              _safe_str(lead_profile.get("email"), 320),
        "source":             _safe_str(lead_profile.get("source"), 100),
        "service_interest":   _safe_str(lead_profile.get("service_interest"), 500),
        "company_size":       _safe_str(lead_profile.get("company_size"), 255),
        "industry":           _safe_str(lead_profile.get("industry"), 255),
        "description":        _safe_str(lead_profile.get("description"), 2000),
        "recent_news":        _safe_list(lead_profile.get("recent_news")),
        "hiring_signals":     _safe_str(lead_profile.get("hiring_signals"), 1000),
        "website":            _safe_str(lead_profile.get("website"), 500),
        "score":              _safe_int(lead_profile.get("score")),
        "tier":               _safe_tier(lead_profile.get("tier")),
        "score_reasoning":    _safe_str(lead_profile.get("score_reasoning"), 2000),
        "key_talking_points": _safe_list(lead_profile.get("key_talking_points")),
        "risk_flags":         _safe_list(lead_profile.get("risk_flags")),
        "recommended_action": _safe_str(lead_profile.get("recommended_action"), 255),
        "email_draft":        _safe_str(lead_profile.get("email_draft"), 5000),
        "email_subject":      _safe_str(lead_profile.get("email_subject"), 500),
        "status":             "new",
        "agent_steps":        _safe_int(lead_profile.get("agent_steps")),
        "region":             _safe_str(lead_profile.get("region"), 100),
        "email_status":       _safe_str(lead_profile.get("email_status"), 20),
    }

    # Remove None values — let Supabase use column defaults
    row = {k: v for k, v in row.items() if v is not None}

    try:
        client = _get_client()
        result = client.table("leads").insert(row).execute()

        if result.data:
            lead_id = result.data[0].get("id", "unknown")
            logger.info("Lead logged to Supabase. ID: %s", lead_id)
            return {"success": True, "lead_id": lead_id, "error": None}

        return {"success": False, "lead_id": None, "error": "Insert returned no data."}

    except Exception as exc:
        logger.error("Supabase insert failed: %s", exc)
        return {"success": False, "lead_id": None, "error": str(exc)}


def fetch_leads(limit: int = 50, offset: int = 0) -> dict:
    """
    Fetch paginated lead records from Supabase for the run history dashboard.

    Returns selected fields only — never the full email_draft body here.
    """
    try:
        client = _get_client()
        result = (
            client.table("leads")
            .select("*")
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return {"success": True, "leads": result.data or [], "error": None}
    except Exception as exc:
        logger.error("fetch_leads failed: %s", exc)
        return {"success": False, "leads": [], "error": str(exc)}


# ---------------------------------------------------------------------------
# Input sanitization helpers
# ---------------------------------------------------------------------------

def _safe_str(value: Any, max_len: int) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text[:max_len] if text else None


def _safe_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_tier(value: Any) -> str | None:
    valid = {"HOT", "WARM", "COLD", "DISQUALIFY"}
    if value and str(value).upper() in valid:
        return str(value).upper()
    return None


def _safe_list(value: Any) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, list):
        return [str(item)[:500] for item in value if item is not None][:20]
    return [str(value)[:500]]


if __name__ == "__main__":
    import pprint
    import logging as lg

    lg.basicConfig(level=lg.INFO)

    mock_profile = {
        "lead_name": "Maria Santos",
        "company": "TechCorp PH",
        "email": "maria@techcorph.com",
        "source": "cli_test",
        "company_size": "50-100 employees",
        "industry": "HR Tech",
        "description": "HR software for SMEs in Southeast Asia",
        "recent_news": ["Raised $2M seed round", "Expanding to Singapore"],
        "hiring_signals": "3 open roles on LinkedIn",
        "website": "techcorph.com",
        "score": 78,
        "tier": "WARM",
        "score_reasoning": "Growing company with active hiring and recent funding.",
        "key_talking_points": ["Singapore expansion timing", "Scaling ops without headcount"],
        "risk_flags": [],
        "recommended_action": "personalized email",
        "email_draft": "Hi Maria,\n\nCongrats on the Singapore expansion...",
        "email_subject": "Congrats on the Singapore expansion, Maria",
        "agent_steps": 6,
    }

    print("\n=== Logging lead to Supabase ===")
    pprint.pprint(log_lead(mock_profile))
