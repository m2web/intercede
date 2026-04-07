"""
app.py — FastAPI backend for Intercede.
Fetches top news headlines and generates Reformed Christian intercessory prayers.
"""

import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

import news_service
import prayer_service

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    Returns a list of objects each containing:
      title, link, source, published, esv_verse, reflection, prayer
    """
    try:
        headlines = news_service.fetch_top_headlines(count=3)
        if not headlines:
            logger.error("news_service returned 0 headlines — returning 503")
            raise HTTPException(status_code=503, detail="Could not fetch news headlines.")
        logger.info("Fetched %d headlines, generating prayers…", len(headlines))
        prayers = prayer_service.generate_prayers(headlines)
        return {"prayers": prayers}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unhandled error in get_prayers")
        raise HTTPException(status_code=500, detail=f"Error generating prayers: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
