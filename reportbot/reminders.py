import json
import random
from typing import List

from slack_sdk.errors import SlackApiError
from .views import build_report_modal_view

# return a list of user IDs in the given channel
# currently does NOT filter by presence
def get_channel_members(app, channel_id: str) -> List[str]:
    try:
        members_resp = app.client.conversations_members(channel=channel_id)
        member_ids = members_resp.get("members", [])
    except SlackApiError as e:
        print(f"Error fetching channel members: {e.response['error']}")
        return []

    # try to remove the bot itself from the candidate list so we only ping humans.
    try:
        auth_info = app.client.auth_test()
        bot_user_id = auth_info.get("user_id")
    except SlackApiError as e:
        print(f"Error calling auth_test: {e.response['error']}")
        bot_user_id = None

    if bot_user_id:
        member_ids = [m for m in member_ids if m != bot_user_id]

    return member_ids

# pick a random channel member and ping them with a button to open the modal
def send_report_prompt(app, channel_id: str) -> None:
    members = get_channel_members(app, channel_id)
    if not members:
        print("No members found to ping.")
        return

    chosen = random.choice(members)

    user_mention = f"<@{chosen}>"
    try:
        app.client.chat_postMessage(
            channel=channel_id,
            text=f"{user_mention} it's time to fill in the duty report.",
            blocks=_build_prompt_blocks(user_mention, status="pending"),
        )
    except SlackApiError as e:
        print(f"Error sending prompt: {e.response['error']}")

# helper: build blocks that show the current status of a report prompt
def _build_prompt_blocks(user_mention: str, *, status: str = "pending") -> list:
    """Return message blocks for the report prompt in one of three states.

    status: 'pending'     – original button
            'in_progress' – orange "In progress" indicator
            'solved'      – green "Solved" indicator (no clickable button)
    """
    text_block = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"{user_mention} it's time to fill in the duty report.",
        },
    }

    if status == "in_progress":
        return [
            text_block,
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🟠 *In progress* — filling in the report…",
                    }
                ],
            },
        ]

    if status == "solved":
        return [
            text_block,
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "✅ Solved"},
                        "style": "primary",
                        "action_id": "report_solved_noop",
                    }
                ],
            },
        ]

    # default: pending
    return [
        text_block,
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
    ]


# register the action handler for the reminder button
def register_reminder_handlers(app) -> None:

    @app.action("open_report_modal")
    def handle_open_report_modal(ack, body, client):  # type: ignore[unused-variable]
        ack()
        trigger_id = body["trigger_id"]

        # figure out which message was clicked so we can update it later
        channel_id = body.get("channel", {}).get("id")
        message_ts = body.get("message", {}).get("ts")
        user_id = body["user"]["id"]

        # encode origin info so the modal submission handler can find the
        # prompt message and mark it as solved
        metadata = {}
        if channel_id and message_ts:
            metadata = {"channel": channel_id, "message_ts": message_ts, "user_id": user_id}

            # immediately flip the prompt to "in progress"
            try:
                client.chat_update(
                    channel=channel_id,
                    ts=message_ts,
                    text=f"<@{user_id}> it's time to fill in the duty report.",
                    blocks=_build_prompt_blocks(f"<@{user_id}>", status="in_progress"),
                )
            except Exception as e:
                print(f"Error updating prompt to in_progress: {e}")

        private_metadata = json.dumps(metadata) if metadata else None

        client.views_open(
            trigger_id=trigger_id,
            view=build_report_modal_view(private_metadata=private_metadata),
        )

    # no-op handler for the disabled "Solved" button
    @app.action("report_solved_noop")
    def handle_solved_noop(ack, body, client):  # type: ignore[unused-variable]
        ack()
