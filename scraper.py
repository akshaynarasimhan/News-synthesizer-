import re
import feedparser
from datetime import datetime, timezone, timedelta
from typing import List, Dict
from urllib.parse import quote_plus

IST = timezone(timedelta(hours=5, minutes=30))

FEEDS = [
    {"source": "Moneycontrol", "url": "https://www.moneycontrol.com/rss/latestnews.xml"},
    {"source": "Moneycontrol Markets", "url": "https://www.moneycontrol.com/rss/marketreports.xml"},
    {"source": "Economic Times", "url": "https://economictimes.indiatimes.com/markets/rss.cms"},
    {"source": "ET Economy", "url": "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms"},
]

_GNEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def _parse_entry(entry, feed_source: str, cutoff, seen: set) -> Dict | None:
    title = entry.get("title", "").strip()
    if not title or title in seen:
        return None
    seen.add(title)

    pub_date = None
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            pub_date = datetime(
                *entry.published_parsed[:6], tzinfo=timezone.utc
            ).astimezone(IST)
            if pub_date < cutoff:
                return None
        except Exception:
            pass

    summary = _strip_html(
        entry.get("summary", entry.get("description", ""))
    )[:400]

    return {
        "source": feed_source,
        "title": title,
        "summary": summary,
        "link": entry.get("link", ""),
        "published": pub_date.strftime("%d %b, %I:%M %p IST") if pub_date else "Recent",
    }


def fetch_news(hours_back: int = 24) -> List[Dict]:
    cutoff = datetime.now(tz=IST) - timedelta(hours=hours_back)
    articles = []
    seen: set = set()

    for feed_cfg in FEEDS:
        try:
            feed = feedparser.parse(feed_cfg["url"])
            for entry in feed.entries[:40]:
                article = _parse_entry(entry, feed_cfg["source"], cutoff, seen)
                if article:
                    articles.append(article)
        except Exception as e:
            print(f"  Warning: Could not fetch {feed_cfg['url']}: {e}")

    print(f"  Scraped {len(articles)} unique macro articles")
    return articles


def fetch_company_news(stocks: List[Dict], hours_back: int = 24) -> List[Dict]:
    cutoff = datetime.now(tz=IST) - timedelta(hours=hours_back)
    articles = []
    seen: set = set()

    for stock in stocks:
        symbol = stock["symbol"]
        name = stock.get("name", symbol)
        query = quote_plus(f'"{name}" OR "{symbol}" NSE stock India')
        url = _GNEWS_RSS.format(query=query)
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                article = _parse_entry(entry, f"[{symbol}] Google News", cutoff, seen)
                if article:
                    article["company"] = symbol
                    articles.append(article)
        except Exception as e:
            print(f"  Warning: Could not fetch news for {symbol}: {e}")

    print(f"  Scraped {len(articles)} company-specific articles")
    return articles
