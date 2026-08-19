"""
app.py — FastAPI backend for Intercede.
Fetches top news headlines and generates Reformed Christian intercessory prayers.
"""

import logging
import os
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

import news_service
import prayer_service
import storage_service

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── In-memory prayer cache (30-minute TTL) ─────────────────
CACHE_TTL_SECONDS = 30 * 60  # 30 minutes
_prayer_cache: dict | None = None
_cache_timestamp: float = 0.0

app = FastAPI(
    title="Intercede API",
    description="Generates Reformed Christian intercessory prayers from today's top news headlines.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://intercede-frontend.onrender.com",  # Render frontend
        "https://intercede-now.org",                # Custom domain
        "https://www.intercede-now.org",            # Custom domain (www)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    status: str
    message: str


@app.get("/api/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", message="Intercede API is running")


@app.get("/api/prayers")
def get_prayers():
    """
    Fetch top 3 news headlines and generate an intercessory prayer for each.

    Returns cached data if available and less than 30 minutes old.
    Otherwise fetches fresh headlines, generates prayers via the LLM,
    caches the result, and returns it.

    Returns a list of objects each containing:
      title, link, source, published, esv_verse, reflection, prayer
    """
    global _prayer_cache, _cache_timestamp

    # Serve from cache if still fresh
    age = time.time() - _cache_timestamp
    if _prayer_cache is not None and age < CACHE_TTL_SECONDS:
        remaining = int(CACHE_TTL_SECONDS - age)
        logger.info("Serving cached prayers (%d s remaining)", remaining)
        return _prayer_cache

    # Cache miss or expired — fetch fresh data
    try:
        headlines = news_service.fetch_top_headlines(count=3)
        if not headlines:
            logger.error("news_service returned 0 headlines — returning 503")
            raise HTTPException(status_code=503, detail="Could not fetch news headlines.")
        logger.info("Fetched %d headlines, generating prayers…", len(headlines))
        prayers = prayer_service.generate_prayers(headlines)

        # Automatically record generated prayers to daily JSON file
        batch = storage_service.record_prayers(prayers, model=prayer_service.get_model())
        recorded_prayers = batch.get("prayers", prayers)
        response = {"prayers": recorded_prayers}

        # Store in cache
        _prayer_cache = response
        _cache_timestamp = time.time()
        logger.info("Prayers cached for %d seconds", CACHE_TTL_SECONDS)

        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unhandled error in get_prayers")
        raise HTTPException(status_code=500, detail=f"Error generating prayers: {str(e)}")


@app.get("/api/prayers/daily")
def get_daily_prayers_endpoint(date: str | None = None):
    """
    Retrieve recorded prayer batches for a given date (YYYY-MM-DD).
    Defaults to today if no date is provided.
    """
    return storage_service.get_daily_prayers(date)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
