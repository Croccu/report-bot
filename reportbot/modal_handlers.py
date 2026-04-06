import html
import json
from datetime import datetime
from typing import Any

from .email_utils import send_report_email
from .reminders import _build_prompt_blocks


def register_modal_handlers(app, channel_id: str) -> None:

    def _get(view: dict, block_id: str, action_id: str, default: str = "") -> str:
        try:
            v = view["state"]["values"][block_id][action_id].get("value", default)
            return v if v is not None else default
        except Exception:
            return default

    def _get_multi(view: dict, block_id: str, action_id: str) -> list[str]:
        try:
            opts = view["state"]["values"][block_id][action_id].get("selected_options") or []
            return [o["text"]["text"] for o in opts]
        except Exception:
            return []

    def _to_int(s: Any, default: int = 0) -> int:
        try:
            return int(str(s).strip())
        except Exception:
            return default

    @app.view("report_modal")
    def handle_modal_submission(ack, body, client, view):  # type: ignore[unused-variable]
        ack()

        user_id = body["user"]["id"]

        # try to resolve a slack name for the user
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
        routines = _get_multi(view, "routines_block", "routines_input")

        edgetier_reports
        edgetier_reports = _to_int(_get(view, "edgetier_reports_block", "edgetier_reports_input"))
        edgetier_general = _to_int(_get(view, "edgetier_general_block", "edgetier_general_input"))

        psp_inbox = _to_int(_get(view, "psp_inbox_block", "psp_inbox_input"))

        date_str = datetime.now().strftime("%d.%m.%Y")

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
            "*Routines* (What reports have been done, routines etc.)",
            "\n".join(f"- {r}" for r in routines) if routines else "-",
            "",
            "*Edgetier*",
            f"- Reports: *{edgetier_reports}*",
            f"- General: *{edgetier_general}*",
            "",
            "*PSP inbox*",
            f"- *{psp_inbox}* pending cases",
            "",
            "_Have a great day!_",
        ]

        # post into Slack channel
        client.chat_postMessage(
            channel=channel_id,
            text="\n".join(lines),
        )

        # plain-text email version (no Slack markup)
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
            "\n".join(f"- {r}" for r in routines) if routines else "-",
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

        # HTML email version
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
    <p>{esc(', '.join(routines)) if routines else '-'}</p>

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

        # if this modal was opened from a prompt message, mark it as solved
        raw_meta = view.get("private_metadata", "")
        if raw_meta:
            try:
                meta = json.loads(raw_meta)
                prompt_channel = meta.get("channel")
                prompt_ts = meta.get("message_ts")
                prompt_user = meta.get("user_id", user_id)
                if prompt_channel and prompt_ts:
                    client.chat_update(
                        channel=prompt_channel,
                        ts=prompt_ts,
                        text=f"<@{prompt_user}> it's time to fill in the duty report.",
                        blocks=_build_prompt_blocks(
                            f"<@{prompt_user}>", status="solved"
                        ),
                    )
            except Exception as e:
                print(f"Error updating prompt to solved: {e}")
