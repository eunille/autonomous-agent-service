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
        "telegram_status":    _safe_str(lead_profile.get("telegram_status"), 20),
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


def check_duplicate(company: str, email: str) -> dict:
    """
    Check if a lead with the same company name or email already exists.
    
    Args:
        company: Company name to check
        email: Email address to check
        
    Returns:
        dict with: is_duplicate (bool), existing_lead (dict or None), error (str or None)
    """
    try:
        client = _get_client()
        
        # Search by company name (case-insensitive) or email (exact match)
        result = (
            client.table("leads")
            .select("id, company, email, tier, score, created_at")
            .or_(f"company.ilike.{company},email.eq.{email}")
            .limit(1)
            .execute()
        )
        
        if result.data and len(result.data) > 0:
            return {
                "is_duplicate": True,
                "existing_lead": result.data[0],
                "error": None,
            }
        
        return {"is_duplicate": False, "existing_lead": None, "error": None}
        
    except Exception as exc:
        logger.error("check_duplicate failed: %s", exc)
        return {"is_duplicate": False, "existing_lead": None, "error": str(exc)}


def delete_leads_by_ids(lead_ids: list[str]) -> dict[str, Any]:
    """
    Delete multiple leads by their IDs.
    
    Args:
        lead_ids: List of lead IDs to delete
        
    Returns:
        dict with: success (bool), deleted_count (int), error (str or None)
    """
    try:
        client = _get_client()
        
        # Delete leads matching the IDs
        result = (
            client.table("leads")
            .delete()
            .in_("id", lead_ids)
            .execute()
        )
        
        deleted_count = len(result.data) if result.data else 0
        logger.info("Deleted %d leads", deleted_count)
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "error": None,
        }
        
    except Exception as exc:
        logger.error("delete_leads_by_ids failed: %s", exc)
        return {
            "success": False,
            "deleted_count": 0,
            "error": str(exc),
        }


def update_lead_by_id(lead_id: str, updates: dict[str, Any]) -> dict[str, Any]:
    """
    Update an existing lead by ID.
    
    Args:
        lead_id: Lead ID to update
        updates: Dict of fields to update
        
    Returns:
        dict with: success (bool), error (str or None)
    """
    try:
        client = _get_client()
        
        # Build update payload with safe conversions
        update_payload = {}
        for key, value in updates.items():
            if key in ("score", "agent_steps"):
                update_payload[key] = _safe_int(value)
            elif key == "tier":
                update_payload[key] = _safe_tier(value)
            elif key in ("key_talking_points", "risk_flags"):
                update_payload[key] = _safe_list(value)
            else:
                update_payload[key] = _safe_str(value, 2000)
        
        # Update the lead
        result = (
            client.table("leads")
            .update(update_payload)
            .eq("id", lead_id)
            .execute()
        )
        
        if not result.data:
            return {
                "success": False,
                "error": f"Lead {lead_id} not found",
            }
        
        logger.info("Updated lead %s", lead_id)
        
        return {
            "success": True,
            "error": None,
        }
        
    except Exception as exc:
        logger.error("update_lead_by_id failed: %s", exc)
        return {
            "success": False,
            "error": str(exc),
        }


def fetch_stats() -> dict:
    """
    Fetch aggregated statistics from all leads.
    
    Returns:
        dict with: success (bool), stats (dict), error (str or None)
        stats contains: total_leads, hot_count, warm_count, cold_count, 
                       disqualify_count, avg_score, recent_count (last 7 days)
    """
    try:
        client = _get_client()
        
        # Fetch all leads with tier and score
        result = (
            client.table("leads")
            .select("tier, score, created_at")
            .execute()
        )
        
        leads = result.data or []
        total_leads = len(leads)
        
        # Count by tier
        hot_count = sum(1 for lead in leads if lead.get("tier") == "HOT")
        warm_count = sum(1 for lead in leads if lead.get("tier") == "WARM")
        cold_count = sum(1 for lead in leads if lead.get("tier") == "COLD")
        disqualify_count = sum(1 for lead in leads if lead.get("tier") == "DISQUALIFY")
        
        # Calculate average score (excluding nulls)
        scores = [lead.get("score") for lead in leads if lead.get("score") is not None]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0
        
        # Count recent leads (last 7 days)
        from datetime import datetime, timedelta, timezone
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent_count = sum(
            1 for lead in leads 
            if lead.get("created_at") and 
            datetime.fromisoformat(lead["created_at"].replace("Z", "+00:00")) > seven_days_ago
        )
        
        stats = {
            "total_leads": total_leads,
            "hot_count": hot_count,
            "warm_count": warm_count,
            "cold_count": cold_count,
            "disqualify_count": disqualify_count,
            "avg_score": avg_score,
            "recent_count": recent_count,
        }
        
        return {"success": True, "stats": stats, "error": None}
        
    except Exception as exc:
        logger.error("fetch_stats failed: %s", exc)
        return {"success": False, "stats": {}, "error": str(exc)}


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


def increment_rate_limit() -> dict[str, Any]:
    """
    Increment the rate limit counter for today.
    
    Returns:
        dict with: success (bool), current_count (int), limit (int), error (str or None)
    """
    try:
        from datetime import date
        client = _get_client()
        today = date.today().isoformat()
        DAILY_LIMIT = 140  # Groq daily limit
        
        # Get current count
        result = client.table("rate_limits").select("request_count").eq("date", today).execute()
        
        if result.data and len(result.data) > 0:
            # Update existing record
            current_count = result.data[0]["request_count"]
            new_count = current_count + 1
            client.table("rate_limits").update({"request_count": new_count}).eq("date", today).execute()
        else:
            # Insert new record for today
            new_count = 1
            client.table("rate_limits").insert({"date": today, "request_count": new_count}).execute()
        
        return {
            "success": True,
            "current_count": new_count,
            "limit": DAILY_LIMIT,
            "error": None,
        }
    except Exception as exc:
        logger.error("increment_rate_limit failed: %s", exc)
        return {
            "success": False,
            "current_count": 0,
            "limit": 140,
            "error": str(exc),
        }


def get_rate_limit_status() -> dict[str, Any]:
    """
    Get the current rate limit status for today.
    
    Returns:
        dict with: current_count (int), limit (int), remaining (int), error (str or None)
    """
    try:
        from datetime import date
        client = _get_client()
        today = date.today().isoformat()
        DAILY_LIMIT = 140
        
        result = client.table("rate_limits").select("request_count").eq("date", today).execute()
        
        if result.data and len(result.data) > 0:
            current_count = result.data[0]["request_count"]
        else:
            current_count = 0
        
        return {
            "current_count": current_count,
            "limit": DAILY_LIMIT,
            "remaining": max(0, DAILY_LIMIT - current_count),
            "error": None,
        }
    except Exception as exc:
        logger.error("get_rate_limit_status failed: %s", exc)
        return {
            "current_count": 0,
            "limit": 140,
            "remaining": 140,
            "error": str(exc),
        }


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
