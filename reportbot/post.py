import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv


load_dotenv()

SLACK_BOT_TOKEN = os.getenv("REPORTBOT_SLACK_BOT_TOKEN")
CHANNEL_ID = os.getenv("REPORTBOT_CHANNEL_ID")

client = WebClient(token=SLACK_BOT_TOKEN)

def send_message(text: str):
    try:
        response = client.chat_postMessage(channel=CHANNEL_ID, text=text)
        print(f"Message sent, ts={response['ts']}")
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

if __name__ == "__main__":
    send_message("Hello from ReportBot! This is test message 2.")
