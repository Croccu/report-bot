# Report Bot

A Slack bot for submitting structured duty reports via `/report` slash command.
Built with [Slack Bolt (Python)](https://slack.dev/bolt-python) and Socket Mode.

---

## Features
- `/report` opens a Slack modal form with fields:
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

- Run `/report` to open the duty report modal.
  - Fill the fields → Submit → A formatted report is posted in the configured
    channel and, if email settings are configured, the same report is also
    sent via email.
- Run `/report-ask` to have the bot pick a random channel member and ping them
  with a button that opens the same report modal.

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
├── .env                   # environment variables (never commit this)
└── README.md
```

---
