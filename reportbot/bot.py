import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from datetime import datetime
import threading
import time
import html
import schedule


# Load environment variables before importing modules that read them
load_dotenv()

from .reminders import register_reminder_handlers, send_report_prompt
from .views import build_report_modal_view
from .email_utils import send_report_email

BOT_TOKEN = os.getenv("REPORTBOT_SLACK_BOT_TOKEN")
APP_TOKEN = os.getenv("REPORTBOT_APP_TOKEN")
CHANNEL_ID = os.getenv("REPORTBOT_CHANNEL_ID")

app = App(token=BOT_TOKEN)
register_reminder_handlers(app)

# run background scheduler that sends /report-ask style prompts twice a day
def _schedule_report_prompts() -> None:

    def morning_job() -> None:
        send_report_prompt(app, CHANNEL_ID)

    def night_job() -> None:
        send_report_prompt(app, CHANNEL_ID)

    # adjust these times if needed.
    schedule.every().day.at("07:50").do(morning_job)
    schedule.every().day.at("23:50").do(night_job)

    while True:
        schedule.run_pending()
        time.sleep(30)

# helpers
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

# slash command: /report
@app.command("/report")
def handle_report(ack, body, client):
    ack()

    client.views_open(
        trigger_id=body["trigger_id"],
        view=build_report_modal_view(),
    )


# slash command: /report-ask
@app.command("/report-ask")
def handle_report_ask(ack, body, respond):
    """Slash command that picks an online user and pings them with a button.

    This reuses the reminder logic in reminders.send_report_prompt.
    """
    ack()
    send_report_prompt(app, CHANNEL_ID)


# modal submission
@app.view("report_modal")
def handle_modal_submission(ack, body, client, view):
    ack()

    user_id = body["user"]["id"]

    # slack name for the user
    slack_display = user_id
    try:
        user_info = client.users_info(user=user_id)
        if user_info.get("ok"):
            user = user_info.get("user", {})
            profile = user.get("profile", {})
            slack_display = (
                profile.get("display_name")
                or profile.get("real_name")
                or user.get("name")
                or user_id
            )
    except Exception:
        # if lookup fails, fall back to raw user ID
        slack_display = user_id

    slack_mention = f"<@{user_id}>"
    email_from_label = f"@{slack_display}"

    # pull raw values
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

    # build message in your exact format
    # header: PaySec duty report dd.mm.yyyy
    date_str = datetime.now().strftime('%d.%m.%Y')

    slack_header = f"*PaySec duty report {date_str} from {slack_mention}*"
    email_header = f"PaySec duty report {date_str}"

    # slack-formatted text (mrkdwn)
    lines = [
        slack_header,
        "",
        "Hello!",
        "",
        "*Summary*",
        summary if summary.strip() else "-",
        "",
        "*KYC* (these numbers, both the General and Peru will hopefully be retrievable by API)",
        f"- General Queue: *{kyc_general_queue}*",
        f"- Security: *{kyc_security}*",
        "",
        "*KYC — Peru*",
        f"- Queue: *{kyc_peru_queue}*",
        f"- Security: *{kyc_peru_security}*",
        "",
        "*Payouts* (this is also actually just a set of numbers, hopefully also reachable by API)",
        f"- ROW: *{payouts_row}*",
        f"- Peru: *{payouts_peru}*",
        "",
        "*Highlights*",
        highlights if highlights.strip() else "-",
        "",
        "*Routines* (What reports have been done, routines etc. Let's skip for now, can be dropdown of options later)",
        "-",
        "",
        "*Edgetier* (user entered numbers through modal)",
        f"- Reports: *{edgetier_reports}*",
        f"- General: *{edgetier_general}*",
        "",
        "*PSP inbox* (user entered numbers through modal)",
        f"- *{psp_inbox}* pending cases",
        "",
        "_Have a great day!_",
    ]

    client.chat_postMessage(
        channel=CHANNEL_ID,
        text="\n".join(lines)
    )

    # also send via email (if SMTP and email env vars are configured).
    # use a simpler header for email (no Slack user mention in the subject).
    email_lines = [email_header] + [""] + [
        "Hello!",
        "",
        "Summary",
        summary if summary.strip() else "-",
        "",
        "KYC",
        f"- General Queue: {kyc_general_queue}",
        f"- Security: {kyc_security}",
        "",
        "KYC — Peru",
        f"- Queue: {kyc_peru_queue}",
        f"- Security: {kyc_peru_security}",
        "",
        "Payouts",
        f"- ROW: {payouts_row}",
        f"- Peru: {payouts_peru}",
        "",
        "Highlights",
        highlights if highlights.strip() else "-",
        "",
        "Routines",
        "-",
        "",
        "Edgetier",
        f"- Reports: {edgetier_reports}",
        f"- General: {edgetier_general}",
        "",
        "PSP inbox",
        f"- {psp_inbox} pending cases",
        "",
        "Have a great day!",
    ]

    subject = email_header
    body = "\n".join(email_lines)

    # simple HTML version for nicer rendering in email clients.
    def esc(text: str) -> str:
        return html.escape(text, quote=True)

    html_body = f"""<html>
  <body style=\"font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.5;\">
    <h1>{esc(email_header)}</h1>
    <p><strong>From (Slack):</strong> {esc(email_from_label)}</p>
    <p>Hello!</p>

    <h2>Summary</h2>
    <p>{esc(summary if summary.strip() else '-')}</p>

    <h2>KYC</h2>
    <ul>
      <li><strong>General Queue:</strong> {kyc_general_queue}</li>
      <li><strong>Security:</strong> {kyc_security}</li>
    </ul>

    <h2>KYC — Peru</h2>
    <ul>
      <li><strong>Queue:</strong> {kyc_peru_queue}</li>
      <li><strong>Security:</strong> {kyc_peru_security}</li>
    </ul>

    <h2>Payouts</h2>
    <ul>
      <li><strong>ROW:</strong> {esc(payouts_row)}</li>
      <li><strong>Peru:</strong> {esc(payouts_peru)}</li>
    </ul>

    <h2>Highlights</h2>
    <p>{esc(highlights if highlights.strip() else '-')}</p>

    <h2>Routines</h2>
    <p>-</p>

    <h2>Edgetier</h2>
    <ul>
      <li><strong>Reports:</strong> {edgetier_reports}</li>
      <li><strong>General:</strong> {edgetier_general}</li>
    </ul>

    <h2>PSP inbox</h2>
    <p>{psp_inbox} pending cases</p>

    <p><em>Have a great day!</em></p>
  </body>
</html>"""

    send_report_email(subject=subject, body=body, html_body=html_body)

if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=_schedule_report_prompts, daemon=True)
    scheduler_thread.start()

    handler = SocketModeHandler(app, APP_TOKEN)
    handler.start()
