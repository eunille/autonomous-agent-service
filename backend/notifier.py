"""
Telegram notification sender — real-time lead alerts.
Sends a formatted message to the analyst when a lead is qualified.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_API_BASE = "https://api.telegram.org"
REQUEST_TIMEOUT = 10


TIER_EMOJI = {
    "HOT": "🔥",
    "WARM": "✅",
    "COLD": "❄️",
    "DISQUALIFY": "⛔",
}


def send_alert(lead_summary: dict[str, Any]) -> dict[str, Any]:
    """
    Send a Telegram alert with the lead qualification summary.

    Args:
        lead_summary: Dict with lead_name, company, email, score, tier,
                      key_findings (list), talking_points (list), recommended_action.

    Returns:
        dict with: success (bool), message_id (int or None), error (str or None)
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set.")
        return {"success": False, "message_id": None, "error": "Telegram credentials not configured."}

    message = _format_message(lead_summary)

    url = f"{TELEGRAM_API_BASE}/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        if data.get("ok"):
            message_id = data["result"]["message_id"]
            logger.info("Telegram alert sent. Message ID: %s", message_id)
            return {"success": True, "message_id": message_id, "error": None}

        error = data.get("description", "Unknown Telegram API error.")
        logger.error("Telegram API returned error: %s", error)
        return {"success": False, "message_id": None, "error": error}

    except requests.exceptions.Timeout:
        logger.error("Telegram request timed out.")
        return {"success": False, "message_id": None, "error": "Request timed out."}
    except requests.exceptions.HTTPError as exc:
        logger.error("Telegram HTTP error: %s", exc)
        return {"success": False, "message_id": None, "error": str(exc)}
    except requests.exceptions.RequestException as exc:
        logger.error("Telegram request failed: %s", exc)
        return {"success": False, "message_id": None, "error": str(exc)}


def _format_message(summary: dict[str, Any]) -> str:
    """Build the formatted Telegram message string. HOT leads get a distinct urgent template."""
    score = summary.get("score", 0)
    tier = str(summary.get("tier", "UNKNOWN")).upper()

    lead_name = summary.get("lead_name", "Unknown")
    company = summary.get("company", "Unknown")
    email = summary.get("email", "N/A")
    recommended = summary.get("recommended_action", "Review manually")
    email_sent = summary.get("email_sent", False)

    findings = summary.get("key_findings", [])
    findings_block = "\n".join(f"• {f}" for f in findings[:4]) if findings else "• No findings"

    talking_points = summary.get("talking_points", [])
    points_block = "\n".join(f"• {p}" for p in talking_points[:3]) if talking_points else "• No talking points"

    if tier == "HOT":
        email_line = (
            f"\n🚀 <b>Outreach email auto-sent</b> to {_esc(email)}"
            if email_sent
            else f"\n📧 Email draft ready — send manually to {_esc(email)}"
        )
        return (
            f"🔥🔥 <b>HOT LEAD — ACT NOW</b> 🔥🔥\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>{_esc(lead_name)}</b> @ <b>{_esc(company)}</b>\n"
            f"📬 {_esc(email)}\n\n"
            f"🎯 <b>Score: {score}/100 — HOT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Why they're HOT:</b>\n{findings_block}\n\n"
            f"<b>Use these talking points:</b>\n{points_block}\n\n"
            f"<b>Next step:</b> {_esc(recommended)}"
            f"{email_line}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ <i>Leads go cold in 5 minutes — call now.</i>"
        )

    # Standard template for WARM / COLD / DISQUALIFY
    emoji = TIER_EMOJI.get(tier, "📋")
    return (
        f"🎯 <b>NEW LEAD QUALIFIED</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Lead:</b> {_esc(lead_name)}\n"
        f"<b>Company:</b> {_esc(company)}\n"
        f"<b>Email:</b> {_esc(email)}\n\n"
        f"<b>Score:</b> {score}/100 {emoji} <b>{tier}</b>\n\n"
        f"<b>Key findings:</b>\n{findings_block}\n\n"
        f"<b>Talking points:</b>\n{points_block}\n\n"
        f"<b>Recommended:</b> {_esc(recommended)}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )


def _esc(text: str) -> str:
    """Escape HTML special characters for Telegram HTML parse mode."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


if __name__ == "__main__":
    import pprint
    import logging as lg

    lg.basicConfig(level=lg.INFO)

    mock_summary = {
        "lead_name": "Maria Santos",
        "company": "TechCorp PH",
        "email": "maria@techcorph.com",
        "score": 78,
        "tier": "WARM",
        "key_findings": [
            "50-person SaaS startup in HR Tech",
            "Raised $2M seed, expanding to Singapore",
            "3 open roles on LinkedIn (active growth)",
            "Founded 2021 — right growth stage",
        ],
        "talking_points": [
            "Singapore expansion timing",
            "Scaling ops without headcount growth",
        ],
        "recommended_action": "Personalized email → follow up in 3 days",
    }

    print("\n=== Sending Telegram alert ===")
    pprint.pprint(send_alert(mock_summary))
