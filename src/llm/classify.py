"""
src/llm/classify.py

Poziva LLM (Gemini) za klasifikaciju jedne pesme, parsira JSON odgovor.
"""

import json
import re

from src.llm.prompts import build_prompt


def _extract_json(text: str):
    """Pokušava da izvuče JSON objekat iz odgovora modela - modeli ponekad
    dodaju objašnjenje ili markdown code-fence oko JSON-a uprkos
    instrukciji da to ne rade, pa tražimo prvi { ... } blok umesto da se
    oslanjamo na to da je CEO odgovor čist JSON."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def classify_song(client, model: str, lyrics: str) -> dict:
    """Vraća dict sa 'theme'/'emotion'/'values', ili dict sa 'error'
    ključem ako poziv ili parsiranje ne uspe."""
    prompt = build_prompt(lyrics)
    try:
        response = client.messages.create(
            model=model,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text
    except Exception as e:
        return {"error": str(e)}

    result = _extract_json(text)
    if result is None:
        return {"error": "JSON parsing failed", "raw_response": text[:200]}
    return result