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
Be concise. Each prayer object should be brief and focused.

For EACH headline, produce a JSON object with exactly these keys:
  "headline"   — the original headline text (unchanged)
  "esv_verse"  — the ESV verse text only, no reference (e.g. "The Lord is near to the brokenhearted...")
  "esv_ref"    — the scripture reference only (e.g. "Psalm 34:18")
  "reflection" — 1-2 sentences on God's sovereign hand over this event; theologically grounded,
                 not platitudinous
  "prayer"     — 3-4 sentence intercessory prayer. Begin with a varied Reformed address
                 (e.g. "Sovereign Lord...", "Gracious Father...", "God of all comfort..."),
                 then specific petitions for those affected, closing with a brief doxology
                 (e.g. "...to the praise of Your glorious grace.")
  "amen"       — a closing phrase ending with 'Amen.' Vary the address naturally,
                 e.g. 'In Jesus name, Amen.', 'In Jesus, Amen.', 'In Christ, Amen.',
                 'In the name of Christ our Lord, Amen.' Always end with 'Amen.'

Tone: reverent, Reformed, theologically precise.
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
        temperature=0.6,
        max_completion_tokens=4096,
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
