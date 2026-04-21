"""
Gmail SMTP email sender.
Sends personalized outreach emails for HOT leads automatically.
Includes a professional HTML template with plain text fallback.
"""

from __future__ import annotations

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GMAIL_SENDER = os.getenv("GMAIL_SENDER", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
GMAIL_SMTP_HOST = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587


def _build_html(subject: str, body: str, lead_name: str, company: str) -> str:
    """Render a modern, clean HTML email template."""
    first_name = lead_name.split()[0] if lead_name else "there"
    paragraphs = "".join(
        f"<p style='margin:0 0 16px 0;color:#374151;font-size:15px;line-height:1.65;'>{line}</p>"
        for line in body.split("\n")
        if line.strip()
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{subject}</title>
</head>
<body style="margin:0;padding:0;background:#f9fafb;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f9fafb;padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

          <!-- Header -->
          <tr>
            <td style="background:#111827;border-radius:12px 12px 0 0;padding:28px 36px;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td>
                    <span style="display:inline-flex;align-items:center;gap:8px;">
                      <span style="display:inline-block;width:28px;height:28px;background:#10b981;border-radius:6px;text-align:center;line-height:28px;font-size:14px;font-weight:700;color:#111827;">A</span>
                      <span style="color:#f9fafb;font-size:15px;font-weight:600;letter-spacing:-0.01em;">AutoSystems</span>
                    </span>
                  </td>
                  <td align="right">
                    <span style="color:#6b7280;font-size:12px;">AI Sales Automation</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="background:#ffffff;padding:36px 36px 28px 36px;">
              {paragraphs}
            </td>
          </tr>

          <!-- Divider + signature -->
          <tr>
            <td style="background:#ffffff;padding:0 36px 36px 36px;border-top:1px solid #f3f4f6;">
              <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:24px;">
                <tr>
                  <td>
                    <p style="margin:0;color:#111827;font-size:14px;font-weight:600;">AutoSystems Team</p>
                    <p style="margin:4px 0 0 0;color:#6b7280;font-size:13px;">AI Sales Automation</p>
                    <a href="mailto:{GMAIL_SENDER}" style="color:#10b981;font-size:13px;text-decoration:none;">{GMAIL_SENDER}</a>
                  </td>
                  <td align="right" valign="bottom">
                    <span style="display:inline-block;background:#ecfdf5;color:#065f46;font-size:11px;font-weight:600;padding:4px 10px;border-radius:20px;letter-spacing:0.04em;">AUTOMATED OUTREACH</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f9fafb;border-radius:0 0 12px 12px;padding:20px 36px;border-top:1px solid #e5e7eb;">
              <p style="margin:0;color:#9ca3af;font-size:11px;text-align:center;">
                You received this because {company} matched our qualification criteria.
                Reply to this email to unsubscribe.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def send_email(
    to_email: str,
    subject: str,
    body: str,
    lead_name: str = "",
    company: str = "",
) -> dict:
    """
    Send a personalized outreach email via Gmail SMTP.

    Args:
        to_email: Recipient email address.
        subject: Email subject line.
        body: Email body (plain text, \\n for line breaks).
        lead_name: Lead's full name.
        company: Lead's company name.

    Returns:
        dict with: success (bool), error (str or None)
    """
    if not GMAIL_SENDER or not GMAIL_APP_PASSWORD:
        return {"success": False, "error": "GMAIL_SENDER or GMAIL_APP_PASSWORD not configured."}

    if GMAIL_APP_PASSWORD == "YOUR_APP_PASSWORD_HERE":
        return {"success": False, "error": "Gmail App Password not set in .env"}

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"AutoSystems <{GMAIL_SENDER}>"
        msg["To"] = to_email
        msg["Subject"] = subject

        # Plain text fallback
        msg.attach(MIMEText(body, "plain"))
        # HTML version (preferred by email clients)
        msg.attach(MIMEText(_build_html(subject, body, lead_name, company), "html"))

        with smtplib.SMTP(GMAIL_SMTP_HOST, GMAIL_SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_SENDER, to_email, msg.as_string())

        logger.info("Email sent to %s (%s)", to_email, lead_name)
        return {"success": True, "error": None, "to": to_email, "subject": subject}

    except smtplib.SMTPAuthenticationError:
        error = "Gmail authentication failed. Check GMAIL_APP_PASSWORD in .env."
        logger.error(error)
        return {"success": False, "error": error}
    except Exception as exc:
        error = f"Email send failed: {exc}"
        logger.error(error)
        return {"success": False, "error": error}

