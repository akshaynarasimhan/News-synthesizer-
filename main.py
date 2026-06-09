import os
import json
import sys
from datetime import datetime, timezone, timedelta

from scraper import fetch_news
from analyzer import analyze_news
from formatter import format_email
from notifier import send_email

IST = timezone(timedelta(hours=5, minutes=30))


def main():
    now = datetime.now(tz=IST)
    print(f"[{now.strftime('%Y-%m-%d %H:%M IST')}] Morning news synthesis starting...")

    with open("watchlist.json") as f:
        watchlist = json.load(f)["stocks"]

    print("Fetching news from Moneycontrol and Economic Times...")
    articles = fetch_news(hours_back=20)
    if not articles:
        print("ERROR: No articles fetched. Exiting.")
        sys.exit(1)

    print(f"Analyzing {len(articles)} articles with Claude...")
    analysis = analyze_news(articles, watchlist)

    date_str = now.strftime("%A, %d %B %Y")
    subject = f"Morning Market Brief — {date_str}"
    html_body = format_email(analysis, date_str)

    recipient = os.environ["RECIPIENT_EMAIL"]
    send_email(subject, html_body, recipient)
    print(f"Done. Email sent to {recipient}")


if __name__ == "__main__":
    main()
