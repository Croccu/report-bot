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

# register the action handler for the reminder button
def register_reminder_handlers(app) -> None:

    @app.action("open_report_modal")
    def handle_open_report_modal(ack, body, client):  # type: ignore[unused-variable]
        ack()
        trigger_id = body["trigger_id"]
        client.views_open(
            trigger_id=trigger_id,
            view=build_report_modal_view(),
        )
