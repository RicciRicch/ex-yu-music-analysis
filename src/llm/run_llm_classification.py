"""
src/llm/run_llm_classification.py

Klasifikuje ceo corpus_analysis_ready.csv preko LLM-a (tema/emocija/
vrednosti). Nastavljiva skripta - pamti šta je već obrađeno u izlaznom
fajlu, pa se bezbedno može prekinuti i pokrenuti ponovo (bitno zbog
dnevnog limita besplatnog Gemini nivoa, ~1500 zahteva/dan).

Pokretanje (iz root foldera projekta):
    python src/llm/run_llm_classification.py
"""

import os
import sys
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
import anthropic
from tqdm import tqdm

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config.config import LLM_MODEL, PROCESSED_DATA_DIR, REPORTS_DIR, GOLD_STANDARD_DIR
from src.llm.classify import classify_song

INPUT_PATH = GOLD_STANDARD_DIR / "gold_standard_sample.csv"
OUTPUT_PATH = REPORTS_DIR / "llm_classifications.csv"

DELAY_SECONDS = 1.0

# Za probu pre punog pokretanja - promeni na None kad budeš spremna za sve
TEST_LIMIT = None

def load_already_done() -> set:
    """Učitava song_id vrednosti koje su već USPEŠNO obrađene - greške se
    NE računaju kao gotove, da bi se automatski pokušale ponovo."""
    if not OUTPUT_PATH.exists():
        return set()
    existing = pd.read_csv(OUTPUT_PATH)
    successful = existing[existing["error"].fillna("") == ""]
    return set(successful["song_id"])


def main():
    load_dotenv()
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    df = pd.read_csv(INPUT_PATH)
    print(f"Učitano {len(df)} pesama ukupno")

    if TEST_LIMIT:
        df = df.head(TEST_LIMIT).copy()
        print(f"PROBNI REŽIM: obrađujem samo prvih {TEST_LIMIT} pesama")

    already_done = load_already_done()
    if already_done:
        print(f"Već obrađeno u prethodnom pokretanju: {len(already_done)} pesama - preskačem ih")

    todo = df[~df["song_id"].isin(already_done)]
    print(f"Preostalo za obradu: {len(todo)} pesama")

    if len(todo) == 0:
        print("Sve je već obrađeno.")
        return

    results = []
    errors = 0

    try:
        for _, row in tqdm(todo.iterrows(), total=len(todo), desc="LLM klasifikacija"):
            result = classify_song(client, LLM_MODEL, row["lyrics_clean"])

            record = {
                "song_id": row["song_id"],
                "artist": row["artist"],
                "title": row["title"],
                "period": row["period"],
                "genre": row["genre"],
                "llm_theme": result.get("theme", ""),
                "llm_emotion": result.get("emotion", ""),
                "llm_values": result.get("values", ""),
                "error": result.get("error", ""),
            }
            results.append(record)
            if result.get("error"):
                errors += 1

            time.sleep(DELAY_SECONDS)

    except KeyboardInterrupt:
        print("\n\nPrekinuto ručno (Ctrl+C) - čuvam ono što je urađeno do sad...")

    finally:
        if results:
            new_df = pd.DataFrame(results)
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            if OUTPUT_PATH.exists():
                new_df.to_csv(OUTPUT_PATH, mode="a", header=False, index=False, encoding="utf-8")
            else:
                new_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
            print(f"\nSačuvano {len(results)} novih klasifikacija u: {OUTPUT_PATH}")
            print(f"Grešaka: {errors}/{len(results)}")


if __name__ == "__main__":
    main()