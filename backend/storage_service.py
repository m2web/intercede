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


def list_records() -> list[dict]:
    """
    Lists all recorded prayer JSON files in the data directory,
    sorted by newest first.
    """
    if not os.path.exists(DATA_DIR):
        return []

    records = []
    for entry in os.scandir(DATA_DIR):
        if entry.is_file() and entry.name.startswith("prayers_") and entry.name.endswith(".json"):
            stat = entry.stat()
            record_info = {
                "filename": entry.name,
                "size_bytes": stat.st_size,
                "modified_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            }
            try:
                with open(entry.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    record_info["batch_id"] = data.get("batch_id")
                    record_info["rendered_at"] = data.get("rendered_at")
                    record_info["prayers_count"] = data.get("prayers_count", len(data.get("prayers", [])))
                    record_info["model"] = data.get("model")
            except Exception:
                pass
            records.append(record_info)

    records.sort(key=lambda r: r.get("rendered_at") or r["filename"], reverse=True)
    return records


def get_record(filename: str) -> dict | None:
    """
    Retrieves the content of a single recorded JSON file safely.
    """
    clean_name = os.path.basename(filename)
    if not clean_name.startswith("prayers_") or not clean_name.endswith(".json"):
        return None

    file_path = os.path.join(DATA_DIR, clean_name)
    if not os.path.isfile(file_path):
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.exception("Failed to read JSON record %s: %s", file_path, e)
        return None


def get_record_path(filename: str) -> str | None:
    """
    Returns the absolute path of a recorded JSON file if it exists and is safe.
    """
    clean_name = os.path.basename(filename)
    if not clean_name.startswith("prayers_") or not clean_name.endswith(".json"):
        return None
    file_path = os.path.join(DATA_DIR, clean_name)
    if os.path.isfile(file_path):
        return file_path
    return None


def create_zip_archive() -> bytes:
    """
    Packs all prayer JSON records into an in-memory zip archive.
    """
    import io
    import zipfile

    if not os.path.exists(DATA_DIR):
        return b""

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for entry in os.scandir(DATA_DIR):
            if entry.is_file() and entry.name.startswith("prayers_") and entry.name.endswith(".json"):
                zip_file.write(entry.path, arcname=entry.name)
    buf.seek(0)
    return buf.getvalue()

