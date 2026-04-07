"""
news_service.py — Fetch the top headlines from reliable RSS feeds.

Google News blocks requests from data-center IPs, so we use a cascade
of alternative feeds (AP News, BBC, NPR) and keep Google News as a
last-resort fallback.
"""

import logging
import urllib.request
import feedparser

logger = logging.getLogger(__name__)

# Ordered by preference — feeds most likely to work from data-center IPs first.
_RSS_FEEDS = [
    ("BBC News", "https://feeds.bbci.co.uk/news/rss.xml"),
    ("NPR News", "https://feeds.npr.org/1001/rss.xml"),
    ("Google News", "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"),
]

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/135.0.0.0 Safari/537.36"
)


def _parse_entries(feed, source_label: str, count: int) -> list[dict]:
    """Extract headline dicts from a parsed feed."""
    headlines = []
    for entry in feed.entries[:count]:
        # Some feeds put the source in different places
        source = source_label
        if hasattr(entry, "source") and isinstance(entry.get("source"), dict):
            source = entry["source"].get("title", source_label)

        headlines.append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "source": source,
            "published": entry.get("published", ""),
        })
    return headlines


def _try_feed(url: str, label: str, count: int) -> list[dict]:
    """Try fetching a single RSS feed, return headlines or empty list."""

    # Attempt 1 — feedparser with browser User-Agent
    try:
        feed = feedparser.parse(url, agent=_USER_AGENT)
        status = feed.get("status", None)
        logger.info("[%s] feedparser: status=%s, entries=%d", label, status, len(feed.entries))
        if feed.entries:
            return _parse_entries(feed, label, count)
    except Exception:
        logger.exception("[%s] feedparser failed", label)

    # Attempt 2 — urllib fallback
    try:
        req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            logger.info("[%s] urllib fallback: HTTP %s, %d bytes", label, resp.status, len(data))
            feed = feedparser.parse(data)
            if feed.entries:
                return _parse_entries(feed, label, count)
    except Exception:
        logger.warning("[%s] urllib fallback failed", label)

    return []


def fetch_top_headlines(count: int = 3) -> list[dict]:
    """Try each RSS feed in order; return headlines from the first that works."""
    for label, url in _RSS_FEEDS:
        headlines = _try_feed(url, label, count)
        if headlines:
            logger.info("Using %d headlines from %s", len(headlines), label)
            return headlines

    logger.error("All %d RSS feeds failed to return headlines.", len(_RSS_FEEDS))
    return []
