"""
Serper API wrapper for company research.
Handles web search for company info and recent activity.
"""

import os
import re
import json
import logging
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
SERPER_ENDPOINT = "https://google.serper.dev/search"
REQUEST_TIMEOUT = 10  # seconds


def _sanitize_query(query: str) -> str:
    """Strip control characters and limit query length."""
    sanitized = re.sub(r"[\x00-\x1f\x7f]", "", query)
    return sanitized[:200].strip()


def _build_headers() -> dict:
    if not SERPER_API_KEY:
        raise EnvironmentError("SERPER_API_KEY is not set.")
    return {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json",
    }


def _serper_search(query: str, num_results: int = 5) -> dict:
    """Execute a Serper search and return raw results."""
    sanitized = _sanitize_query(query)
    payload = {"q": sanitized, "num": num_results}
    try:
        response = requests.post(
            SERPER_ENDPOINT,
            headers=_build_headers(),
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.error("Serper request timed out for query: %s", sanitized)
        return {}
    except requests.exceptions.HTTPError as exc:
        logger.error("Serper HTTP error %s for query: %s", exc.response.status_code, sanitized)
        return {}
    except requests.exceptions.RequestException as exc:
        logger.error("Serper request failed: %s", exc)
        return {}


def _extract_organic(raw: dict) -> list[dict]:
    """Pull the organic results from a Serper response."""
    return raw.get("organic", [])


def search_company(company_name: str) -> dict:
    """
    Search for general company information.

    Returns a structured dict with:
      - company, description, industry, size_signals,
        website, founded, recent_news (list)
    """
    query = f"{company_name} company overview employees industry"
    raw = _serper_search(query, num_results=5)
    organic = _extract_organic(raw)

    description = ""
    website = ""
    snippets: list[str] = []

    for result in organic:
        snippet = result.get("snippet", "")
        link = result.get("link", "")
        if snippet:
            snippets.append(snippet)
        if not website and link and company_name.lower().replace(" ", "") in link.replace("-", "").lower():
            website = link

    description = snippets[0] if snippets else "No description found."
    recent_news = snippets[1:4] if len(snippets) > 1 else []

    # Rough size signal from snippets
    size_signal = "Unknown"
    combined = " ".join(snippets).lower()
    for marker in ["10,000", "5,000", "1,000", "500", "200", "100", "50"]:
        if marker in combined or f"{marker} employees" in combined:
            size_signal = f"~{marker} employees (from search)"
            break

    return {
        "company": company_name,
        "description": description,
        "industry": _infer_industry(combined),
        "size_signals": size_signal,
        "website": website,
        "founded": _infer_founded(combined),
        "recent_news": recent_news,
    }


def search_recent_activity(company_name: str) -> dict:
    """
    Search for recent company news, hiring, and funding signals.

    Returns a structured dict with:
      - hiring, news (list), social, funding
    """
    query = f"{company_name} hiring jobs funding news 2025 2026"
    raw = _serper_search(query, num_results=5)
    organic = _extract_organic(raw)

    snippets = [r.get("snippet", "") for r in organic if r.get("snippet")]
    combined = " ".join(snippets).lower()

    hiring_signal = "No hiring activity found."
    for keyword in ["open roles", "job opening", "hiring", "new position", "we're hiring"]:
        if keyword in combined:
            hiring_signal = f"Active hiring detected ({keyword} mentioned in results)."
            break

    funding_signal = "No funding news found."
    for keyword in ["raised", "series a", "series b", "seed round", "funding", "million", "valuation"]:
        if keyword in combined:
            funding_signal = f"Funding activity detected ({keyword} mentioned)."
            break

    return {
        "hiring": hiring_signal,
        "news": snippets[:3],
        "social": _infer_social_activity(combined),
        "funding": funding_signal,
    }


def _infer_industry(text: str) -> str:
    """Heuristic industry detection from search snippet text."""
    industry_keywords = {
        "SaaS": ["saas", "software as a service", "cloud platform"],
        "FinTech": ["fintech", "payments", "banking", "financial technology"],
        "HR Tech": ["hr tech", "human resources", "workforce", "payroll", "recruitment"],
        "E-commerce": ["ecommerce", "e-commerce", "online store", "marketplace"],
        "HealthTech": ["health tech", "healthcare", "medtech", "telemedicine"],
        "EdTech": ["edtech", "education", "learning platform", "lms"],
        "PropTech": ["proptech", "real estate", "property management"],
        "Logistics": ["logistics", "supply chain", "delivery", "fleet"],
        "Cybersecurity": ["cybersecurity", "security platform", "threat detection"],
        "AI / ML": ["artificial intelligence", "machine learning", "ai-powered", " llm"],
    }
    for industry, keywords in industry_keywords.items():
        if any(kw in text for kw in keywords):
            return industry
    return "Technology"


def _infer_founded(text: str) -> str:
    """Extract founding year from snippet text if present."""
    match = re.search(r"founded\s+in\s+(\d{4})", text)
    if match:
        return match.group(1)
    match = re.search(r"since\s+(\d{4})", text)
    if match:
        return match.group(1)
    return "Unknown"


def _infer_social_activity(text: str) -> str:
    for marker in ["linkedin", "twitter", "social media", "active online"]:
        if marker in text:
            return "Active on social media (LinkedIn/Twitter mentioned)."
    return "Social activity not detected in search results."


if __name__ == "__main__":
    import sys
    import pprint

    logging.basicConfig(level=logging.INFO)

    company = sys.argv[1] if len(sys.argv) > 1 else "Grab Philippines"
    print(f"\n=== Company Info: {company} ===")
    pprint.pprint(search_company(company))

    print(f"\n=== Recent Activity: {company} ===")
    pprint.pprint(search_recent_activity(company))
