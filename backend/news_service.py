"""
news_service.py — Fetch the top 3 headlines from Google News RSS.

Uses a browser-like User-Agent to avoid being blocked by Google on
data-center IPs (e.g. Render, AWS).  Falls back to urllib if feedparser's
built-in HTTP client is rejected.
"""

import logging
import urllib.request
import feedparser

logger = logging.getLogger(__name__)

GOOGLE_NEWS_RSS = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/135.0.0.0 Safari/537.36"
)


def _parse_entries(feed, count: int) -> list[dict]:
    """Extract headline dicts from a parsed feed."""
    headlines = []
    for entry in feed.entries[:count]:
        headlines.append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "source": entry.get("source", {}).get("title", "Google News"),
            "published": entry.get("published", ""),
        })
    return headlines


def fetch_top_headlines(count: int = 3) -> list[dict]:
    """Parse Google News Top Stories RSS and return the top `count` items."""

    # Attempt 1 — feedparser with a browser User-Agent
    feed = feedparser.parse(GOOGLE_NEWS_RSS, agent=_USER_AGENT)
    status = feed.get("status", None)
    logger.info("feedparser attempt: status=%s, entries=%d", status, len(feed.entries))

    if feed.entries:
        return _parse_entries(feed, count)

    # Attempt 2 — manual urllib fetch (different TLS fingerprint / headers)
    logger.warning("feedparser returned 0 entries (status %s). Trying urllib fallback.", status)
    try:
        req = urllib.request.Request(GOOGLE_NEWS_RSS, headers={"User-Agent": _USER_AGENT})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            logger.info("urllib fallback: HTTP %s, %d bytes", resp.status, len(data))
            feed = feedparser.parse(data)
            if feed.entries:
                return _parse_entries(feed, count)
    except Exception:
        logger.exception("urllib fallback also failed")

    logger.error("All attempts to fetch Google News RSS returned 0 entries.")
    return []
