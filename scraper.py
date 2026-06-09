import re
import feedparser
from datetime import datetime, timezone, timedelta
from typing import List, Dict

IST = timezone(timedelta(hours=5, minutes=30))

FEEDS = [
    {"source": "Moneycontrol", "url": "https://www.moneycontrol.com/rss/latestnews.xml"},
    {"source": "Moneycontrol Markets", "url": "https://www.moneycontrol.com/rss/marketreports.xml"},
    {"source": "Economic Times", "url": "https://economictimes.indiatimes.com/markets/rss.cms"},
    {"source": "ET Economy", "url": "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms"},
]


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def fetch_news(hours_back: int = 20) -> List[Dict]:
    cutoff = datetime.now(tz=IST) - timedelta(hours=hours_back)
    articles = []
    seen = set()

    for feed_cfg in FEEDS:
        try:
            feed = feedparser.parse(feed_cfg["url"])
            for entry in feed.entries[:40]:
                title = entry.get("title", "").strip()
                if not title or title in seen:
                    continue
                seen.add(title)

                pub_date = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    try:
                        pub_date = datetime(
                            *entry.published_parsed[:6], tzinfo=timezone.utc
                        ).astimezone(IST)
                        if pub_date < cutoff:
                            continue
                    except Exception:
                        pass

                summary = _strip_html(
                    entry.get("summary", entry.get("description", ""))
                )[:400]

                articles.append({
                    "source": feed_cfg["source"],
                    "title": title,
                    "summary": summary,
                    "link": entry.get("link", ""),
                    "published": (
                        pub_date.strftime("%d %b, %I:%M %p IST")
                        if pub_date else "Recent"
                    ),
                })
        except Exception as e:
            print(f"  Warning: Could not fetch {feed_cfg['url']}: {e}")

    print(f"  Scraped {len(articles)} unique articles")
    return articles
