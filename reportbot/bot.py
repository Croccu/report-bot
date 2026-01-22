import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from datetime import datetime

from .reminders import register_reminder_handlers, send_report_prompt

load_dotenv()

BOT_TOKEN = os.getenv("REPORTBOT_SLACK_BOT_TOKEN")
APP_TOKEN = os.getenv("REPORTBOT_APP_TOKEN")
CHANNEL_ID = os.getenv("REPORTBOT_CHANNEL_ID")

app = App(token=BOT_TOKEN)
register_reminder_handlers(app)

# ----- Helpers ---------------------------------------------------------------
def _get(view, block_id, action_id, default=""):
    try:
        v = view["state"]["values"][block_id][action_id].get("value", default)
        return v if v is not None else default
    except Exception:
        return default

def _to_int(s, default=0):
    try:
        return int(str(s).strip())
    except Exception:
        return default

# ----- Slash command: /report  ----------------------------------------------
@app.command("/report")
def handle_report(ack, body, client):
    ack()

    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "report_modal",
            "title": {"type": "plain_text", "text": "Duty Report"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "close": {"type": "plain_text", "text": "Cancel"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "summary_block",
                    "label": {"type": "plain_text", "text": "Summary (free text)"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "summary_input",
                        "multiline": True,
                        "placeholder": {"type": "plain_text", "text": "Night summary, incidents, flow, etc."}
                    }
                },

                {"type": "section", "text": {"type": "mrkdwn", "text": "*KYC — General*"}},
                {
                    "type": "input",
                    "block_id": "kyc_general_queue_block",
                    "label": {"type": "plain_text", "text": "General Queue (number)"},
                    "element": {"type": "plain_text_input", "action_id": "kyc_general_queue_input"}
                },
                {
                    "type": "input",
                    "block_id": "kyc_security_block",
                    "label": {"type": "plain_text", "text": "Security (number)"},
                    "element": {"type": "plain_text_input", "action_id": "kyc_security_input"}
                },

                {"type": "section", "text": {"type": "mrkdwn", "text": "*KYC — Peru*"}},
                {
                    "type": "input",
                    "block_id": "kyc_peru_queue_block",
                    "label": {"type": "plain_text", "text": "Peru Queue (number)"},
                    "element": {"type": "plain_text_input", "action_id": "kyc_peru_queue_input"}
                },
                {
                    "type": "input",
                    "block_id": "kyc_peru_security_block",
                    "label": {"type": "plain_text", "text": "Peru Security (number)"},
                    "element": {"type": "plain_text_input", "action_id": "kyc_peru_security_input"}
                },

                {"type": "section", "text": {"type": "mrkdwn", "text": "*Payouts*" }},
                {
                    "type": "input",
                    "block_id": "payouts_row_block",
                    "label": {"type": "plain_text", "text": "ROW (short text, e.g. 'up to date', '1 page')"},
                    "element": {"type": "plain_text_input", "action_id": "payouts_row_input"}
                },
                {
                    "type": "input",
                    "block_id": "payouts_peru_block",
                    "label": {"type": "plain_text", "text": "Peru (short text)"},
                    "element": {"type": "plain_text_input", "action_id": "payouts_peru_input"}
                },

                {
                    "type": "input",
                    "block_id": "highlights_block",
                    "label": {"type": "plain_text", "text": "Highlights (free text)"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "highlights_input",
                        "multiline": True,
                        "placeholder": {"type": "plain_text", "text": "Critical updates/issues"}
                    }
                },

                {"type": "section", "text": {"type": "mrkdwn", "text": "*Edgetier*" }},
                {
                    "type": "input",
                    "block_id": "edgetier_reports_block",
                    "label": {"type": "plain_text", "text": "Reports (number)"},
                    "element": {"type": "plain_text_input", "action_id": "edgetier_reports_input"}
                },
                {
                    "type": "input",
                    "block_id": "edgetier_general_block",
                    "label": {"type": "plain_text", "text": "General (number)"},
                    "element": {"type": "plain_text_input", "action_id": "edgetier_general_input"}
                },

                {"type": "section", "text": {"type": "mrkdwn", "text": "*PSP inbox*" }},
                {
                    "type": "input",
                    "block_id": "psp_inbox_block",
                    "label": {"type": "plain_text", "text": "Pending cases (number)"},
                    "element": {"type": "plain_text_input", "action_id": "psp_inbox_input"}
                },
            ],
        }
    )


# ----- Slash command: /report-ask -------------------------------------------
@app.command("/report-ask")
def handle_report_ask(ack, body, respond):
    """Slash command that picks an online user and pings them with a button.

    This reuses the reminder logic in reminders.send_report_prompt.
    """
    ack()
    send_report_prompt(app, CHANNEL_ID)
    respond("Okay, I'll ask someone in the channel to fill in the duty report.")


# ----- Modal submission ------------------------------------------------------
@app.view("report_modal")
def handle_modal_submission(ack, body, client, view):
    ack()

    user_id = body["user"]["id"]

    # Pull raw values
    summary = _get(view, "summary_block", "summary_input")
    kyc_general_queue = _to_int(_get(view, "kyc_general_queue_block", "kyc_general_queue_input"))
    kyc_security = _to_int(_get(view, "kyc_security_block", "kyc_security_input"))
    kyc_peru_queue = _to_int(_get(view, "kyc_peru_queue_block", "kyc_peru_queue_input"))
    kyc_peru_security = _to_int(_get(view, "kyc_peru_security_block", "kyc_peru_security_input"))

    payouts_row = _get(view, "payouts_row_block", "payouts_row_input", default="up to date")
    payouts_peru = _get(view, "payouts_peru_block", "payouts_peru_input", default="up to date")

    highlights = _get(view, "highlights_block", "highlights_input")

    edgetier_reports = _to_int(_get(view, "edgetier_reports_block", "edgetier_reports_input"))
    edgetier_general = _to_int(_get(view, "edgetier_general_block", "edgetier_general_input"))

    psp_inbox = _to_int(_get(view, "psp_inbox_block", "psp_inbox_input"))

    # Build message in your exact format
    lines = [
        "Hello!",
        "",
        summary if summary.strip() else "-",
        "",
        "KYC (these numbers, both the General and Peru will hopefully be retrievable by API)",
        f"General Queue: {kyc_general_queue}",
        f"Security: {kyc_security}",
        "",
        f"Peru Queue: {kyc_peru_queue}",
        f"Peru Security: {kyc_peru_security}",
        "",
        "Payouts: (this is also actually just a set of numbers, hopefully also reachable by API)",
        f"ROW: {payouts_row}",
        f"Peru: {payouts_peru}",
        "",
        "Highlights:",
        highlights if highlights.strip() else "-",
        "",
        "Routines: (What reports have been done, routines etc. Let's skip for now, can be dropdown of options later)",
        "-",
        "",
        "Edgetier: (user entered numbers through modal)",
        f"Reports - {edgetier_reports}",
        f"General - {edgetier_general}",
        "",
        "PSP inbox: (user entered numbers through modal)",
        f"{psp_inbox} pending cases",
        "",
        "Have a great day!",
    ]

    client.chat_postMessage(
        channel=CHANNEL_ID,
        text="\n".join(lines)
    )

if __name__ == "__main__":
    handler = SocketModeHandler(app, APP_TOKEN)
    handler.start()
