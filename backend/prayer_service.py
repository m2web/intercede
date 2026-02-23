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

SYSTEM_PROMPT = """You are a Reformed Christian minister helping God's people intercede for the world.
Your task: take news headlines and craft sincere, substantive, pastorally warm intercessory prayers
in the Reformed tradition — affirming God's sovereign ordination of all things while earnestly
petitioning Him on behalf of those affected by these events.

For EACH headline, produce a JSON object with exactly these keys:
  "headline"   — the original headline text (unchanged)
  "esv_verse"  — a single relevant ESV Bible verse formatted as: "Verse text." — Book Chapter:Verse
  "reflection" — 2–3 sentences acknowledging God's sovereign hand over this event and its
                 human/spiritual significance; theologically grounded, not platitudinous
  "prayer"     — a paragraph of earnest intercessory prayer. It MUST begin with the exact phrase
                 "Lord, you ordain all things for your glory..." then transition into specific,
                 heartfelt petitions for those affected, and close with a brief doxological phrase
                 (e.g., "...to the praise of Your glorious grace. Amen.")

Tone: reverent, Reformed, theologically precise yet pastorally warm.
Do NOT use clichés or vague spirituality. Ground prayers in Scripture and Reformed soteriology.

Return ONLY a valid JSON object with a single key "prayers" whose value is an array of the objects above.
No markdown fences, no additional commentary — pure JSON only."""


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
        max_tokens=2500,
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
