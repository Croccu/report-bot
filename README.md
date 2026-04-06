# Report Bot

A Slack bot that automatically picks someone in the channel and asks them to
fill in the duty report. No more typing `/report` yourself — the bot pings a
random channel member with a button that opens the report form.
Built with [Slack Bolt (Python)](https://slack.dev/bolt-python) and Socket Mode.

---

## How it works
1. Twice a day (on a configurable schedule) the bot picks a random member of
   the configured channel and sends them a message with an **Open report form**
   button.
2. The selected person clicks the button, fills in the modal, and submits.
3. A formatted duty report is posted back into the channel (and optionally
   sent via email).

You can also trigger this flow manually with the `/report-ask` slash command
(useful for testing — see [Usage](#5-use-it) below).

## Features
- Automatic report prompts — bot selects a channel member and pings them with
  a button to open the report modal.
- `/report-ask` slash command to manually trigger the ask-to-report flow
  (great for testing without waiting for the schedule).
- `/report` slash command still available for anyone who wants to open the form
  directly.
- Modal form with fields:
  - Summary
  - KYC (General, Security, Peru Queue, Peru Security)
  - Payouts (ROW, Peru)
  - Highlights
  - Edgetier (Reports, General)
  - PSP inbox
- Bot posts a formatted duty report back into the channel using Slack mrkdwn
  (bold headline + section headers, bullet lists, etc.).
- Static intro/outro lines (“Hello!” / “Have a great day!”).
- Optional: send the same duty report via email using SMTP (e.g. Mailtrap sandbox
  or your own SMTP provider).

---

## Setup

### 1. Clone repo
```bash
git clone git@github.com:Croccu/report-bot.git
cd report-bot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
Create a `.env` file:
```env
REPORTBOT_SLACK_BOT_TOKEN=xoxb-your-bot-token
REPORTBOT_APP_TOKEN=xapp-your-app-token
REPORTBOT_CHANNEL_ID=C1234567890

# Email settings (optional, for sending the duty report via email)
REPORTBOT_SMTP_HOST=smtp.your-provider.com
REPORTBOT_SMTP_PORT=587
REPORTBOT_SMTP_USER=your-smtp-username
REPORTBOT_SMTP_PASSWORD=your-smtp-password
REPORTBOT_EMAIL_FROM=duty-bot@your-company.com
REPORTBOT_EMAIL_TO=duty-reports@your-company.com
```

- `REPORTBOT_SLACK_BOT_TOKEN` → Bot User OAuth Token from Slack app settings.
- `REPORTBOT_APP_TOKEN` → App-level token with `connections:write` (for Socket Mode).
- `REPORTBOT_CHANNEL_ID` → Slack channel ID where reports are posted.
- `REPORTBOT_SMTP_HOST` / `REPORTBOT_SMTP_PORT` → SMTP server host + port.
- `REPORTBOT_SMTP_USER` / `REPORTBOT_SMTP_PASSWORD` → SMTP credentials (if required).
- `REPORTBOT_EMAIL_FROM` → From address used for the emails (e.g. a duty-bot mailbox).
- `REPORTBOT_EMAIL_TO` → Default recipient address (e.g. a distribution list).

### 4. Run the bot
```bash
python3 -m reportbot.bot
```

### 5. Use it
In Slack:

- Run `/report-ask` to test the main flow — the bot picks a random channel
  member, pings them with a message, and gives them an **Open report form**
  button. Clicking the button opens the report modal.
- Run `/report` to open the duty report modal directly (without the bot
  picking someone).
- Fill the fields → Submit → A formatted report is posted in the configured
  channel and, if email settings are configured, also sent via email.

In production the bot triggers this automatically on a schedule (see
`_schedule_report_prompts` in `bot.py`), so no slash command is needed
day-to-day.

---

## Project Structure
```
report-bot/
├── reportbot/
│   ├── __init__.py        # package init
│   ├── bot.py             # main bot logic (socket mode, modal + report post + email)
│   ├── views.py           # Slack modal view definition
│   ├── reminders.py       # reminder helpers and /report-ask button handler
│   ├── email_utils.py     # SMTP helper for sending duty reports via email
│   └── post.py            # simple test message sender (optional)
├── requirements.txt
├── .env                   # environment variables
└── README.md
```

---
