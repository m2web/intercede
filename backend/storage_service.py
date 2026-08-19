"""
storage_service.py — Automatically records generated prayers to daily JSON files.
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Base data directory: backend/data
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.getenv("INTERCEDE_DATA_DIR", os.path.join(_BASE_DIR, "data"))


def record_prayers(prayers: list[dict], model: str = "gpt-5-mini") -> dict:
    """
    Records a batch of generated prayers into a daily JSON file:
    backend/data/prayers_YYYY-MM-DD.json

    If the file exists, appends the new batch to the day's batches array.
    """
    if not prayers:
        return {}

    os.makedirs(DATA_DIR, exist_ok=True)

    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    batch_id = f"batch_{now.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    rendered_at = now.isoformat()

    # Assign IDs and format prayers
    enhanced_prayers = []
    for i, p in enumerate(prayers):
        prayer_copy = dict(p)
        if "id" not in prayer_copy:
            prayer_copy["id"] = f"prayer_{now.strftime('%Y%m%d%H%M%S')}_{i + 1}"
        enhanced_prayers.append(prayer_copy)

    batch_record = {
        "batch_id": batch_id,
        "rendered_at": rendered_at,
        "date": date_str,
        "model": model,
        "prayers_count": len(enhanced_prayers),
        "prayers": enhanced_prayers,
    }

    file_path = os.path.join(DATA_DIR, f"prayers_{date_str}.json")

    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except Exception:
                    data = {}

            if isinstance(data, dict) and "batches" in data and isinstance(data["batches"], list):
                data["batches"].append(batch_record)
            elif isinstance(data, dict) and "batch_id" in data:
                # Convert previous single-batch format to list of batches
                data = {
                    "date": date_str,
                    "batches": [data, batch_record],
                }
            elif isinstance(data, list):
                data.append(batch_record)
            else:
                data = {
                    "date": date_str,
                    "batches": [batch_record],
                }
        else:
            data = {
                "date": date_str,
                "batches": [batch_record],
            }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info("Successfully recorded %d prayers to %s (Batch: %s)", len(enhanced_prayers), file_path, batch_id)

    except Exception as e:
        logger.exception("Failed to write prayers to JSON file: %s", e)

    return batch_record


def get_daily_prayers(date_str: str | None = None) -> dict:
    """
    Reads the JSON file for a specific date (defaults to today).
    """
    if not date_str:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    file_path = os.path.join(DATA_DIR, f"prayers_{date_str}.json")
    if not os.path.exists(file_path):
        return {"date": date_str, "batches": []}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.exception("Failed to read JSON file %s: %s", file_path, e)
        return {"date": date_str, "batches": [], "error": str(e)}
