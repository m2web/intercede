"""
news_service.py — Fetch the top 3 headlines from Google News RSS.
"""

import feedparser

GOOGLE_NEWS_RSS = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"


def fetch_top_headlines(count: int = 3) -> list[dict]:
    """Parse Google News Top Stories RSS and return the top `count` items."""
    feed = feedparser.parse(GOOGLE_NEWS_RSS)

    headlines = []
    for entry in feed.entries[:count]:
        headlines.append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "source": entry.get("source", {}).get("title", "Google News"),
            "published": entry.get("published", ""),
        })

    return headlines
