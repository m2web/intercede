"""
storage_service.py — Automatically records generated prayers to timestamped JSON files.
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
    Records a batch of generated prayers into a dedicated JSON file named
    with the date and time down to the millisecond:
    backend/data/prayers_YYYY-MM-DD_HH-MM-SS-mmm.json
    """
    if not prayers:
        return {}

    os.makedirs(DATA_DIR, exist_ok=True)

    now = datetime.now(timezone.utc)
    # Date down to millisecond (e.g. 2026-08-19_18-18-01-123)
    ms = now.microsecond // 1000
    timestamp_str = f"{now.strftime('%Y-%m-%d_%H-%M-%S')}-{ms:03d}"
    batch_id = f"batch_{now.strftime('%Y%m%d_%H%M%S')}_{ms:03d}"
    rendered_at = now.isoformat()

    # Assign IDs and format prayers
    enhanced_prayers = []
    for i, p in enumerate(prayers):
        prayer_copy = dict(p)
        if "id" not in prayer_copy:
            prayer_copy["id"] = f"prayer_{now.strftime('%Y%m%d%H%M%S')}_{ms:03d}_{i + 1}"
        enhanced_prayers.append(prayer_copy)

    batch_record = {
        "batch_id": batch_id,
        "rendered_at": rendered_at,
        "timestamp": timestamp_str,
        "model": model,
        "prayers_count": len(enhanced_prayers),
        "prayers": enhanced_prayers,
    }

    filename = f"prayers_{timestamp_str}.json"
    file_path = os.path.join(DATA_DIR, filename)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(batch_record, f, indent=2, ensure_ascii=False)

        logger.info("Successfully recorded %d prayers to %s", len(enhanced_prayers), file_path)

    except Exception as e:
        logger.exception("Failed to write prayers to JSON file %s: %s", file_path, e)

    return batch_record
