"""
Tool definitions for the Groq function-calling agent.
Each tool has:
  - schema: OpenAI/Groq-compatible function definition (JSON Schema)
  - handler: callable that executes the tool and returns a result dict
"""

from __future__ import annotations

from typing import Any

# Tools are imported lazily inside handlers to avoid circular imports
# and to allow independent unit testing of this module.

# ---------------------------------------------------------------------------
# Tool schemas (Groq / OpenAI function calling format)
# ---------------------------------------------------------------------------

TOOL_SCHEMAS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "search_company",
            "description": (
                "Search the web for general information about a company including "
                "its size, industry, description, website, founding year, and recent news. "
                "Call this first for any lead to build a baseline research profile."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "The full name of the company to research.",
                    }
                },
                "required": ["company_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_recent_activity",
            "description": (
                "Search for recent activity signals for a company: hiring activity, "
                "funding rounds, product launches, and press coverage from the past 12 months. "
                "Call this to assess growth momentum and buying intent signals."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "The full name of the company to check for recent activity.",
                    }
                },
                "required": ["company_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "score_lead",
            "description": (
                "Score a lead 0-100 using AI reasoning based on all research collected so far. "
                "Returns a score, tier (HOT/WARM/COLD/DISQUALIFY), reasoning, key talking points, "
                "risk flags, and a recommended action. Call this once search_company and "
                "search_recent_activity have both been called. The framework automatically "
                "injects the research results — you only need to provide lead_name and company."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "lead_name": {
                        "type": "string",
                        "description": "Full name of the lead contact.",
                    },
                    "company": {
                        "type": "string",
                        "description": "Company name.",
                    },
                },
                "required": ["lead_name", "company"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "draft_outreach_email",
            "description": (
                "Draft a personalized outreach email for the lead using research findings and score. "
                "The email references specific details found during research (not a generic template). "
                "Call this only if the lead score is 40 or above (WARM or HOT). The framework "
                "automatically injects all research context — you only need lead_name, company, and email."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "lead_name": {
                        "type": "string",
                        "description": "Full name of the lead contact.",
                    },
                    "company": {
                        "type": "string",
                        "description": "Company name.",
                    },
                    "email": {
                        "type": "string",
                        "description": "Lead's email address.",
                    },
                },
                "required": ["lead_name", "company", "email"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "log_to_supabase",
            "description": (
                "Save the complete lead qualification profile to the Supabase database. "
                "Call this after scoring (and optionally after email drafting) to persist all research, "
                "score, and agent output for CRM tracking. The framework builds the full profile "
                "automatically from all prior tool results — no arguments required."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_telegram_alert",
            "description": (
                "Send a Telegram notification with the lead qualification summary. "
                "Call this as the final step to alert the sales analyst in real time. "
                "Always call this regardless of lead tier. The framework builds the alert "
                "automatically — no arguments required."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


# ---------------------------------------------------------------------------
# Tool dispatcher
# ---------------------------------------------------------------------------

class ToolExecutionError(Exception):
    """Raised when a tool fails to execute."""


def dispatch(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """
    Execute a tool by name with the given arguments.

    Args:
        tool_name: One of the 6 registered tool names.
        arguments: Parsed JSON arguments from the LLM tool call.

    Returns:
        A dict result that is passed back to the LLM as a tool observation.

    Raises:
        ToolExecutionError: Wraps any underlying exception with context.
    """
    try:
        if tool_name == "search_company":
            from search import search_company
            return search_company(arguments["company_name"])

        if tool_name == "search_recent_activity":
            from search import search_recent_activity
            return search_recent_activity(arguments["company_name"])

        if tool_name == "score_lead":
            from llm import score_lead
            # company_info and recent_activity are injected by agent._inject_context
            return score_lead(
                lead_name=arguments["lead_name"],
                company=arguments["company"],
                company_info=arguments.get("company_info", {}),
                recent_activity=arguments.get("recent_activity", {}),
            )

        if tool_name == "draft_outreach_email":
            from llm import draft_email
            # company_info, recent_activity, score_result injected by agent._inject_context
            return draft_email(
                lead_name=arguments["lead_name"],
                company=arguments["company"],
                email=arguments["email"],
                company_info=arguments.get("company_info", {}),
                recent_activity=arguments.get("recent_activity", {}),
                score_result=arguments.get("score_result", {}),
            )

        if tool_name == "log_to_supabase":
            from database import log_lead
            # lead_profile built by agent._build_lead_profile and injected
            return log_lead(arguments.get("lead_profile", {}))

        if tool_name == "send_telegram_alert":
            from notifier import send_alert
            # lead_summary built by agent._build_telegram_summary and injected
            return send_alert(arguments.get("lead_summary", {}))

        raise ToolExecutionError(f"Unknown tool: {tool_name}")

    except ToolExecutionError:
        raise
    except KeyError as exc:
        raise ToolExecutionError(f"Missing required argument for '{tool_name}': {exc}") from exc
    except Exception as exc:
        raise ToolExecutionError(f"Tool '{tool_name}' failed: {exc}") from exc
