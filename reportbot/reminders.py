import random
from typing import List

from slack_sdk.errors import SlackApiError


def _build_report_modal_view() -> dict:
    """Build the duty report modal.

    NOTE: This must stay in sync with the modal opened by the /report command
    in bot.py (same block_ids, action_ids, and callback_id) so that the
    `handle_modal_submission` view handler can read the fields correctly.
    """
    return {
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
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Night summary, incidents, flow, etc.",
                    },
                },
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": "*KYC — General*"}},
            {
                "type": "input",
                "block_id": "kyc_general_queue_block",
                "label": {"type": "plain_text", "text": "General Queue (number)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "kyc_general_queue_input",
                },
            },
            {
                "type": "input",
                "block_id": "kyc_security_block",
                "label": {"type": "plain_text", "text": "Security (number)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "kyc_security_input",
                },
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": "*KYC — Peru*"}},
            {
                "type": "input",
                "block_id": "kyc_peru_queue_block",
                "label": {"type": "plain_text", "text": "Peru Queue (number)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "kyc_peru_queue_input",
                },
            },
            {
                "type": "input",
                "block_id": "kyc_peru_security_block",
                "label": {"type": "plain_text", "text": "Peru Security (number)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "kyc_peru_security_input",
                },
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": "*Payouts*"}},
            {
                "type": "input",
                "block_id": "payouts_row_block",
                "label": {
                    "type": "plain_text",
                    "text": "ROW (short text, e.g. 'up to date', '1 page')",
                },
                "element": {
                    "type": "plain_text_input",
                    "action_id": "payouts_row_input",
                },
            },
            {
                "type": "input",
                "block_id": "payouts_peru_block",
                "label": {"type": "plain_text", "text": "Peru (short text)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "payouts_peru_input",
                },
            },
            {
                "type": "input",
                "block_id": "highlights_block",
                "label": {"type": "plain_text", "text": "Highlights (free text)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "highlights_input",
                    "multiline": True,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Critical updates/issues",
                    },
                },
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": "*Edgetier*"}},
            {
                "type": "input",
                "block_id": "edgetier_reports_block",
                "label": {"type": "plain_text", "text": "Reports (number)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "edgetier_reports_input",
                },
            },
            {
                "type": "input",
                "block_id": "edgetier_general_block",
                "label": {"type": "plain_text", "text": "General (number)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "edgetier_general_input",
                },
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": "*PSP inbox*"}},
            {
                "type": "input",
                "block_id": "psp_inbox_block",
                "label": {"type": "plain_text", "text": "Pending cases (number)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "psp_inbox_input",
                },
            },
        ],
    }


def get_channel_members(app, channel_id: str) -> List[str]:
    """Return a list of user IDs in the given channel.

    This intentionally does NOT filter by Slack presence, to avoid requiring
    additional presence scopes. If you later add presence scopes to your bot
    token, you can reintroduce presence checks here.
    """
    try:
        members_resp = app.client.conversations_members(channel=channel_id)
        member_ids = members_resp.get("members", [])
    except SlackApiError as e:
        print(f"Error fetching channel members: {e.response['error']}")
        return []

    # Try to remove the bot itself from the candidate list so we only ping humans.
    try:
        auth_info = app.client.auth_test()
        bot_user_id = auth_info.get("user_id")
    except SlackApiError as e:
        print(f"Error calling auth_test: {e.response['error']}")
        bot_user_id = None

    if bot_user_id:
        member_ids = [m for m in member_ids if m != bot_user_id]

    return member_ids


def send_report_prompt(app, channel_id: str) -> None:
    """Pick a random channel member and ping them with a button to open the modal."""
    members = get_channel_members(app, channel_id)
    if not members:
        print("No members found to ping.")
        return

    chosen = random.choice(members)

    try:
        app.client.chat_postMessage(
            channel=channel_id,
            text=f"<@{chosen}> it's time to fill in the duty report.",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"<@{chosen}> it's time to fill in the duty report.",
                    },
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Open report form"},
                            "action_id": "open_report_modal",
                        }
                    ],
                },
            ],
        )
    except SlackApiError as e:
        print(f"Error sending prompt: {e.response['error']}")


def register_reminder_handlers(app) -> None:
    """Register the button action that opens the duty report modal."""

    @app.action("open_report_modal")
    def handle_open_report_modal(ack, body, client):  # type: ignore[unused-variable]
        ack()
        trigger_id = body["trigger_id"]
        client.views_open(
            trigger_id=trigger_id,
            view=_build_report_modal_view(),
        )
