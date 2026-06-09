import os
import json
import sys
from datetime import datetime, timezone, timedelta

from scraper import fetch_news
from analyzer import analyze_news
from formatter import format_email
from notifier import send_email

IST = timezone(timedelta(hours=5, minutes=30))


def _load_from_excel(path: str) -> list:
    from openpyxl import load_workbook
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    if not rows:
        return []
    headers = [str(h).strip().lower() if h else "" for h in rows[0]]
    stocks = []
    for row in rows[1:]:
        if not any(row):
            continue
        d = dict(zip(headers, row))
        symbol = str(d.get("symbol", "") or "").strip().upper()
        name   = str(d.get("name",   "") or "").strip()
        sector = str(d.get("sector", "") or "").strip()
        if symbol:
            stocks.append({"symbol": symbol, "name": name, "sector": sector})
    return stocks


def load_watchlist() -> list:
    if os.path.exists("watchlist.xlsx"):
        stocks = _load_from_excel("watchlist.xlsx")
        print(f"  Loaded {len(stocks)} stocks from watchlist.xlsx")
        return stocks
    with open("watchlist.json") as f:
        stocks = json.load(f)["stocks"]
    print(f"  Loaded {len(stocks)} stocks from watchlist.json")
    return stocks


def main():
    now = datetime.now(tz=IST)
    print(f"[{now.strftime('%Y-%m-%d %H:%M IST')}] Morning news synthesis starting...")

    watchlist = load_watchlist()
    if not watchlist:
        print("ERROR: Watchlist is empty. Exiting.")
        sys.exit(1)

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
