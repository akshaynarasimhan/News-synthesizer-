# Morning Market Brief — News Synthesizer

A daily automated digest that scrapes **Moneycontrol** and **Economic Times**, synthesizes the top stories using Claude, and emails a sharp market brief to your inbox by 8 AM IST.

## What you get every morning

- **Macro Setup** — global cues, domestic themes, Nifty/Sensex outlook
- **7-9 Top Stories** — each with market impact, pros & cons
- **Watchlist Snapshot** — which of your stocks are impacted today and why

## Setup

### 1. Add GitHub Actions Secrets

Go to **Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `GMAIL_USER` | Gmail address used to send (e.g. `yourname@gmail.com`) |
| `GMAIL_APP_PASSWORD` | 16-char Gmail App Password (see below) |
| `RECIPIENT_EMAIL` | Where to receive the brief (can be same or different) |

### 2. Generate a Gmail App Password

1. Enable 2-Step Verification on your Google account
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Create an app password for "Mail" → copy the 16-character code
4. Use that as `GMAIL_APP_PASSWORD`

### 3. Update your watchlist

Edit `watchlist.json` to match your actual holdings/watchlist. The default includes 20 large-cap Indian stocks across key sectors.

### 4. Enable Actions

The workflow runs automatically at **7:30 AM IST (2:00 AM UTC)** every day.  
To test immediately: go to **Actions → Morning Market Brief → Run workflow**.

## Local testing

```bash
cp .env.example .env
# fill in .env with your keys
pip install -r requirements.txt
python main.py
```

## Schedule

`cron: '0 2 * * *'` — 2:00 AM UTC = 7:30 AM IST, email arrives well before 8 AM.
