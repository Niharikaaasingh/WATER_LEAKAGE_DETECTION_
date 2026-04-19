"""
alerts.py — Alert helpers for AquaGuard IoT Water Leakage Detection System
Handles:
  • Email alerts via SMTP (Gmail)
  • SMS alerts via Twilio
Both functions are safe to call even when credentials are placeholders —
they catch all exceptions and return a status string so the UI can report
what happened without crashing.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


# ══════════════════════════════════════════════════════════════════════════════
# ── EMAIL CONFIGURATION ───────────────────────────────────────────────────────
# Replace the values below with your real Gmail credentials.
# IMPORTANT: Use an App Password, NOT your regular Gmail password.
#   How to create one:
#   1. Go to myaccount.google.com → Security → 2-Step Verification (enable it)
#   2. Then: myaccount.google.com/apppasswords → create password for "Mail"
#   3. Paste the 16-char password as EMAIL_PASSWORD below.
# ══════════════════════════════════════════════════════════════════════════════

EMAIL_SENDER   = "your_gmail@gmail.com"       # ← replace with sender Gmail
EMAIL_PASSWORD = "your_app_password_here"     # ← replace with 16-char App Password
EMAIL_RECEIVER = "receiver_email@example.com" # ← replace with recipient email
EMAIL_SMTP     = "smtp.gmail.com"
EMAIL_PORT     = 465                          # SSL port


def send_email_alert(flow: float, moisture: float, trigger: str) -> str:
    """
    Send a leak-detection email alert via Gmail SMTP (SSL).

    Parameters
    ----------
    flow     : current water flow reading (L/min)
    moisture : current moisture level (%)
    trigger  : trigger reason string from detect_leak()

    Returns
    -------
    str : "sent" | "skipped" | "error: <message>"
    """

    # Guard: skip if credentials are still placeholders
    if "your_" in EMAIL_SENDER or "your_" in EMAIL_PASSWORD:
        return "skipped (credentials not configured)"

    trigger_map = {
        "flow_drop":                "Sudden drop in water flow (≥45%)",
        "moisture_high":            "Moisture level exceeded threshold (≥70%)",
        "flow_drop + moisture_high":"Both: flow drop AND high moisture",
        "manual":                   "Manually triggered via dashboard",
    }
    trigger_label = trigger_map.get(trigger, "Leak condition detected")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ── Build email ──────────────────────────────────────────────────────────
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🚨 AquaGuard ALERT — Water Leak Detected at {now}"
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = EMAIL_RECEIVER

    # Plain-text fallback
    text_body = f"""
AquaGuard Water Leakage Detection System
==========================================
STATUS     : ⚠ LEAK DETECTED
Time       : {now}
Trigger    : {trigger_label}
Flow Rate  : {flow} L/min
Moisture   : {moisture}%

Please inspect your water supply immediately.
This alert was generated automatically by the AquaGuard IoT system.
"""

    # HTML body
    html_body = f"""
<html><body style="font-family:Arial,sans-serif;background:#f4f4f4;padding:20px">
  <div style="max-width:520px;margin:auto;background:#fff;border-radius:10px;
              border-left:6px solid #ff4466;overflow:hidden;box-shadow:0 2px 12px #0002">
    <div style="background:#0a0e1a;padding:20px 24px">
      <h2 style="color:#ff4466;margin:0;font-size:1.3rem">
        🚨 Water Leak Detected
      </h2>
      <p style="color:#64748b;margin:4px 0 0;font-size:0.8rem">
        AquaGuard IoT Monitoring System
      </p>
    </div>
    <div style="padding:24px">
      <table style="width:100%;border-collapse:collapse;font-size:0.92rem">
        <tr><td style="padding:8px 0;color:#555;width:130px"><b>Status</b></td>
            <td style="color:#ff4466;font-weight:700">⚠ LEAK DETECTED</td></tr>
        <tr><td style="padding:8px 0;color:#555"><b>Timestamp</b></td>
            <td>{now}</td></tr>
        <tr><td style="padding:8px 0;color:#555"><b>Trigger</b></td>
            <td>{trigger_label}</td></tr>
        <tr style="background:#fff4f6">
            <td style="padding:8px 6px;color:#555"><b>Flow Rate</b></td>
            <td style="color:#ff4466"><b>{flow} L/min</b></td></tr>
        <tr style="background:#fff4f6">
            <td style="padding:8px 6px;color:#555"><b>Moisture</b></td>
            <td style="color:#ff4466"><b>{moisture}%</b></td></tr>
      </table>
      <hr style="border:none;border-top:1px solid #eee;margin:20px 0">
      <p style="color:#888;font-size:0.8rem;margin:0">
        Please inspect your water supply immediately.<br>
        This alert was generated automatically by the AquaGuard IoT system.
      </p>
    </div>
  </div>
</body></html>
"""

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    # ── Send ─────────────────────────────────────────────────────────────────
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(EMAIL_SMTP, EMAIL_PORT, context=context) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        return "sent"
    except smtplib.SMTPAuthenticationError:
        return "error: authentication failed — check EMAIL_SENDER / EMAIL_PASSWORD"
    except smtplib.SMTPException as e:
        return f"error: SMTP error — {e}"
    except Exception as e:
        return f"error: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# ── TWILIO SMS CONFIGURATION ──────────────────────────────────────────────────
# Sign up at twilio.com/try-twilio (free trial gives ~$15 credit).
# Find your credentials at console.twilio.com → Account Info.
# ══════════════════════════════════════════════════════════════════════════════

TWILIO_ACCOUNT_SID  = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # ← replace
TWILIO_AUTH_TOKEN   = "your_auth_token_here"                # ← replace
TWILIO_FROM_NUMBER  = "+1XXXXXXXXXX"   # ← your Twilio number (E.164 format)
TWILIO_TO_NUMBER    = "+91XXXXXXXXXX"  # ← recipient number  (E.164 format)


def send_sms_alert(flow: float, moisture: float, trigger: str) -> str:
    """
    Send a leak-detection SMS via Twilio.

    Parameters
    ----------
    flow     : current water flow reading (L/min)
    moisture : current moisture level (%)
    trigger  : trigger reason string from detect_leak()

    Returns
    -------
    str : "sent: <SID>" | "skipped" | "error: <message>"
    """

    # Guard: skip if credentials are still placeholders
    if TWILIO_ACCOUNT_SID.startswith("AC" + "x") or "your_" in TWILIO_AUTH_TOKEN:
        return "skipped (Twilio credentials not configured)"

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    body = (
        f"🚨 AquaGuard ALERT\n"
        f"Water leak detected at {now}\n"
        f"Flow: {flow} L/min | Moisture: {moisture}%\n"
        f"Trigger: {trigger}\n"
        f"Please inspect your water supply immediately."
    )

    try:
        # Lazy import — only fails if twilio package is not installed
        from twilio.rest import Client  # type: ignore
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=body,
            from_=TWILIO_FROM_NUMBER,
            to=TWILIO_TO_NUMBER,
        )
        return f"sent: {message.sid}"
    except ImportError:
        return "error: twilio package not installed — run: pip install twilio"
    except Exception as e:
        return f"error: {e}"