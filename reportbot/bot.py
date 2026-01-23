import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
import threading
import time
import schedule


# Load environment variables before importing modules that read them
load_dotenv()

from .reminders import register_reminder_handlers, send_report_prompt
from .views import build_report_modal_view
from .modal_handlers import register_modal_handlers

BOT_TOKEN = os.getenv("REPORTBOT_SLACK_BOT_TOKEN")
APP_TOKEN = os.getenv("REPORTBOT_APP_TOKEN")
CHANNEL_ID = os.getenv("REPORTBOT_CHANNEL_ID")

app = App(token=BOT_TOKEN)
register_reminder_handlers(app)
register_modal_handlers(app, CHANNEL_ID)

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

# helpers (slash commands only; modal helpers live in modal_handlers.py)

# slash command: /report
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


# modal submission handler lives in modal_handlers.register_modal_handlers

if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=_schedule_report_prompts, daemon=True)
    scheduler_thread.start()

    handler = SocketModeHandler(app, APP_TOKEN)
    handler.start()
