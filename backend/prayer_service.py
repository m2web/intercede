"""
prayer_service.py — Use OpenAI to reason over news headlines and generate
Reformed Christian intercessory prayers with ESV scripture.
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = """Reformed minister. Per headline, return JSON:
- "headline": unchanged
- "esv_verse": "Text." — Book Ch:V
- "reflection": 2–3 sentences; God's sovereignty over the event; theologically grounded
- "prayer": begins "Lord, you ordain all things for your glory...", specific petitions, doxology close

Tone: Reformed, reverent, precise, warm. No clichés. Root in Scripture and Reformed soteriology.
Output ONLY {"prayers": [...]}. No markdown."""


def generate_prayers(headlines: list[dict]) -> list[dict]:
    """
    Given a list of headline dicts, call OpenAI and return a list of prayer objects.
    Each result merges original headline metadata (link, source, published) with
    the AI-generated fields (esv_verse, reflection, prayer).
    """
    headline_list = "\n".join(
        f"{i + 1}. {h['title']}" for i, h in enumerate(headlines)
    )
    user_message = (
        f"Please write intercessory prayers for these {len(headlines)} news headlines:\n\n"
        f"{headline_list}"
    )

    response = _client.chat.completions.create(
        model=_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.75,
        max_tokens=8192,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    parsed = json.loads(content)

    # Model returns {"prayers": [...]} per our system prompt
    if isinstance(parsed, list):
        prayers = parsed
    else:
        prayers = parsed.get("prayers") or next(
            (v for v in parsed.values() if isinstance(v, list)), []
        )

    # Merge AI output with original headline metadata
    results = []
    for i, prayer_obj in enumerate(prayers):
        meta = headlines[i] if i < len(headlines) else {}
        results.append({**meta, **prayer_obj})

    return results
