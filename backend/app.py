"""
app.py — FastAPI backend for Intercede.
Fetches top news headlines and generates Reformed Christian intercessory prayers.
"""

import logging
import os
import time

from fastapi import FastAPI, HTTPException, Header, Query, Response, Security
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

import news_service
import prayer_service
import storage_service

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Admin secret key for private admin endpoints (optional in development, recommended in production)
ADMIN_KEY = os.getenv("ADMIN_KEY", "")


def _verify_admin_access(key: str | None, x_admin_key: str | None):
    expected_key = os.getenv("ADMIN_KEY", "").strip()
    if expected_key:
        provided = (key or x_admin_key or "").strip()
        if provided != expected_key:
            raise HTTPException(status_code=403, detail="Forbidden: Invalid admin credentials.")

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

        # Automatically record generated prayers to daily JSON file on disk
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


@app.get("/api/records", include_in_schema=False)
def get_recorded_batches(
    key: str | None = Query(None),
    x_admin_key: str | None = Header(None),
):
    """
    Private endpoint: List all recorded prayer JSON batches stored on the server.
    """
    _verify_admin_access(key, x_admin_key)
    records = storage_service.list_records()
    return {
        "count": len(records),
        "records": records,
    }


@app.get("/api/records/export.zip", include_in_schema=False)
def export_all_records_zip(
    key: str | None = Query(None),
    x_admin_key: str | None = Header(None),
):
    """
    Private endpoint: Download all recorded prayer JSON files as a single ZIP archive.
    """
    _verify_admin_access(key, x_admin_key)
    zip_bytes = storage_service.create_zip_archive()
    if not zip_bytes:
        raise HTTPException(status_code=404, detail="No recorded prayer files found to export.")

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=intercede_prayers_export.zip"
        },
    )


@app.get("/api/records/{filename}", include_in_schema=False)
def get_single_record(
    filename: str,
    download: bool = False,
    key: str | None = Query(None),
    x_admin_key: str | None = Header(None),
):
    """
    Private endpoint: View or download a specific recorded JSON file by its filename.
    """
    _verify_admin_access(key, x_admin_key)
    record_path = storage_service.get_record_path(filename)
    if not record_path:
        raise HTTPException(status_code=404, detail=f"Record file '{filename}' not found.")

    if download:
        return FileResponse(
            record_path,
            media_type="application/json",
            filename=os.path.basename(record_path),
        )

    data = storage_service.get_record(filename)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Could not read record file '{filename}'.")
    return data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
